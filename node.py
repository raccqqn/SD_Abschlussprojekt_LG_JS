import networkx as nx
import numpy as np

class Node:
    """
    Basisklasse. Node beschreibt einen Punkt im Raum mit möglichen Bewegungen. Randbedinungen, Freiheitsgrade und Belastungen können hier festgelegt werden.
    """
    def __init__(self, id, pos):
        self.id = id
        self.pos = np.array(pos, dtype=float)

        self.F = np.zeros_like(pos, dtype=float)            #zeros_like: Matrix in gleicher Form, mit 0 füllen
        self.fixed = np.zeros_like(pos, dtype=bool)         #Node in x, y oder z Richtung fixiert?

        self.u_indices = None                               #Zuweisung der zugehörigen Verschiebungen

    def set_force(self, vals):
        self.F[:] = vals
    
    def fix(self, is_fixed=None):                           #Wird is_fixed nicht übergeben: Knoten fixiert
        if is_fixed == None:                                #Wenn schon, kann festgelegt werden, welche Richtung fixiert ist
            self.fixed[:] = True
        else:
            self.fixed[:] = is_fixed