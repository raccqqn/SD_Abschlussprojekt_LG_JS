from beamBuilder2D import BeamBuilder2D
from bodyBuilder3D import BodyBuilder3D
from solver_global import Solver
import matplotlib.pyplot as plt

def build_beam():

    length = 200
    width = 50
    k = 1

    bld = BeamBuilder2D(length,width,k)
    bld.create_geometry()

    #bld.apply_force((100,0), [0, -35])

    for x in range(95,105):                              #Kraft wirkt verteilt über festgelegte Länge, bessere Ergebnisse
        bld.apply_force((x,0), [0,-1])

    bld.fix_node((0,width-1), [1,1])
    bld.fix_node((length-1,width-1), [1,1])
    beam = bld.build()

    K, F = beam.assemble()

    slv = Solver(K, F, beam.fixed_dofs())
    solution = slv.solve()

    scale = 0.1                                         #Skalierung, sonst sieht man nichts
    u_nodes = solution.reshape(-1, 2)                   #Lösung in richtiges Format fürs Plotting kriegen

    for node_id, data in beam.graph.nodes(data=True):
        node = data["node_ref"]
        x, y = node.pos
        ux, uy = u_nodes[node_id]

        plt.plot(x, y, "ko")                           #ursprüngliche Lage
        plt.plot(x + scale*ux, y + scale*uy, "ro")     #verformte Lage

    plt.gca().set_aspect("equal")
    plt.show()

def build_body():
    length = 40
    width = 10
    depth = 10
    k = 1
    F = -5

    bld = BodyBuilder3D(length,width,depth,k)
    bld.create_geometry()

    for y in range(width):
        for x in range(5):
            bld.apply_force((17 + x, 0, y), [0,F, 0])
    
    for y in range(depth):
        bld.fix_node((0, width-1, y), [1,1,1])
        bld.fix_node((length-1, width-1, y), [1,1,1])

    body = bld.build()

    K, F = body.assemble()

    slv = Solver(K, F, body.fixed_dofs())
    solution = slv.solve()

    u_nodes = solution.reshape(-1, 3)       #Für Plot reshapen
    scale = 0.1 

    #3D-Plot
    fig = plt.figure()
    ax = plt.axes(projection="3d")

    for node_id, data in body.graph.nodes(data=True):
        node = data["node_ref"]
        x,y,z = node.pos
        ux,uy,uz = u_nodes[node_id]

        plt.plot(x, y, z, "ko")                                      #ursprüngliche Lage
        plt.plot(x + scale*ux, y + scale*uy, z + scale*uz, "ro")     #verformte Lage
    
    plt.gca().set_aspect("equal")
    plt.show()




if __name__ == "__main__":
    build_body()



