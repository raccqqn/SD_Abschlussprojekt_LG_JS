import networkx as nx
import numpy as np

from node import Node
from spring import Spring

class Structure:

    def __init__(self, EA: float, dim: int):
        self.EA = EA
        self.dim = dim                          # Dimension übergeben
        self.graph = nx.Graph()                 # Dimensionslosen Graph erstellen
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

    def has_force(self, node_id):
        node = self.graph.nodes[node_id]["node_ref"]
        return not np.allclose(node.F, 0)                                       #True, wenn Kraft nicht nahe an 0 ist 
    
    def is_mechanically_stable(self, node_id) -> bool:

        #Fixierte Knoten sind immer stabil
        if self.is_fixed(node_id):
            return True

        neighbors = list(self.graph.neighbors(node_id))

        #Zu wenige Verbindungen -> instabil
        if len(neighbors) < self.dim:
            return False

        node = self.graph.nodes[node_id]["node_ref"]
        x0, y0 = node.pos[0], node.pos[1]

        directions = []

        for n_id in neighbors:
            neighbor = self.graph.nodes[n_id]["node_ref"]
            dx = neighbor.pos[0] - x0
            dy = neighbor.pos[1] - y0

            length = np.hypot(dx, dy)
            if length == 0:
                continue

            directions.append([dx / length, dy / length])

        if len(directions) < self.dim:
            return False

        directions = np.array(directions)

        #Rang bestimmen
        rank = np.linalg.matrix_rank(directions)

        return rank >= self.dim
    

    #Statisch, da Funktion unabhängig von self funktionieren soll aber rein logisch hier hin gehört
    @staticmethod
    def build_from_data(data, EA, dim):
        """Erzeugt eine Structure-Instanz aus gespeicherten Rohdaten"""

        #Neue Instanz erstellen
        struct = Structure(EA, dim)
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

        return struct
    
    def update_force(self):
        pass

    def update_fixings(self):
        pass        