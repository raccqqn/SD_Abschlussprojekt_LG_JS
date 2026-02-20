import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

from builder import Builder
from bodyBuilder3D import BodyBuilder3D
from beamBuilder2D import BeamBuilder2D
from solver_global import Solver
from structure import Structure
from optimizerESO import OptimizerESO
from optimizerSimp import OptimizerSIMP

st.set_page_config(page_title="Visualisierung der Balken")
st.header("Maße des Balkens")
st.subheader("Erste Eingaben")

if "active_optimizer" not in st.session_state:
    st.session_state["active_optimizer"] = None

if "current_page" not in st.session_state:
    st.session_state["current_page"] = None

if "values_changed" not in st.session_state:
    st.session_state["values_changed"] = False



























START = {
    "f_start" : 1,  
    "f_area" : 1,
}


for k,v in START.items():
    if k not in st.session_state:
        st.session_state[k] = v

def set_optimizer(name):
    st.session_state["active_optimizer"] = name

def ui_geometry():
    c1, c2, c3, c4 = st.columns(4)
    with c1: laenge = st.number_input("Länge", min_value = 2, value = 9, width=150)
    with c2: breite = st.number_input("Breite", min_value = 3, value = 4, width=150)
    with c3: tiefe = st.number_input("Tiefe", min_value = 1, value = 1, width=150)
    with c4: ea = st.number_input("Steifigkeit", min_value = 1.0, value = 1000.0)
    
    return laenge, breite, tiefe, ea

def ui_force(laenge):
    c1, c2, c3 = st.columns(3)
    with c1: kraft = st.number_input("Kraftstärke", min_value = 10, value = 10)
    with c2: F_start = st.number_input("Angriffspunkt", min_value = 0, max_value = laenge-1, key="f_start")
    with c3: F_start_area = st.number_input("Linienkraft?", min_value = 1, max_value = laenge-F_start, key = "f_area")
    
    return kraft, F_start, F_start_area

def ui_festlager():
    off = st.toggle("Festlager vordefinieren?")
    if off:
        pass # In zukunft festlager an den Ecken definieren, ansonsten frei wählbar

def ui_optimizer():
    st.subheader("Chooses your Optimierer")
    c1, c2 = st.columns(2)
    with c1: 
        if st.button("ESO"):
            set_optimizer("ESO")
    with c2: 
        if st.button("SIMP"):
            set_optimizer("SIMP")
    
    st.write("Aktivierter Optimierer:", st.session_state["active_optimizer"])


def input_values():
    laenge, breite, tiefe, ea = ui_geometry()
    kraft, F_start, F_start_area = ui_force(laenge)
    ui_festlager()
    ui_optimizer()

    params = dict(length=laenge, width=breite, depth = tiefe, EA = ea, force = kraft)
    return params

def active_ESO(object, VolumenFrac, Aggressivity):
    opt = OptimizerESO(object)
    opt_object = opt.optimize(VolumenFrac, Aggressivity)
    for state in opt_object:
        print(state)
    opt_object = opt.structure















































def geometry_beam(params):                                                                    #Zuerst mal Balken Bauen in 2D
    bld = BeamBuilder2D(params["length"], params["width"], params["EA"])
    bld.create_geometry()

    bld.fix_node((0, params["width"]-1), [0,1])                               #Freiheitsgrad in y-richtung eingeschränkt
    bld.fix_node((params["length"]-1, params["width"]-1), [1, 1])   #Freiheitsgrad in x+y-Richtung eingeschränkt

    F_start = st.session_state["f_start"]                                            
    F_start_area = st.session_state["f_area"]

    for x in range(F_start, F_start + F_start_area):                                     #Angriffsbereich der Kraft. 
        bld.apply_force((x, 0), [0, params["force"]])

    beam = bld.build()                                                          #Tatsächliches BAUEN des Balkens
    beam.assemble()                                                             #Zusammenfügen zu einer Struktur

    return beam

def plot_beam(beam):                        
    fig, ax = plt.subplots()                                

    for _,_, edge in beam.graph.edges(data = True):             #Federninfo aus Kanten abrufen
        spring = edge["spring"]
        xi, yi = spring.i.pos                                   #Ausgangspositionen auslesen
        xj, yj = spring.j.pos
        ax.plot([xi, xj], [yi, yj], "b-", linewidth = 1)        #Plotten der Feder als einzelne Linien
    
    for _, node in beam.graph.nodes(data = True):               #Massenpunkte abrufen, speichern und plotten
        mass = node["node_ref"]
        x,y = mass.pos
        ax.plot(x,y, "bo", markersize = 1)
    
    ax.set_aspect("equal")              
    ax.invert_yaxis()
    st.pyplot(fig)

def plot_beam_deformed(structure, u, scale=0.2, show_nodes=True):
    fig, ax = plt.subplots()

    for _, _, edge in structure.graph.edges(data=True):
        spring = edge["spring"]
        xi, yi = spring.i.pos
        xj, yj = spring.j.pos
        ax.plot([xi, xj], [yi, yj], color="0.7", linewidth=1, zorder=1)       #Normale Darstellung Balken

    for _, _, edge in structure.graph.edges(data=True):
        spring = edge["spring"]
        xi, yi = spring.i.pos
        xj, yj = spring.j.pos
        ui = u[spring.i.dof_indices]                                #Verschiebungen
        uj = u[spring.j.dof_indices]
        ax.plot([xi + scale*ui[0], xj + scale*uj[0]],               #verschobene Darstellung
                [yi + scale*ui[1], yj + scale*uj[1]], color="b", linewidth=1, zorder=2)

    if show_nodes:                                                              #Massenpunkte
        for _, ndata in structure.graph.nodes(data=True):
            node = ndata["node_ref"]
            x, y = node.pos
            ux, uy = u[node.dof_indices] 
            ax.plot(x, y, "o", markersize=1, color="0.7", zorder=1)             #Normale Darstellung
            ax.plot(x + scale*ux, y + scale*uy, "bo", markersize=1, zorder=2)   #Verschobener Plot

    ax.set_aspect("equal")
    ax.invert_yaxis()
    st.pyplot(fig)

def geometry_body():                                                             #3D Körper bauen und darstellen      
    bld = BodyBuilder3D(params["length"], params["width"], params["depth"], params["EA"])
    bld.create_geometry()

    for z in range(params["depth"]):                                   #Freiheitsgrade definieren
        bld.fix_node((0, 0, z), [0,1,0])                                        #Freiheitsgrad in y-richtung eingeschränkt
        bld.fix_node((params["length"]-1, 0, z), [1, 1,1])                     #Freiheitsgrad in x+y+z-Richtung eingeschränkt
    
    for z in range(params["depth"]):
        F_start = st.session_state["f_start"]                                            
        F_start_area = st.session_state["f_area"]
        F = params["force"]
        for x in range(F_start, F_start + F_start_area):                                     #Angriffsbereich der Kraft. 
            bld.apply_force((x, 0, z), [F,0,0])

    body = bld.build()                                                          #Tatsächliches BAUEN des Balkens
    body.assemble()                                                             #Form: ((xi,yi,zi) (xj,yj,zj))

    return body

def plot_body(body):                        
    fig = plt.figure()
    ax = fig.add_subplot(111, projection = "3d") #3D Plot generieren                                
    for _,_, edge in body.graph.edges(data = True):             #Federninfo aus Kanten abrufen
        spring = edge["spring"]
        xi, yi, zi = spring.i.pos                                   #Ausgangspositionen auslesen
        xj, yj, zj = spring.j.pos
        ax.plot([xi, xj], [yi, yj], [zi, zj], "b-", linewidth = 1)        #Plotten der Feder als einzelne Linien

    for _, nodes in body.graph.nodes(data = True):               #Massenpunkte abrufen, speichern und plotten
        mass = nodes["node_ref"]
        x,y,z = mass.pos
        ax.scatter(x,y,z, color="b")

    ax.set_aspect("equal")
    st.pyplot(fig)

def plot_body_deformed(structure, u, scale=0.2, show_nodes=True):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    for _, _, edge in structure.graph.edges(data=True):
        spring = edge["spring"]
        xi, yi, zi = spring.i.pos
        xj, yj, zj = spring.j.pos
        ax.plot([xi, xj], [yi, yj], [zi, zj], color="0.7", linewidth=1, zorder=1)       #Normale Darstellung Balken

    for _, _, edge in structure.graph.edges(data=True):
        spring = edge["spring"]
        xi, yi, zi = spring.i.pos
        xj, yj, zj = spring.j.pos
        ui = u[spring.i.dof_indices]                                #Verschiebungen
        uj = u[spring.j.dof_indices]
        ax.plot([xi + scale*ui[0], xj + scale*uj[0]],                #verschobene Darstellung
                [yi + scale*ui[1], yj + scale*uj[1]],
                [zi + scale*ui[2], zj + scale*uj[2]], color="b", linewidth=1, zorder=2)

    if show_nodes:                                                              #Massenpunkte
        for _, ndata in structure.graph.nodes(data=True):
            node = ndata["node_ref"]
            x, y, z = node.pos
            ux, uy, uz = u[node.dof_indices] 
            ax.scatter(x,y,z)             #Normale Darstellung
            ax.scatter(x + scale*ux, y + scale*uy, z+scale*uz)   #Verschobener Plot

    ax.set_aspect("equal")
    ax.invert_yaxis()
    st.pyplot(fig)

params = input_values()
scale = st.slider("Skalierung", 0.0, 5.0, 0.2, 0.05)

if params["depth"] < 2:
    beam = geometry_beam(params)
    plot_beam(beam)
    solver = Solver(beam)
    u = solver.solve()
    plot_beam_deformed(beam, u, scale=scale, show_nodes=False)
    st.write(st.session_state)
    
else:
    body = geometry_body()
    plot_body(body)
    solver3d = Solver(body)
    u1 = solver3d.solve()
    plot_body_deformed(body, u1, scale = scale, show_nodes=True)
