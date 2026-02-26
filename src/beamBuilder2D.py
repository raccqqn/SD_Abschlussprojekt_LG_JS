import numpy as np
from src.builder import Builder

class BeamBuilder2D(Builder):
    def __init__(self, length, width, EA):
        super().__init__(l=length, w=width, d=1, dim=2, EA=EA)                             #Dimension hier immer 2
                            

    def create_geometry(self):

        for y in range(self.w):
            for x in range(self.l):

                pos = (x,y)

                self.nodes_data[pos] = {                  #Node-Daten für gewünschte Struktur speichern
                    "cords": np.array([x,y], dtype=float),
                    "force": np.zeros(self.dim),
                    "fixed": np.zeros(self.dim, dtype=bool)
                    }
                
                if x > 0:                                   #Verbindung bereits möglich?
                    self.elements.append(((x-1, y), pos))   #Positionen für Späteres Verbinden speichern

                if y > 0:
                    self.elements.append(((x, y-1), pos))

                if x > 0 and y > 0:                         #Diagonale zur Aussteifung (beide Richtungen)
                    self.elements.append(((x-1, y-1), pos))
                    self.elements.append(((x-1, y), (x, y-1)))  