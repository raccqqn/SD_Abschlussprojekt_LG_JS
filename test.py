from beamBuilder2D import BeamBuilder2D
from bodyBuilder3D import BodyBuilder3D
from solver_global import Solver
from optimizerSimp import OptimizerSIMP
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

def build_beam():

    length = 40
    width = 10
    k = 1

    bld = BeamBuilder2D(length,width,k)
    bld.create_geometry()

#    bld.apply_force((98,102), [0, 0.1])

    for x in range(18,22):                              #Kraft wirkt verteilt über festgelegte Länge, bessere Ergebnisse
        bld.apply_force((x,0), [0,0.3])

#    for y in range(width):
#        bld.fix_node((0,y), [1,1])
#        bld.fix_node((length-1,y), [0,1])

    bld.fix_node((0,width-1), [0,1])
    bld.fix_node((length-1,width-1), [1,1])
    
    beam = bld.build()
    beam.assemble()

    opt = OptimizerSIMP(beam)
    opt_beam = opt.optimize(0.4, 50, 1.5)

    sol = Solver(opt_beam)
    u = sol.solve()

    plot_optimization_result(opt_beam, u)



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
    build_body()



