import numpy as np
from structure import Structure

class Solver(): 
    """
    Solverklasse. Nimmt globale Steifigkeit, globale Kraft und fixed Matrix entgegen. Berechnet die Verschiebung aus F = k * u
    """
    def __init__(self, structure: Structure):
        self.eps = 1e-9                                                     #Regularisierung zum Vermeiden einer Singulären Matrix
        self.K = np.array(structure.K_global, dtype = float)                              
        self.F = np.array(structure.F_global, dtype = float).reshape(-1)    # Sicherstellen, dass 1D Vektor ist                             
        self.fix = np.array(structure.fixed_dofs(), dtype = bool)           # Logische Maske: Bei FIX = True
        self.free = ~self.fix                                               # Logische Maske: Bei FREE = True 

        assert self.K.shape[0] == self.K.shape[1], "Stiffness matrix K must be square."               # Aus Muster-Solver importiert
        assert self.K.shape[0] == self.F.shape[0], "Force vector F must have the same size as K."
    
    def reduced_system(self):
        K_ff = self.K[self.free][:,self.free]  # K, F bei freien dofs
        F_f = self.F[self.free]
        return K_ff, F_f

    def solve(self):                           # Globaler Verschiebungsvektor 
        K_ff, F_f = self.reduced_system()                      
        u = np.zeros_like(self.F)              # Vektor mit gleicher Länge wie Kraftvektor - gefüllt mit Nullen

        try:
            u_f = np.linalg.solve(K_ff, F_f)       # Gleichung lösen für freie dofs
        #Nach Beispiel-Solver: Bei Singularität mit kleiner Regularisierung versuchen
        except np.linalg.LinAlgError:               
            K_ff += np.eye(K_ff.shape[0]) * self.eps
            u_f = np.linalg.solve(K_ff, F_f)

        u[self.free] = u_f                     # Lösung an den Positionen einetzen
        return u
    
    def reaktionsgleichung(self):
        u = self.solve()
        R = self.K @ u - self.F
        return R   