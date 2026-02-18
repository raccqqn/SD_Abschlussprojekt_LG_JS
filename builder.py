from abc import ABC, abstractmethod
import numpy as np
from structure import Structure
from node import Node

class Builder(ABC):
    """
    Abstrakte Basisklasse für die Erstellung von 2D- und 3D-Stabstrukturen.

    - Legt Geometrie fest (Knoten und Elementverbindungen)
    - Weißt Kräfte an gewünschte Knoten zu
    - Setzt Randbedinungen
    - Erzeugt anschließend ein Structure-Objekt
    """

    def __init__(self, dim: int, EA: float):
        self.dim = dim                  #Dimension kann festgelegt werden, so auch Bauen einer 3D-Struktur möglich
        self.nodes_data = {}            #Dictionary für die Struktur-Daten, {(x,y): {"cords", "force", "fixed"}}
        self.elements = []              #Liste von (pos_i, pos_j)

        self.EA = EA

    @abstractmethod
    def create_geometry(self):
        pass

    def apply_force(self, pos, val):    #Kraft wird an gewählte Nodes zugewiesen
        self.nodes_data[pos]["force"] = np.array(val) 
 
    def fix_node(self, pos, mask):      #Fixierung ausgewählter Nodes, mask legt Richtung fest 
        self.nodes_data[pos]["fixed"] = np.array(mask, dtype=bool)

    def build(self):
        structure = Structure(self.dim)

        node_objects = {}               #Temporäreres Speichern der erstellten Nodes für Erstellung der Springs
        node_id = 0

        #Nodes aus gespeicherten Daten erzeugen
        for pos, data in self.nodes_data.items():
            node = Node(node_id, data["cords"])
            structure.add_node(node, data["force"], data["fixed"])
            node_objects[pos] = node
            node_id += 1
        
        #Springs aus gespeicherten Daten erzeugen
        for pos_i, pos_j in self.elements:
            
            #Federsteifigkeiten berechnen
            xi = self.nodes_data[pos_i]["cords"]        #Positionen aus Dictionary abgreifen
            xj = self.nodes_data[pos_j]["cords"]

            L = np.linalg.norm(xj-xi)                   #Abstand berechnen
            k = self.EA/L

            structure.add_spring(node_objects[pos_i], node_objects[pos_j], k)

        structure.assign_dofs()                         #Freiheitsgrade zuweisen
        return structure