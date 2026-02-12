import numpy as np
from node import Node
from structure import Structure
from builder import Builder

class BeamBuilder2D(Builder):
    def __init__(self, length, width, EA):
        super().__init__(dim=2)                             #Dimension hier immer 2
        super().__init__(EA=EA)
        
        self.length = length
        self.width = width                             


    def create_geometry(self):

        for y in range(self.width):
            for x in range(self.length):

                pos = (x,y)

                self.nodes_data[(x,y)] = {                  #Node-Daten für gewünschte Struktur speichern
                    "cords": np.array([x,y], dtype=float),
                    "force": np.zeros(self.dim),
                    "fixed": np.zeros(self.dim, dtype=bool)
                    }
                
                if x > 0:                                   #Verbindung bereits möglich?
                    self.elements.append((x-1, y), pos)     #Positionen für Späteres Verbinden speichern
                
                if y > 0:
                    self.elements.append((x, y-1), pos)
    
