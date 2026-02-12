import numpy as np
from node import Node
from structure import Structure
from builder import Builder

class BodyBuilder3D(Builder):
    def __init__(self, length, width, depth, EA):
        super().__init__(dim=3, EA=EA)                             #Dimension hier immer 3
        
        self.length = length
        self.width = width 
        self.depth = depth    

        self._elements = set()          #Menge, die doppelte Einträge verhindert

    def _add(self, a, b):
        if a == b:                      #Keine Feder zwischen identische Knoten
            return
        c = tuple(sorted((a,b)))        #Verbindungen einheitlich sortieren und wieder als tuple speichern 
        self._elements.add(c)           #Tuple zur Menge hinzufügen

    def create_geometry(self):
        self.nodes_data = {}
        self._elements = set()

        for z in range(self.depth):
            for y in range(self.width):
                for x in range(self.length):
                    pos = (x,y,z)

                    self.nodes_data[pos] = {                  #Node-Daten für gewünschte Struktur speichern
                        "cords": np.array(pos, dtype=float),
                        "force": np.zeros(self.dim),
                        "fixed": np.zeros(self.dim, dtype=bool)
                        }
                    
                    if x > 0:                                   
                        self._add((x-1, y, z), pos)             #Horizontale Feder

                    if y > 0:                                   #Vertikale Feder
                        self._add((x, y-1, z), pos)

                    if z > 0:                                   #Feder in z-Richtung
                        self._add((x, y, z-1), pos)

                    if x > 0 and y > 0:                         #Flächendiagonalen in x/y Ebene
                        self._add((x-1, y-1, z), pos)
                        self._add((x-1, y, z), (x, y-1, z))  
                    
                    if y > 0 and z > 0:                         #Flächendiagonalen in y/z Ebene
                        self._add((x, y-1, z-1), pos)
                        self._add((x, y-1, z), (x, y, z-1))

                    if x > 0 and z > 0:                         #Flächendiagonalen in x/z Ebene
                        self._add((x-1, y, z-1), pos)
                        self._add((x-1, y, z),(x, y, z-1))

                    if x > 0 and y > 0 and z > 0:               #Raumdiagonale
                        self._add((x-1, y-1, z-1), pos)
        
        self.elements = list(self._elements)                    #Menge in Liste umwandeln