import numpy as np
import networkx as nx
from src.structure import Structure
from src.solver_global import Solver

class OptimizerESO():

    def __init__(self, structure: Structure):
        self.structure = structure
        self.inital_nodes = self.structure.graph.number_of_nodes()

        self.initial_node_ids = list(self.structure.graph.nodes())

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
            Ko = spring.K_global(use_simp = False)                                              

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
                    if self.can_remove(node_id):
                        self.structure.remove_node(node_id)
                        n_removed += 1
                        changed = True

        for _, _, data in self.structure.graph.edges(data=True):
            #Geometrie neu berechnen, da sich Knoten verändern könnten (theoretisch)
            data["spring"].update_geometry()

        #Freiheitsgrade neu zuweisen
        self.structure.assign_dofs()
        #Struktur neu aufbauen: In diesem Solver wird kein SIMP verwendet, Ko soll neu berechnet werden!                                    
        self.structure.assemble(use_simp=False) 

        #Wie viele Knoten wurden in dieser Iteration entfernt?
        return n_removed                        

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
    
    def det_batch_size(self, target, aggressivity):

        current_nodes = self.structure.graph.number_of_nodes()
        inital_nodes = self.inital_nodes

        #Maximal 2% der Nodes in einer Iteration entfernen
        max_rem_frac = 0.05

        #Fortschritt berechnen
        progress = (inital_nodes - current_nodes) / (inital_nodes - target)

        #Minimum: 20% der Maximal-Aggressivität, steigt linear mit Fortschritt an
        ramp = 0.1 + 0.95 * progress

        batch = int(max(1, max_rem_frac * current_nodes * aggressivity * ramp))

        if self.structure.dim > 2: return min(batch,5)
        return min(batch, 30)

    def optimize(self, red_fac, aggressivity):

        #Sicherstellen, dass richtiges K_Global aufgestellt wurde
        self.structure.assemble(use_simp=False)

        weight = self.structure.graph.number_of_nodes()
        target = red_fac * weight
        c = 1

        while self.structure.graph.number_of_nodes() > target:

            old_count = self.structure.graph.number_of_nodes()
            batch_size = self.det_batch_size(target, aggressivity)

            print(f"Starting {c}. Iteration...")
            print(f"Nodes left: {self.structure.graph.number_of_nodes()}")

            solver = Solver(self.structure)

            u = solver.solve()
            energy = self.calc_node_energy(u)

            n_removed = self.edit_structure(energy, batch_size)

            new_count = self.structure.graph.number_of_nodes()

            if old_count == new_count:
                print("Es konnte kein weiterer Knoten gelöscht werden, passe Aggressivität an")
                break
            
            c += 1

            #Mask, so kann für Visualisierung bestimmt werden ob Knoten noch existiert
            current_nodes = set(self.structure.graph.nodes())
            mask = np.array([node_id in current_nodes for node_id in self.initial_node_ids])

            yield {
                "iter": c,
                "node_mask": mask,
                "energies": energy,
                "remaining_nodes": new_count,
                "n_removed": n_removed,
                "vol_frac": self.structure.graph.number_of_nodes() / self.inital_nodes
            }