import networkx as nx
import numpy as np

class Node:
    """
    Basisklasse. Node beschreibt einen Punkt im Raum mit möglichen Bewegungen. Randbedinungen, Freiheitsgrade und Belastungen können hier festgelegt werden.
    """
    def __init__(self, id, pos):
        self.id = id
        self.pos = np.array(pos, dtype=float)

        self.F = None                                       #Belastung und Randbedinungen werden in Struktur festgelegt, nicht an Node
        self.fixed = None                                   #Node in x, y oder z Richtung fixiert?
        self.dof_indices = None                             #Zuweisung der zugehörigen Freiheitsgrade

    def set_force(self, F):
        self.F = np.array(F, float)
    
    def fix(self, fixed=None):                           #Wird is_fixed nicht übergeben: Knoten fixiert
        if fixed is None:                                #Wenn schon, kann festgelegt werden, welche Richtung fixiert ist
            self.fixed = np.ones_like(self.pos, dtype=bool)
        else:
            self.fixed = np.array(fixed, dtype=bool)