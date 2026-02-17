from beamBuilder2D import BeamBuilder2D
from bodyBuilder3D import BodyBuilder3D
from solver_global import Solver
from optimizerSimp import OptimizerSIMP
import matplotlib.pyplot as plt

def build_beam():

    length = 50
    width = 10
    k = 1

    bld = BeamBuilder2D(length,width,k)
    bld.create_geometry()

    bld.apply_force((25,0), [0, -2])

#    for x in range(23,27):                              #Kraft wirkt verteilt über festgelegte Länge, bessere Ergebnisse
#        bld.apply_force((x,0), [0,-5])

#    for y in range(width):
#        bld.fix_node((0,y), [1,1])
#        bld.fix_node((length-1,y), [0,1])

    bld.fix_node((0,width-1), [0,1])
    bld.fix_node((length-1,width-1), [1,1])
    
    beam = bld.build()
    beam.assemble()

    opt = OptimizerSIMP(beam)
    opt_beam = opt.optimize(0.2, 50)

    plot_structure(opt_beam)

    scale = 0.1                                         #Skalierung, sonst sieht man nichts

"""     for _, data in opt_beam.graph.nodes(data=True):
        node = data["node_ref"]
        x, y = node.pos

        ux, uy = u[node.dof_indices]

        plt.plot(x, y, "ko")                           #ursprüngliche Lage
        #plt.plot(x + scale*ux, y + scale*uy, "ro")     #verformte Lage

    plt.gca().set_aspect("equal")
    plt.show() """

import matplotlib.pyplot as plt

def plot_structure(structure, title="Optimierte Struktur", show_nodes=False):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 1. Edges (Stäbe) zeichnen
    for i, j, data in structure.graph.edges(data=True):
        
        spring = data["spring"]
        x_val = spring.x
        
        # Filter: Sehr dünne Stäbe fast unsichtbar machen
        if x_val < 0.01:
            continue
            
        pos_i = spring.i.pos
        pos_j = spring.j.pos

        # Farbe basierend auf Dichte (von Hellgrau zu Schwarz)
        color = plt.cm.Greys(x_val) 

        ax.plot(
            [pos_i[0], pos_j[0]],
            [pos_i[1], pos_j[1]],
            color=color,
            linewidth=5 * x_val,      # Maximale Dicke skalieren
            alpha=max(0.1, x_val),    # Mindest-Sichtbarkeit
            solid_capstyle='round',   # Schöne abgerundete Ecken
            zorder=1
        )

    # 2. Knoten zeichnen (optional)
    if show_nodes:
        nodes_x = [d["pos"][0] for n, d in structure.graph.nodes(data=True)]
        nodes_y = [d["pos"][1] for n, d in structure.graph.nodes(data=True)]
        ax.scatter(nodes_x, nodes_y, s=10, color='red', zorder=2, alpha=0.5)

    # 3. Lager und Lasten (Bonus)
    # Hier könntest du Symbole für fixierte Knoten einbauen

    ax.set_aspect("equal")
    ax.set_title(title)
    ax.axis('off') # Koordinatenachsen oft störend bei Strukturen
    ax.invert_yaxis()
    plt.tight_layout()
    plt.show()

def build_body():
    length = 200
    width = 10
    depth = 10
    k = 1
    F = -5

    bld = BodyBuilder3D(length,width,depth,k)
    bld.create_geometry()

    for y in range(width):
        for x in range(5):
            bld.apply_force((10 + x, 0, y), [0,F,0])
    
    for y in range(depth):
        bld.fix_node((0, 0, y), [1,1,1])
        bld.fix_node((length-1, 0, y), [1,1,1])

    body = bld.build()
    body.assemble()

    opt = Optimizer(body)
    
    opt_body, u = opt.optimize(1500)

#    u_nodes = solution.reshape(-1, 3)       #Für Plot reshapen
    scale = 0.1 

    #3D-Plot
    fig = plt.figure()
    ax = plt.axes(projection="3d")

    for _, data in opt_body.graph.nodes(data=True):
        node = data["node_ref"]
        x,y,z = node.pos
        #ux,uy,uz = [node.dof_indices]

        plt.plot(x, y, z, "ko")                                      #ursprüngliche Lage
        #plt.plot(x + scale*ux, y + scale*uy, z + scale*uz, "ro")     #verformte Lage
    
    plt.gca().set_aspect("equal")
    plt.show()




if __name__ == "__main__":
    build_beam()



