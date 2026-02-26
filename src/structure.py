import networkx as nx
import numpy as np

from src.node import Node
from src.spring import Spring

class Structure:

    def __init__(self, length: int, width: int, depth: int, EA: float, dim: int):
        self.graph = nx.Graph()                 # Dimensionslosen Graph erstellen

        #Geometrie auch in Struktur speichern
        self.length = length
        self.width = width
        self.depth = depth        
        self.EA = EA
        self.dim = dim                          # Dimension übergeben
        
        self.ndofs = None                       # Gesamtanzahl Freiheitsgrade
        self.K_global = None
        self.F_global = None                    # Globaler Lastvektor

    def add_node(self, node: Node, force = None, fixed = None):
        if force is not None:                                              #Festlegen, ob Kraft auf Knoten wirkt
            node.set_force(force)
        else:
            node.set_force(np.zeros(self.dim))

        if fixed is not None:                                               #Festlegen, wo Knoten fixiert ist
            node.fix(fixed)
        else:
            node.fix(np.zeros(self.dim, dtype=bool))

        self.graph.add_node(node.id, node_ref=node)                         # Knoten hinzufügen und Attribute speichern

    def remove_node(self, node_id: Node):
        self.graph.remove_node(node_id)                                     #Verbundene Springs werden mit gelöscht!

    def find_node(self, pos):
        """
        Sucht ein Node-Objekt an einer gewünschten Koordinate, gibt Node zurück.
        Für Aktualisierung der Randbedinungen notwendig.
        """
        #Sicherstellen, dass Position als Array geladen wird
        pos_arr = np.array(pos)

        for _, data in self.graph.nodes(data=True):
            node = data["node_ref"]
            #Kleiner Toleranzbereich, keine Fehler bei inkonsequentem Typing
            if np.allclose(node.pos, pos_arr, atol=1e-5):
                return node
        #Wenn Node nicht gefunden werden kann
        return None

    def add_spring(self, node_i: Node, node_j: Node, k, x = 1.0):
        spring = Spring(node_i, node_j, k, x)                                  #Spring Instanz an Knoten i und j erstellen
        self.graph.add_edge(node_i.id, node_j.id, spring=spring)            #Feder zwischen Knoten als Edge hinzufügen, Objekt als Attribut

    def assign_dofs(self):                                                  # Nummerierung der Freiheitsgrade + hinzufügen zum Knoten
        dof_count = 0
        for _, data in self.graph.nodes(data=True):                         #id wird nicht verwendet, Zähler dafür, nicht jeder Knoten hat gleich viele Freiheitsgrade
            node = data["node_ref"]
            node.dof_indices = np.arange(dof_count, dof_count+self.dim)
            dof_count += self.dim                                           #Bei jeder Iteration Freiheitsgrade dazu addieren
        self.ndofs = dof_count

    def get_ndofs(self): 
        return self.ndofs                                                   # Anzahl möglicher Freiheitsgrade zurückgeben
        
    def assemble(self, use_simp=True): # Zusammenbauen
        self.assemble_stiffnes(use_simp)
        self.assemble_force_vector()

    def fixed_dofs(self):
        fixed_mask = np.zeros(self.ndofs, dtype = bool)                     #Logische Maske für Fixierung

        for _, data in self.graph.nodes(data=True):                         #Durch Nodes iterieren, Indizes der fixierten Nodes speichern
            node = data["node_ref"]
            for i, is_fixed in enumerate(node.fixed):
                if is_fixed:
                    fixed_mask[node.dof_indices[i]] = True

        return fixed_mask
    
    def is_fixed(self, node_id):
        node = self.graph.nodes[node_id]["node_ref"]                        #Node aus Graph bestimmen, speichern
        fixed = np.any(node.fixed)                                          #Ein Element aus Dictionary true?
        return fixed
    
    def get_supports(self):
        """Extrahiert alle Lager als Dict, so können sie in UI geladen und angezeigt werden"""
        supports = {}
        for node_id, data in self.graph.nodes(data=True):
            node = data["node_ref"]
            #Fixiert? in Dict speichern
            if np.any(node.fixed):
                #Position als Tuple als Key nutzen, so mit UI kompatibel
                #Explizit als Integer speichern, sonst label in UI!
                pos_tuple = tuple(int(round(c)) for c in node.pos)
                supports[pos_tuple] = {
                    "pos": pos_tuple,
                    "mask": node.fixed.tolist()
                }
        return supports
    
    def has_force(self, node_id):
        node = self.graph.nodes[node_id]["node_ref"]
        return not np.allclose(node.F, 0)                                       #True, wenn Kraft nicht nahe an 0 ist 

    def get_forces(self):
        """Extrahiert alle Kräfte als Dict, so können sie in UI geladen und angezeigt werden"""
        forces = {}
        for node_id, data in self.graph.nodes(data=True):
            node = data["node_ref"]
            #Kraft nicht nahe 0? in Dict speichern
            if not np.allclose(node.F, 0):
                #Position als Tuple als Key nutzen, so mit UI kompatibel
                #Explizit als Integer speichern, sonst label in UI!
                pos_tuple = tuple(int(round(c)) for c in node.pos)
                forces[pos_tuple] = {
                    "pos": pos_tuple,
                    "vec": node.F.tolist()
                }
        return forces

    def assemble_stiffnes(self, use_simp=True):
        K = np.zeros((self.ndofs, self.ndofs))

        for _, _, data in self.graph.edges(data=True):                      #Über alle Federelemente iterieren
            spring = data["spring"]

            Ko = spring.K_global(use_simp=use_simp)                         #Globale Steifigkeit berechnen - Standardmäßig nach SIMP skaliert

            indices = np.concatenate((                                      #Aktuelle Freiheits-Indizes abrufen 
                spring.i.dof_indices, spring.j.dof_indices
            ))

            #Globale Steifigkeit des jeweiligen Federelements in Steifigkeitsmatrix abspeichern
            idx = indices                           
            K[idx[:, None], idx] += Ko

            self.K_global = K

    def assemble_force_vector(self):                                            #Kraftvektor bauen
        F = np.zeros(self.ndofs)

        for _, data in self.graph.nodes(data=True):                             #Durch Nodes iterieren, wirkende Kraft zu Kraftvektor dazuaddieren
            node = data["node_ref"]
            for i, dof in enumerate(node.dof_indices):
                F[dof] += node.F[i]
        
        self.F_global = F

    def update_bnd_cons(self, supports_state, forces_state):
        """Aktualisiert Lager und Kräfte"""

        #Alle aktuellen Randbedinungen zurücksetzen, so kein Speichern alter Zustände nötig 
        for _, data in self.graph.nodes(data=True):
            node = data["node_ref"]
            #Zurücksetzen, Dimensionsunabhängig
            node.fixed = [False] * self.dim
            node.F = np.zeros(self.dim)
        
        #Lager neu setzen, an Werte aus session_state anpassen
        for pos, supports_data in supports_state.items():
            node = self.find_node(pos)
            #Kann Node gefunden werden: Mask speichern
            if node:
                #Lagerung aus Data auslesen
                mask = supports_data["mask"]
                node.fix(mask)

        for pos, force_data in forces_state.items():
            node = self.find_node(pos)
            if node:
                f_vec = force_data["vec"] 
                node.set_force(f_vec)

        self.assign_dofs()
        self.assemble()

    def is_mechanically_stable(self, node_id) -> bool:

        #Fixierte Knoten sind immer stabil
        if self.is_fixed(node_id):
            return True

        neighbors = list(self.graph.neighbors(node_id))

        #Zu wenige Verbindungen -> instabil
        if len(neighbors) < self.dim:
            return False

        node = self.graph.nodes[node_id]["node_ref"]
        pos0 = node.pos  #Dimensionsunabhängig

        directions = []

        for n_id in neighbors:
            neighbor = self.graph.nodes[n_id]["node_ref"]

            #Vektor berechnen
            diff = neighbor.pos - pos0
            length = np.linalg.norm(diff)

            #Überspringen bei numerischen Fehlern
            if length < 1e-9:
                continue

            directions.append(diff / length)

        #Weniger Elemente als Dimension: Nicht stabil
        if len(directions) < self.dim:
            return False

        directions = np.array(directions)

        #Rang bestimmen, muss abhängig von dim 2 oder 3 sein
        rank = np.linalg.matrix_rank(directions)

        return rank >= self.dim
    
    def calc_element_energies(self, u):
        """
        Berechnung der Feder-Energien zufolge einer Verformung.
        Gibt Array zurück.
        """

        springs = [self.graph[i_id][j_id]["spring"] for i_id, j_id in self.graph.edges]
        element_energies = np.zeros(len(springs))                                          

        #Über alle Springs in Graph iterieren, i_id: Startpunkt, j_id: Endpunkt (Nodes)
        for idx, spring in enumerate(springs):          

            #Verschiebung an angehängten Nodes bestimmen
            u_nds = np.concatenate([u[spring.i.dof_indices], u[spring.j.dof_indices]]) 

            #Skalierte Globale Steifigkeit der Feder abrufen
            #Hier K_0 -> Fester Referenzwert für das Material. Potenzial des Stabes Last zu tragen, falls er voll ausgebildet wäre.
            #K_0 nutzen, da sonst "tote" Stäbe nie wiederbelebt werden könnten
            Ko = spring.K_global(use_simp = False)                                              

            #Verformungsenergie der Feder berechnen
            e_spring = 0.5 * u_nds.T @ Ko @ u_nds

            #In Dictionary speichern
            element_energies[idx] = e_spring
        
        return element_energies
    
    def calc_element_forces(self, u):
        """
        Berechnet die Normalkräte in allen Federn zufolge einer Verschiebung.
        Gibt eine Liste der Kräfte in Reihenfolge der Edges zurück. 
        """
        forces = []

        for _, _, data in self.graph.edges(data=True):
            spring = data["spring"]

            #Verschiebungen und Positionen der Nodes auslesen
            u_i = u[spring.i.dof_indices]
            u_j = u[spring.j.dof_indices]
            pos_i = spring.i.pos
            pos_j = spring.j.pos
            
            #Ursprüngliche Länge
            L0 = spring.L

            #Neue Positionen, neuen Abstand, Längenänderung berechnen
            pos_i_new = pos_i + u_i
            pos_j_new = pos_j + u_j
            L_new = np.linalg.norm(pos_j_new - pos_i_new)
            delta_L = L_new - L0

            #Kraft berechnen: (delta_L * EA) / L0 = F
            F = (delta_L * self.EA) / L0
            forces.append(F)

        return forces
    
    def cleanup_simp(self, threshhold=0.05):
        """Entfernt unwichtige Federn und Knoten entsprechend der jeweiligen x-Werte"""
        
        #Als Array speichern, so können Edges später über eine Zeile entfernt werden
        edges_to_remove = []
        for i_id, j_id, data in self.graph.edges(data=True):
            if data["spring"].x < threshhold:
                edges_to_remove.append((i_id, j_id))
        #Edges entfernen 
        self.graph.remove_edges_from(edges_to_remove)

        #2. Schritt: Freie und nur an einem Element hängende Knoten entfernen
        nodes_removed_count = 0
        while True:
            nodes_to_remove = []
            for node_id, data in self.graph.nodes(data=True):
                #Keine Verbindung, nur eine Verbindung?
                if self.graph.degree(node_id) <= 1:
                    nodes_to_remove.append(node_id)
            
            #Aus Schleife raus, sobald keine Nodes entfernt werden können, so wird auch neue Struktur überprüft
            if not nodes_to_remove: break
            
            self.graph.remove_nodes_from(nodes_to_remove)
            nodes_removed_count += len(nodes_to_remove)

        #Freiheitsgrade neu zuweisen, Steifigkeit und Kraft neu aufstellen
        self.assign_dofs()
        self.assemble()

        return len(edges_to_remove), nodes_removed_count
    

    #Statisch, da Funktion unabhängig von self funktionieren soll aber rein logisch hier hin gehört
    @staticmethod
    def build_from_data(data, l, w, d, EA, dim):
        """Erzeugt eine Structure-Instanz aus gespeicherten Rohdaten"""

        #Neue Instanz erstellen
        struct = Structure(l, w, d, EA, dim)
        #Informationen über Nodes in Dict speichern
        nodes_dict = {}

        #Über Data iterieren, relevante Daten auslesen
        for i, n_id in enumerate(data["node_ids"]):
            node_id = int(n_id) 
            pos = data["pos"][i]
            
            #Node-Objekt erstellen
            node = Node(node_id, pos)
            struct.add_node(node, force=data["forces"][i], fixed=data["fixed"][i])
            
            #In Dict für anschließende Verwendung speichern
            nodes_dict[node_id] = node

        #Über Data iterieren, verbundene Knoten auslesen
        for idx, edge in enumerate(data["con_nodes"]):
            i_id, j_id = int(edge[0]), int(edge[1])
            node_i = nodes_dict[i_id]
            node_j = nodes_dict[j_id]
                
            #Steifigkeit berechnen
            L = np.linalg.norm(node_j.pos - node_i.pos)
            k = EA / L if L > 0 else 0
            x = data["x"][idx]

            struct.add_spring(node_i, node_j, k, x)

        #Freiheitsgrade zuweisen
        struct.assign_dofs()
        #Steifigkeit und Kraftvektor aufstellen
        struct.assemble()

        return struct
