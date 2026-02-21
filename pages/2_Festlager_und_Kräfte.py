import streamlit as st
from modules.state import init_session_states, init_remove_input_force_support
from modules.ui_parts import ui_festlager_2d, ui_festlager_3d, ui_force_2D, ui_force_3D
from modules.geometry import build_object
from plots import Plotter
init_session_states()           #Notwendig, damit bei einem refresh der page die Daten geladen werden
plotter = Plotter()

c1, c2 = st.columns(2)
with c1: 
    if st.button("Zurück", use_container_width=True):
        st.switch_page("pages/1_Grundmaße.py")
with c2: 
    if st.button("Weiter", use_container_width=True):
        st.switch_page("pages/3_Optimierer.py")
st.divider()
st.write(st.session_state.length, st.session_state.width, st.session_state.depth, st.session_state.EA) #Zum Checken
st.title("Lager und Kraft auswählen")
st.write("Die Platzierung der Lager kann frei gewählt werden. Das System wird immer gelöst werden.")
st.divider()

if st.session_state["depth"] > 1:   #Je nach 2d oder 3d: Unterschiedliche Funktionen verwenden
    st.write("Lager definieren")
    ui_festlager_3d()
    ui_force_3D()

else:
    st.subheader("Lager definieren")
    ui_festlager_2d()
    st.divider()
    st.subheader("Kraft bestimmen")
    ui_force_2D()

structure = build_object()                      #= Structure()   
st.session_state["structure"] = structure       #Speichern für Optimierung auf nächster Seite

if st.session_state["depth"] > 1:               #Plotten der Darstellung
    plotter.body_undeformed(structure, True)

else:
    plotter.beam_undeformed(structure, True, 2,1)