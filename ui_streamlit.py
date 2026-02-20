import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events   

from builder import Builder
from bodyBuilder3D import BodyBuilder3D
from beamBuilder2D import BeamBuilder2D
from solver_global import Solver
from structure import Structure
from optimizerESO import OptimizerESO
from optimizerSimp import OptimizerSIMP
from plots import Plotter

plotter = Plotter(invert_y=True)

if "page" not in st.session_state:          #Erste Eingaben in den Session States
    st.session_state["page"] = 1
    st.session_state["length"] = 9
    st.session_state["width"] = 4
    st.session_state["depth"] = 1
    st.session_state["EA"] = 1000.0
    st.session_state["dimension"] = "2d"

def next_page():                            #Auf nächste Seite switchen
    st.session_state.page += 1

def previous_page():                        #Vorherige Seite
    st.session_state.page -= 1

def sync_ui_values():                       #Session_States eingaben aktualisieren: 2 unterschiedliche States, damit in der Form auch immer der aktuelle Wert geschrieben steht
    st.session_state.length = st.session_state.ui_length
    st.session_state.width = st.session_state.ui_width
    st.session_state.depth = st.session_state.ui_depth
    st.session_state.EA = st.session_state.ui_EA

def ui_geometry():                          #Eingaben in Session States speichern
    with st.form("geom_form"):
        c1, c2, c3, c4 = st.columns(4)
        with c1: laenge = st.number_input("Länge",  min_value=2,value=st.session_state.length,  key="ui_length",width=150)
        with c2: breite = st.number_input("Breite", min_value=3, value=st.session_state.width,  key="ui_width",width=150)
        with c3: tiefe = st.number_input("Tiefe", min_value=1, value=st.session_state.depth,  key="ui_depth",width=150)
        with c4: ea = st.number_input("Steifigkeit", value=st.session_state.EA, key="ui_EA", min_value=1.0)
    
        submitted = st.form_submit_button("Bestätigen" )
        if submitted:
            sync_ui_values()

def geometry_beam():                                                            #Zuerst mal Balken Bauen in 2D
    bld = BeamBuilder2D(st.session_state.length, st.session_state.width, st.session_state.EA)
    bld.create_geometry()
    beam = bld.build()                                                          
    beam.assemble()                                                             
    return beam

def geometry_body():                                                            #3D Körper bauen und darstellen      
    bld = BodyBuilder3D(st.session_state.length, st.session_state.width, st.session_state.depth, st.session_state.EA)
    bld.create_geometry()
    body = bld.build()                                                          #Tatsächliches BAUEN des Balkens
    body.assemble()                                                             #Form: ((xi,yi,zi) (xj,yj,zj))
    return body


def ui_festlager():
    if "supports" not in st.session_state:
        st.session_state["supports"]  = {}
    
    c1,c2,c3,c4 = st.columns(4)

    with c1: x = st.number_input("x", min_value = 0, max_value = st.session_state.length - 1 , value = 0, key = "x_sup")
    with c2: y = st.number_input("y", min_value = 0, max_value = st.session_state.width - 1, value = 0, key = "y_sup")
    with c3: 
        selection = st.segmented_control("Fixierte Freiheitsgrade", ["Ux", "Uy"], selection_mode="multi", key = "dofs_sup")
        mask = ["Ux" in selection, "Uy" in selection]
    
    with c4: add = st.button("Hinzufügen", key = "add_sup")
    
    if add:
        if any(mask):                                                                           #Mindestens 1 Wert muss TRUE sein
            pos = (int(x), int(y))                                                              #Knoten Koordinate
            st.session_state["supports"][pos] = {"pos" : pos, "mask" : mask}                    #Speichern im Dictionary - Überschreibt Position, falls da schon ein Wert drinnen war

    st.subheader("Aktuelle Lager")
    for i, (pos, s) in enumerate(st.session_state["supports"].items(), start=1):
        c1, c2 = st.columns([6,1])
        with c1:
            st.write(f"{pos}  {s['mask']}") 
        with c2:
            if st.button("Entfernen", key=f"sup_del_{i}"):
                del st.session_state["supports"][pos]
                st.rerun()

    if st.button("Alle löschen", key="sup_clear"):
        st.session_state["supports"] = {}
        st.rerun()



#Seiten Aufteilung___________________________________________________________________________________________________________
if st.session_state.page == 1:
    st.title("SWD Abschlussprojekt", text_alignment="center")
    st.subheader("Joachim Spitaler und Leonie Graf", text_alignment="center")
    st.button("Neue Modellierung starten", key="p1_next", on_click=next_page, use_container_width=True)
    st.button("Letzte Berechnung wiederherstellen", use_container_width=True)

elif st.session_state.page == 2:
    c1, c2 = st.columns(2)
    with c1: st.button("Zurück", key="p2_prev", on_click=previous_page, use_container_width=True)
    with c2: st.button("Weiter", key="p2_next", on_click=next_page, use_container_width=True)
    st.title("Grundmaße")
    st.subheader("Parameter eingeben und bestätigen")
    
    ui_geometry()
    st.write(st.session_state.length, st.session_state.width, st.session_state.depth, st.session_state.EA)
    
    st.divider()
    if st.session_state.depth > 1:                  #Je nachdem ob 2d oder 3d werden andere Plot verfahren genutzt
        st.session_state["dimension"] = "3d"
        body = geometry_body()
        plotter.body_undeformed(body, True)

    else:
        st.session_state["dimension"] = "2d"
        beam = geometry_beam()
        plotter.beam_undeformed(beam, True, 2, 1)

elif st.session_state.page == 3:
    c1, c2 = st.columns(2)
    with c1: st.button("Zurück", key="p3_prev", on_click=previous_page, use_container_width=True)
    with c2: st.button("Weiter", key="p3_next", on_click=next_page, use_container_width=True)
    st.title("Lager und Kraft auswählen")

    if st.session_state.dimension == "2d":
        st.write("In 2d ist es am Besten ein Festlager und ein Loslager jeweils an den Enden. ")
    else:
        st.write("In 3d Musst du soviel auswählen")

    st.write(st.session_state.length, st.session_state.width, st.session_state.depth, st.session_state.EA)
    ui_festlager()
    if st.session_state.dimension == "2d":
        beam = geometry_beam()
        plotter.beam_undeformed(beam, True, 2, 1)
    
    else:
        body = geometry_body()
        plotter.body_undeformed(body, True)

elif st.session_state.page == 4:
    st.button("Zurück", key="p4_prev", on_click=previous_page, use_container_width=True)
    st.title("Optimierer Wählen und Attribute eingeben ")
    st.write("je nach optimierer kommen 2 unterschiedliche Eingabe felder ")
    st.write(st.session_state.length, st.session_state.width, st.session_state.depth, st.session_state.EA)