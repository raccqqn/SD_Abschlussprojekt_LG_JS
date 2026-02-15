import numpy as np
import networkx as nx
from structure import Structure
from solver_global import Solver

class Optimizer():

    def __init__(self, structure: Structure):
        self.structure = structure

    def calc_node_energy(self, u):
        
        node_ids = list(self.structure.graph.nodes())                           
        ids_to_idx = {node_id: i for i, node_id in enumerate(node_ids)}         #Node ID's nummerieren und Index in Dict speichern
        node_energies = np.zeros(len(node_ids))

        #Über alle Springs in Graph iterieren, i_id: Startpunkt, j_id: Endpunkt (Nodes)
        for i_id, j_id, data in self.structure.graph.edges(data=True):          
            spring = data["spring"]

            #Verschiebung an angehängten Nodes bestimmen
            u_nds = np.concatenate([u[spring.i.dof_indices], u[spring.j.dof_indices]]) 

            #Globale Steifigkeit der Feder abrufen
            Ko = spring.K_global()                                              

            #Verformungsenergie der Feder berechnen
            e_spring = 0.5 * u_nds.T @ Ko @ u_nds

            #Zu entsprechenden Nodes dazuaddieren
            node_energies[ids_to_idx[i_id]] += e_spring
            node_energies[ids_to_idx[j_id]] += e_spring
        
        return node_energies

    def edit_structure(self, energy, batch_size):
        
        node_ids = list(self.structure.graph.nodes())
        sorted_nodes = sorted(zip(node_ids, energy), key=lambda x: x[1])      #Node ID's nach Energie aufsteigend sortieren, verpacken
        n_removed = 0 
        

        for node_id, e in sorted_nodes:
            if n_removed >= batch_size:
                break

            if node_id not in self.structure.graph:                     #Wurde schon gelöscht? Überspringen
                continue

            if self.can_remove(node_id):                                #Überprüfen ob fixiert, kraftwirkung oder kein Lastpfad ohne Node
                self.structure.remove_node(node_id)                     #Verbundene Springs werden von NetworkX automatisch gelöscht
                n_removed += 1                                                   

        #Nach Löschen des Nodes System überprüfen: Gibt es mechanisch instabile Nodes?
        changed = True
        while changed:
            changed = False
            for node_id in list(self.structure.graph.nodes()):
                #Ist Knoten nur mit einer Feder verbunden -> Mechanisch instabil, Singularity Error
                if not self.structure.is_fixed(node_id) and \
                not self.structure.is_mechanically_stable(node_id):
                    self.structure.remove_node(node_id)
                    changed = True

        self.structure.assign_dofs()                                    #Struktur neu aufbauen!
        self.structure.assemble()

    def can_remove(self, node_id) -> bool:                              #Überprüfen, ob Node entfernt werden kann

        if self.structure.is_fixed(node_id):                            
            return False

        if self.structure.has_force(node_id):
            return False

        temp_graph = self.structure.graph.copy()                        #Struktur kopieren, Node löschen
        temp_graph.remove_node(node_id)

        if not nx.is_connected(temp_graph):                             #Besteht die Struktur noch aus einem Stück?
            return False

        return True

    def optimize(self, target):

        c = 1

        while self.structure.graph.number_of_nodes() > target:

            current_nodes = self.structure.graph.number_of_nodes()
            if current_nodes > 700:
                batch_size = 2
            else:
                batch_size = 10

            print(f"Starting {c}. Iteration...")
            print(f"Nodes left: {self.structure.ndofs/self.structure.dim}")

            solver = Solver(self.structure)

            u = solver.solve()
            energy = self.calc_node_energy(u)

            self.edit_structure(energy, batch_size)

            try:
             _ = Solver(self.structure).solve()
            except np.linalg.LinAlgError:
                print("Mechanismus erkannt nach Entfernen.")
                break
        
            c += 1
            
        return self.structure, u