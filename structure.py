import networkx as nx
import numpy as np

class Structure:

    def __init__(self, dim = 2):
        self.dim = dim                          # Dimension übergeben
        self.graph = nx.Graph()                 # Dimensionslosen Graph erstellen

    def add_node(self, id, pos, force = None, fixed = None):
        pos = np.array(pos, dtype=float)

        if force is None:                       # Standard: Kraft auf 0 und Loslager
            force = np.zeros(self.dim)
        else:
            force = np.array(force, dtype=float)

        if fixed is None:
            fixed = np.zeros(self.dim, dtype=bool)
        else:
            fixed = np.array(fixed, dtype=float)
        
        self.graph.add_node(id, pos = pos, F = force, fixed = fixed, u_indices = None) # Knoten hinzufügen und Attribute speichern

    def add_spring(self, node_i, node_j, k):
        self.graph.add_edge(node_i, node_j, k=k)            # Feder hinzufügen zwischen 2 Knoten mit Gewichtung k

    def assign_dof(self):                       # Nummerierung der Freiheitsgrade + hinzufügen zum Knoten
        for var, id in enumerate(self.graph.nodes): 
            num = var*self.dim
            self.graph.nodes[id]["u_indices"] = np.arange(num, num+self.dim)
    
    def ndofs(self): 
        return self.graph.number_of_nodes() * self.dim      # Knoten * Dimension = Anzahl möglicher Freiheitsgrade
        
    def assemble():
        None

    def fixed_dofs():
        None

    def solve():
        None