import numpy as np
import networkx as nx
from structure import Structure
from solver_global import Solver

class OptimizerSIMP():

    def __init__(self, structure: Structure):
        self.structure = structure

        #Edges und Springs werden in diesem Optimizer nicht verändert: Können einmal geladen werden
        self.edges = list(self.structure.graph.edges())
        self.springs = [self.structure.graph[i_id][j_id]["spring"] for i_id, j_id in self.edges]

        #Ausgangsvolumen verändert sich nicht: Einmal festlegen, in Array speichern
        self.V_vec = np.array([spring.V for spring in self.springs])
        self.V_total = np.sum(self.V_vec)        

    def calc_element_energies(self, u):
        
        element_energies = {}                                                   #Dict für Energien, Format: {(i_id, j_id): Energy}

        #Über alle Springs in Graph iterieren, i_id: Startpunkt, j_id: Endpunkt (Nodes)
        for i_id, j_id, data in self.structure.graph.edges(data=True):          
            spring = data["spring"]

            #Verschiebung an angehängten Nodes bestimmen
            u_nds = np.concatenate([u[spring.i.dof_indices], u[spring.j.dof_indices]]) 

            #Skalierte Globale Steifigkeit der Feder abrufen
            #Hier K_0 -> Fester Referenzwert für das Material. Potenzial des Stabes Last zu tragen, falls er voll ausgebildet wäre.
            #K_0 nutzen, da sonst "tote" Stäbe nie wiederbelebt werden könnten
            Ko = spring.get_K                                              

            #Verformungsenergie der Feder berechnen
            e_spring = 0.5 * u_nds.T @ Ko @ u_nds

            #In Dictionary speichern
            element_energies[(i_id, j_id)] = e_spring
        
        return element_energies

    def compute_sensitivities(self, energies):
        """
        Compliance-Optimierung: Compliance = Nachgiebigkeit. Ideal, da ein Wert für die Nachgiebigkeit in Lastrichtung, Steifigkeit ungeeignet
        Compliance: C = f.T * u = 2*U --> Compliance ist doppelte Verformungsenergie
        
        Verformungsenergie bereits in element_energies berechnet -> Frage: Wie ändert sich Compliance bei Faktor x? (Steigung, nach x ableiten)

        Ziel: Compliance minimieren (Steifigkeit folgend maximiert)
        SIMP-Methode: Steifigkeit K hängt von Skalierungsfaktor spring.x ab: 
        K(x) = x^p * K_0 --Ableitung--> dK(x)/dx = p * x^(p-1) * K_0

        C = f.T * u unter Verwendung der adjungierten-Methode ableiten: dC/dx = -u.T * (dK/dx) * u
        dK/dx eingesetzt: dC/dx = -p * x^(p-1) * u.T * K_0 * u || u.T * K_0 * u = element_energy * 2, wird in calc_element_energies bereits berechnet

        Adjungierten-Methode: Ohne müsste für jedes x die Sensitivität von u berechnet werden. 
        Unter Nutzung der Gleichgewichtsbedinung K * u = f als Nebenbedinung kann Term eliminiert werden. 
        Für dieses Problem ist der adjungierte Vektor identisch mit u.
        """

        #Dictionary für Speichern der Sensitivitäten der Springs
        sens = {}                                                               

        #Über alle Springs iterieren
        for (i_id, j_id), ee_val in energies.items():

            spring = self.structure.graph[i_id][j_id]["spring"]

            sens[(i_id, j_id)] = - spring.pen * (spring.x ** (spring.pen - 1)) * ee_val * 2

        return sens


    def update_x(self, sensitivities, vol_fac, move=0.2, xmin=0.001):

        #Zielvolumen berechnen
        target_volume = vol_fac * self.V_total

        #aktuelles x in Array speichern
        x_old = np.array([spring.x for spring in self.springs])

        #Aktuelle Empfindlichkeiten in Array abspeichern
        sensits = np.array([sensitivities[edge] for edge in self.edges])     

        #Lagrange-Multiplikator lam: Korrekturfaktor. Groß: Material "teurer", x sinkt | Klein: Material "günstiger", x steigt
        #Lagrange-Formel: L(x,lam) = C(x) + lam * (sum(x_i * v_i) - V_targ)
        #In Klammer: Nebenbedinung. (Summe aller Teilvolumen - Target)
        #Optimum: Ableitung von L nach jedem x gleich 0. Umstellen: (-dC/dc) / lam * V_i = 1
        #Altes x wird mit rechter Seite der Gleichung multipliziert. Größer als 1: Zunahme, Kleiner: Abnahme

        #Grenzen für Lagrange-Multiplikator, anfangs große Spanne um target_vol zu treffen
        l1 = 0.0
        l2 = 1e9

        #Aufhören, wenn Grenzen fast übereinander liegen
        while (l2 - l1) > 10e-6:
            #Mitte als Startwert
            lam = (l1 + l2) / 2             

            #neues x für alle Elemente berechnen
            x_new = x_old * np.sqrt(-sensits / (lam * self.V_vec))

            #Clipping: Wert muss in gültigem Bereich bleiben
            #Minimum: Wert darf nie 0 werden, sonst Singularitäts-Fehler!
            #Maximum: Wert darf sich nie weiter als "Schrittweite" von altem Wert entfernen, sonst sprunghafte Änderungen
            x_new = np.clip(x_new, np.maximum(xmin, x_old - move), 
                            np.minimum(1.0, x_old + move))

            #Neues Volumen berechnen, skaliert
            current_vol = np.sum(x_new * self.V_vec)

            #Neue Obergrenze/Untergrenze setzen
            if current_vol > target_volume:
                l1 = lam
            else:
                l2 = lam

        #Neue x-Werte im Spring-Object speichern
        for i, spring in enumerate(self.springs):
            spring.x = x_new[i]

    def optimize(self, vol_fac=0.4, max_iter=50):

        for it in range(max_iter):

            print(f"Iteration {it}")

            #Struktur neu assemblen, neue x-Werte werden in Gesamtsteifigkeit übernommen
            self.structure.assemble()

            solver = Solver(self.structure)
            u = solver.solve()

            ee = self.calc_element_energies(u)
            sens = self.compute_sensitivities(ee)

            self.update_x(sens, vol_fac)

            #Compliance berechnen
            compliance = solver.F.T @ u
            print(f"Compliance: {compliance}")

        return self.structure
