import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

from builder import Builder
from bodyBuilder3D import BodyBuilder3D
from beamBuilder2D import BeamBuilder2D

st.set_page_config(page_title="Visualisierung der Balken")

START = {
    "length": 4,                                     #Speichern als DICT
    "width": 2,
    "depth": 1,
    "EA": 1000.0,
    "force" : 10.0,
    "f_start" : 1,  
    "f_flaeche" : 1
}

for k,v in START.items():
    if k not in st.session_state:
        st.session_state[k] = v

def input_geometry():                                                           #Eingaben der Geometrie
    laenge = st.number_input("Länge", min_value = 1, value = 2)
    breite = st.number_input("Breite", min_value = 3, value = 4)
    tiefe = st.number_input("Tiefe", min_value = 1, value = 2)
    ea = st.number_input("Steifigkeit", min_value = 1.0, value = 1000.0)
    kraft = st.number_input("Kraftstärke", min_value = 10, value = 10)
    Fx = st.number_input("Kraftangriffspunkt Beginn", min_value = 0, max_value = st.session_state["length"]-1, value = START["f_start"])
    Fx_end = st.number_input("Kraftangriffsbereich", min_value = 1, max_value = st.session_state["width"], value = breite-1)

    return laenge, breite, tiefe, ea, kraft, Fx, Fx_end

def init_session_states(laenge, breite, tiefe, ea, kraft, Fx, Fx_end):                              #Eingabe in SessionStates speichern
    st.session_state["length"] = laenge                                         #Speichern als DICT
    st.session_state["width"] = breite
    st.session_state["depth"] = tiefe
    st.session_state["EA"] = ea
    st.session_state["force"] = kraft
    st.session_state["f_start"] = Fx
    st.session_state["f_flaeche"] = Fx_end

def geometry_beam():                                                           #Objekt gleich in 3D bauen
    bld = BeamBuilder2D(st.session_state["length"], st.session_state["width"], st.session_state["EA"])
    bld.create_geometry()

    bld.fix_node((0, st.session_state["width"]-1), [0,1])                                   #Fixierte Knoten immer fix gesetzt
    bld.fix_node((st.session_state["length"]-1, st.session_state["width"]-1), [1, 1])

    fx = st.session_state["f_start"]
    fx_end = st.session_state["f_flaeche"]

    for x in range(fx, fx + fx_end):  #Aufgebrachte Kraft
        bld.apply_force((x, 0), [0, st.session_state["force"]])

    beam = bld.build()
    beam.assemble()

    return bld, beam

def plot_beam(beam):
    fig, ax = plt.subplots()

    for _,_, edata in beam.graph.edges(data = True):
        spring = edata["spring"]
        xi, yi = spring.i.pos
        xj, yj = spring.j.pos

        ax.plot([xi, xj], [yi, yj], "k-", linewidth = 1)
    
    for _, ndata in beam.graph.nodes(data = True):
        node = ndata["node_ref"]
        x,y = node.pos
        ax.plot(x,y, "ko", markersize = 3)
    
    ax.set_aspect("equal")
    ax.invert_yaxis()

    st.pyplot(fig)




laenge, breite, tiefe, ea, kraft, Fx, Fx_end = input_geometry()
init_session_states(laenge, breite, tiefe, ea, kraft, Fx, Fx_end)
bld, beam = geometry_beam()
plot_beam(beam)

st.write(st.session_state)