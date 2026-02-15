from beamBuilder2D import BeamBuilder2D
from bodyBuilder3D import BodyBuilder3D
from solver_global import Solver
from optimizer import Optimizer
import matplotlib.pyplot as plt

def build_beam():

    length = 50
    width = 20
    k = 1

    bld = BeamBuilder2D(length,width,k)
    bld.create_geometry()

#    bld.apply_force((10,0), [0, -1.5])

    for x in range(23,27):                              #Kraft wirkt verteilt über festgelegte Länge, bessere Ergebnisse
        bld.apply_force((x,0), [0,-2])

#    for y in range(width):
#        bld.fix_node((0,y), [1,1])
#        bld.fix_node((length-1,y), [0,1])

    bld.fix_node((0,0), [0,1])
    bld.fix_node((length-1,0), [1,1])
    
    beam = bld.build()
    beam.assemble()

    opt = Optimizer(beam)
    opt_beam, u = opt.optimize(500)

    scale = 0.1                                         #Skalierung, sonst sieht man nichts

    for _, data in opt_beam.graph.nodes(data=True):
        node = data["node_ref"]
        x, y = node.pos

        ux, uy = u[node.dof_indices]

        plt.plot(x, y, "ko")                           #ursprüngliche Lage
        #plt.plot(x + scale*ux, y + scale*uy, "ro")     #verformte Lage

    plt.gca().set_aspect("equal")
    plt.show()

def build_body():
    length = 20
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



