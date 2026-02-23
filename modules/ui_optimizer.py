import streamlit as st
from solver_global import Solver
from optimizerSimp import OptimizerSIMP
from optimizerESO import OptimizerESO
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from plots import Plotter
from solver_global import Solver
import numpy as np
import cProfile

def opt_eso(structure, target_vol, agg):
    opt = OptimizerESO(structure)
    opt_structure = opt.optimize(target_vol, agg)

    for state in opt_structure:
        print(state)
    
    opt_structure = opt.structure
    return opt_structure

def opt_SIMP(structure, target_vol, MaxIter, Filter ):
    opt = OptimizerSIMP(structure)
    opt_structure = opt.optimize(target_vol, MaxIter, Filter)
    
    for state in opt_structure:
        print(state)
    
    opt_structure = opt.structure
    return opt_structure

def plot_opt(opt_structure):
    sol = Solver(opt_structure)
    u = sol.solve()
    plotter = Plotter()
    plotter.plot_optimization_result(opt_structure, u)

