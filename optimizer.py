import numpy as np
import networkx as nx
from structure import Structure
from solver_global import Solver

class Optimizer():

    def __init__(self, structure: Structure):
        self.structure = structure

    def calc_node_energy(self, u):
        
        K = self.structure.K_global
        
        node_energy = 0.5 * u * (K @ u)                                 #Elementweise Lösung ohne transponieren von u, sonst (1*1), nur ein globaler Wert!
        node_energy = node_energy.reshape(-1,self.structure.dim)
        node_energy = np.sum(node_energy, axis=1)

        return node_energy 


    def edit_structure(self, energy):
        
        node_ids = list(self.structure.graph.nodes())
        threshhold = np.percentile(energy, 0.1)                           #Untere 5% als Threshold
        remove_list = []                                                #Zu entfernende Nodes in Liste speichern, ID's durcheinander wenn zuvor gelöscht wird!

        for i, node_id in enumerate(node_ids):
            if energy[i] < threshhold and not self.structure.is_fixed(node_id):
                remove_list.append(node_id)                             #Ist Node nicht fixiert und unter Schwelle: Zu Liste hinzufügen

        for node_id in remove_list:
            if  self.can_remove(node_id):
                self.structure.remove_node(node_id)                     #Verbundene Springs werden von NetworkX automatisch gelöscht

        node_ids = list(self.structure.graph.nodes())
        for i, node_id in enumerate(node_ids):                          #Frei schwebende Knoten löschen
            if self.structure.graph.degree(node_id) == 0:
                self.structure.remove_node(node_id)

        self.structure.assign_dofs()                                    #Struktur neu aufbauen!
        self.structure.assemble()

    def can_remove(self, node_id) -> bool:                              #Überprüfen, ob Node entfernt werden kann

        struc_temp = self.structure.graph.copy()
        struc_temp.remove_node(node_id)

        for component in nx.connected_components(struc_temp):

            has_fixed_node = False

            for n in component:                                         #Enthält jede Component mindestens einen Knoten, dessen Node-Objekt fixed ist?
                if self.structure.is_fixed(n):
                    has_fixed_node = True
                    break
            
            if not has_fixed_node:
                return False

        return True

    def optimize(self, target):

        c = 1

        while self.structure.graph.number_of_nodes() > target:

            print(f"Starting {c}. Iteration...")
            print(f"Nodes left: {self.structure.ndofs/self.structure.dim}")

            solver = Solver(self.structure)

            u = solver.solve()
            energy = self.calc_node_energy(u)

            self.edit_structure(energy)
        
            c += 1
            
        return self.structure, u