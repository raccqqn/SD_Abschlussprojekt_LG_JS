import numpy as np

class Solver(): 
    """
    Solverklasse. Nimmt globale Steifigkeit, globale Kraft und fixed Matrix entgegen. Berechnet die Verschiebung aus F = k * u
    """
    def __init__(self, K_global, F_global, fixed_mask):
        self.K = np.array(K_global, dtype = float)                              
        self.F = np.array(F_global, dtype = float).reshape(-1)  # Sicherstellen, dass 1D Vektor ist                             
        self.fix = np.array(fixed_mask, dtype = bool)           # Logische Maske: Bei FIX = True
        self.free = ~self.fix                                   # Logische Maske: Bei FREE = True 

        assert self.K.shape[0] == self.K.shape[1], "Stiffness matrix K must be square."               # Aus Muster-Solver importiert
        assert self.K.shape[0] == self.F.shape[0], "Force vector F must have the same size as K."
    
    def reduced_system(self):
        K_ff = self.K[self.free][:,self.free]  # K, F bei freien dofs
        F_f = self.F[self.free]
        return K_ff, F_f

    def solve(self):                           # Globaler Verschiebungsvektor 
        K_ff, F_f = self.reduced_system()                      
        u = np.zeros_like(self.F)              # Vektor mit gleicher Länge wie Kraftvektor - gefüllt mit Nullen
        u_f = np.linalg.solve(K_ff, F_f)       # Gleichung lösen für freie dofs
        
        u[self.free] = u_f                     # Lösung an den Positionen einetzen
        return u    
    
    def reaktionsgleichung(self):
        u = self.solve()
        R = self.K @ u - self.F
        return R   