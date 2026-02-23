import streamlit as st
from solver_global import Solver
from optimizerSimp import OptimizerSIMP
from optimizerESO import OptimizerESO
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from plots import Plotter
from solver_global import Solver
import numpy as np

def plot_opt(opt_structure):
    sol = Solver(opt_structure)
    u = sol.solve()
    plotter = Plotter()
    plotter.plot_optimization_result(opt_structure, u)

