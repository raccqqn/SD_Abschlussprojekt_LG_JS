import networkx as nx
import numpy as np

from node import Node
from spring import Spring

class Structure:

    def __init__(self, dim: int):
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

    def add_spring(self, node_i: Node, node_j: Node, k):
        spring = Spring(node_i, node_j, k)                                  #Spring Instanz an Knoten i und j erstellen
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
        
    def assemble(self): # Zusammenbauen
        K = np.zeros((self.ndofs, self.ndofs))

        for _, _, data in self.graph.edges(data=True):                      #Über alle Federelemente iterieren
            spring = data["spring"]

            Ko = spring.K_global()                                          #Globale Steifigkeit berechnen

            indices = np.concatenate((                                                #Aktuelle Freiheits-Indizes abrufen 
                spring.i.dof_indices, spring.j.dof_indices
            ))

            for a in range(len(indices)):                                      #Globale Steifigkeit des jeweiligen Federelements in Steifigkeitsmatrix abspeichern
                for b in range(len(indices)):
                    K[indices[a], indices[b]] += Ko[a, b]

        self.K_global

    def fixed_dofs(self): # Randys :)
        fixed = []

        for _, data in self.graph.nodes(data=True):                             #Durch Nodes iterieren, Indizes der fixierten Nodes speichern
            node = data["note_ref"]
            for i, is_fixed in enumerate(node.fixed):
                if is_fixed:
                    fixed.append(node.u_indices[i])

        return np.array(fixed, dtype=bool)

    