import numpy as np
from src.structure import Structure
from src.solver_global import Solver

class OptimizerSIMP():

    def __init__(self, structure: Structure):
        self.structure = structure

        #Edges und Springs werden in diesem Optimizer nicht verändert: Können einmal geladen werden
        self.edges = list(self.structure.graph.edges())
        self.springs = [self.structure.graph[i_id][j_id]["spring"] for i_id, j_id in self.edges]

        #Ausgangsvolumen verändert sich nicht: Einmal festlegen, in Array speichern
        self.V_vec = np.array([spring.V for spring in self.springs])
        self.V_total = np.sum(self.V_vec)
        self.L_vals = np.array([spring.L for spring in self.springs])

        #Mittelpunkte der Federn speichern. pos bleiben Konstant, kann einmal bestimmt werden
        self.centers = []                                       
        for spring in self.springs:
            xi = spring.i.pos
            xj = spring.j.pos
            #Mittelpunkt speichern
            self.centers.append(0.5*(xi + xj))

        #Als Array speichern
        self.centers = np.array(self.centers)
        #Neighbor-List wird später einmalig berechnet
        self.neighbor_list = None         

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
        sens = np.zeros(len(self.springs))                                                               

        #Über alle Springs iterieren
        for i, spring in enumerate(self.springs):
            sens[i] = - spring.pen * (spring.x ** (spring.pen - 1)) * energies[i] * 2

        return sens


    def apply_filter(self, sensits, radius):
        """
        Empfindlichkeiten werden in festgelegtem Radius gemittelt.
        """
        new_sens = np.zeros_like(sensits)
        #x-Werte in Array vorladen
        x_vals = np.array([spring.x for spring in self.springs])
        
        for i in range(len(self.edges)):
            weight_sum = 0.0

            #Index und Distanz aus vorberechneter Liste speichern
            neighbor_indices, dists = self.neighbor_list[i]

            #Skalieren, Linear mit Entfernung abnehmend
            fac = radius - dists
            
            #Multipliziert mit x: Nur relevante Elemente beeinflussen Nachbarn
            weighted_sum = np.sum(fac * x_vals[neighbor_indices] * sensits[neighbor_indices])

            weight_sum += np.sum(fac)
            
            #Neuen sens-Wert nach Gesamtsumme  normieren, Wert darf nie 0 sein.
            #Wieder durch x teilen, um Sens auf ursprüngliches Niveau zu kriegen
            new_sens[i] = weighted_sum / (max(1e-3, x_vals[i]) * weight_sum)
        
        return new_sens
    
    def det_neighbors(self, radius):
        """
        Position der Elemente bleibt während des Optimierens konstant.
        Benachbarte Knoten können einmalig berechnet und gespeichert werden.
        """
        
        neighbor_list = []
        
        for i in range (len(self.edges)):

            #Abstände aller Centers zu Center [i]
            dists = np.linalg.norm(self.centers - self.centers[i], axis=1)
            
            #Elemente innerhalb Radius auswählen
            indices = np.where(dists < radius)[0]

            #Index und Distanz speichern
            neighbor_list.append((indices, dists[indices]))
        
        self.neighbor_list = neighbor_list


    def update_x(self, sensitivities, vol_fac, move=0.3, xmin=0.001):

        #Zielvolumen berechnen
        target_volume = vol_fac * self.V_total

        #aktuelles x in Array speichern
        x_old = np.array([spring.x for spring in self.springs])

        #Aktuelle Empfindlichkeiten in Array abspeichern
        #sensits = np.array([sensitivities[edge] for edge in self.edges])
        sensits = sensitivities     

        #Lagrange-Multiplikator lam: Korrekturfaktor. Groß: Material "teurer", x sinkt | Klein: Material "günstiger", x steigt
        #Lagrange-Formel: L(x,lam) = C(x) + lam * (sum(x_i * v_i) - V_targ)
        #In Klammer: Nebenbedinung. (Summe aller Teilvolumen - Target)
        #Optimum: Ableitung von L nach jedem x gleich 0. Umstellen: (-dC/dc) / lam * V_i = 1
        #Altes x wird mit rechter Seite der Gleichung multipliziert. Größer als 1: Zunahme, Kleiner: Abnahme

        #Grenzen für Lagrange-Multiplikator, anfangs große Spanne um target_vol zu treffen
        l1 = 0.0
        l2 = 1e9

        #Aufhören, wenn Grenzen fast übereinander liegen
        while (l2 - l1) > 10e-4:
            #Mitte als Startwert
            lam = (l1 + l2  ) / 2             

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

    def optimize(self, vol_fac=0.4, max_iter=50, filter_radius = None):

        #Vernünftigeren Startwert für x festlegen
        for spring in self.springs:
            spring.x = vol_fac

        #Nachbarn vorberechnen, verkürzt Rechenzeit
        if filter_radius is not None:
            self.det_neighbors(filter_radius)

        for it in range(max_iter):

            print(f"Iteration {it}")

            #Struktur neu assemblen, neue x-Werte werden in Gesamtsteifigkeit übernommen
            self.structure.assemble()

            solver = Solver(self.structure)
            u = solver.solve()

            ee = self.structure.calc_element_energies(u)

            sens = self.compute_sensitivities(ee)

            #Optimierung kann weiterhin ohne Filter durchgeführt werden
            if filter_radius is not None:
                sens_final = self.apply_filter(sens, filter_radius)
            else:
                sens_final = sens
            
            self.update_x(sens_final, vol_fac)

            #Compliance berechnen
            compliance = solver.F.T @ u
            print(f"Compliance: {compliance}")

            #Werte pro Iteration zurückgeben

            x_vals = np.array([spring.x for spring in self.springs])
             
            yield {
                "iter": it,
                "x": x_vals,
                #"volume": np.sum(x_vals * self.L_vals),
                "frac": np.sum(x_vals * self.L_vals) / self.V_total,                                                        
                "compliance": compliance
            }

    

