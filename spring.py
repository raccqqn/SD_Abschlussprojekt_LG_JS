import numpy as np
from node import Node

class Spring:
    """
    Beschreibt ein Federelement zwischen zwei Knoten.
    Berechnet die Eigenschaften (Länge, Richtung) sowie die lokale und globale Steifigkeitsmatrix.
    """
    def __init__(self, node_i: Node, node_j: Node, k):
        self.i = node_i                     #i-Knoten
        self.j = node_j                     #j-Knoten
        self.k = k                          #Federsteifigkeit
        
    def length(self):                       #Länge ändert sich, wird hier berechnet, Abstand zurückgeben
        dis = self.j.pos - self.i.pos
        return (np.linalg.norm(dis))
    
    def direction(self):                          #Normierten Abstandsvektor für Richtung zurückgeben
        dis = self.j.pos - self.i.pos
        return (dis / self.length())
    
    def K_local(self):
        mask = np.array([[1.0, -1.0], [-1.0, 1.0]])    #Lokale Steifigkeit einer 1D-Feder
        return self.k * mask

    def proj_matrix(self):      
        dir = self.direction()
        dim = len(dir)                      #Aktuelle Dimension speichern

        #Funktion in 2D:
        #Format: (u_ix, u_iy, u_jx, u_jy). Ziel: Globale Verschiebungen in lokale Längenänderungen entlang der Feder übersetzen
        #Verschiebungen Node i auf Stabrichtung projezieren
        #Verschiebungen Node j auf Stabrichtung projezieren
        #In gegebenem solver.py 2*2 Matrix da eine Node fixiert ist

        pm = np.zeros((2, 2*dim))           #Leere Projektionsmatrix erstellen

        #Füllen, so Dimensionsunabhängig
        pm[0, 0:dim] = dir                  #Node i    
        pm[1,dim:2*dim] = dir               #Node j

        return pm
    
    def K_global(self):
        """Gibt globale Steifigkeit eines Feder-Elements zurück"""
        O = self.proj_matrix()
        K_loc = self.K_local()
        return O.T @ K_loc @ O              #O.T: In welche Richtungen wirkt die Kraft, zufolge einer Längenänderung der Feder?
                                            #O.T @ : Lokale Kräfte auf globale Freiheitsgrade projezieren
    
    