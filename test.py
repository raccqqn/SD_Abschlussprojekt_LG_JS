from beamBuilder2D import BeamBuilder2D
from bodyBuilder3D import BodyBuilder3D
from solver_global import Solver
from optimizerSimp import OptimizerSIMP
from optimizerESO import OptimizerESO
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

import cProfile
from optimizerSimp import OptimizerSIMP




def build_beam():

    length = 80
    width = 20
    k = 1

    bld = BeamBuilder2D(length,width,k)
    bld.create_geometry()

#    bld.apply_force((98,102), [0, 0.1])

    for x in range(38,42):                              #Kraft wirkt verteilt über festgelegte Länge, bessere Ergebnisse
        bld.apply_force((x,0), [0,2])

#    for y in range(width):
#        bld.fix_node((0,y), [1,1])
#        bld.fix_node((length-1,y), [0,1])

    bld.fix_node((0,width-1), [0,1])
    bld.fix_node((length-1,width-1), [1,1])
    #bld.fix_node((0, 0), [0,1])
    
    beam = bld.build()
    beam.assemble()

#-------------------------------------------------------------------------------------------------------------------------------

#    opt_old = OptimizerESO(beam)
#    opt_beam = opt_old.optimize(0.6, 0.4)

#    for state in opt_beam:
#        print(state)

#    opt_beam = opt_old.structure
#-------------------------------------------------------------------------------------------------------------------------------

    profiler = cProfile.Profile()
    profiler.enable()

    opt = OptimizerSIMP(beam)
    opt_beam = opt.optimize(0.4, 20, 1.5)

    #Schrittweiße Lösen, Dic mit {iter:, x:, energies:, compliance:} wird nach jeder Iteration zurückgegeben!
    #Energien und x nicht indiziert! 
    for state in opt_beam:
        print(state)    #Hier können die Daten ausgelesen werden
    
    opt_beam = opt.structure

    profiler.disable()
    profiler.dump_stats("simp_profile.prof")
    
#--------------------------------------------------------------------------------------------------------------------------------

    sol = Solver(opt_beam)
    u = sol.solve() 
    

    plot_optimization_result(opt_beam, u)
    #plot_nodes(opt_beam, u)

def plot_nodes(opt_beam, u):
    scale = 0.1                                         #Skalierung, sonst sieht man nichts

    for _, data in opt_beam.graph.nodes(data=True):
        node = data["node_ref"]
        x, y = node.pos

        ux, uy = u[node.dof_indices]

        plt.plot(x, y, "ko")                           #ursprüngliche Lage
        #plt.plot(x + scale*ux, y + scale*uy, "ro")     #verformte Lage

    plt.gca().invert_yaxis()
    plt.gca().set_aspect("equal")
    plt.show()

def plot_optimization_result(structure, u, scale_factor=0.1):
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Alle Edges (Stäbe) durchlaufen
    for i, j, data in structure.graph.edges(data=True):
        spring = data["spring"]
        x_val = spring.x
        
        # Original-Positionen
        pos_i = np.array(spring.i.pos)
        pos_j = np.array(spring.j.pos)
        
        # Verschiebungen extrahieren (u hat das Format [u1x, u1y, u2x, u2y, ...])
        u_i = u[spring.i.dof_indices]
        u_j = u[spring.j.dof_indices]
        
        # Deformierte Positionen berechnen
        pos_i_def = pos_i + scale_factor * u_i
        pos_j_def = pos_j + scale_factor * u_j

        # 1. OPTIMIERTE STRUKTUR (Grau/Schwarz)
        if x_val > 0.01:
            ax.plot(
                [pos_i[0], pos_j[0]], [pos_i[1], pos_j[1]],
                color=plt.cm.Greys(x_val),
                linewidth=5 * x_val,
                alpha=0.3, # Etwas transparenter, damit rot besser wirkt
                zorder=1
            )
        
         # 2. VERSCHOBENE STRUKTUR (Rot)
        # Wir plotten die verschobene Struktur dünner, um die Tendenz zu zeigen
        if x_val > 0.1: # Nur relevante Stäbe verschoben zeigen
            ax.plot(
                [pos_i_def[0], pos_j_def[0]], [pos_i_def[1], pos_j_def[1]],
                color='red',
                linestyle='--',
                linewidth=1,
                alpha=0.6,
                zorder=2
            )
        
            

    ax.set_aspect("equal")
    ax.set_title(f"Optimierung & Verformung (Skalierung: {scale_factor}x)")
    ax.axis('off')
    ax.invert_yaxis()
    plt.show()



def build_body():
    length = 20
    width = 10
    depth = 5
    k = 1
    F = 3

    bld = BodyBuilder3D(length,width,depth,k)
    bld.create_geometry()

    for y in range(depth):
        for x in range(4):
            bld.apply_force((8 + x, 0, y), [0,F,0])
    
    for y in range(depth):
        bld.fix_node((0, 0, y), [0,1,0])
        bld.fix_node((length-1, 0, y), [1,1,1])

    body = bld.build()
    body.assemble()

    opt = OptimizerSIMP(body)
    
    opt_body = opt.optimize(0.4, 30, 1.5)
    
    sol = Solver(opt_body)
    u = sol.solve()
    plot_optimization_result_3d(opt_body, u)



if __name__ == "__main__":
    build_beam()



