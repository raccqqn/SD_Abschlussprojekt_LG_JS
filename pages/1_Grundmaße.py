import streamlit as st
from modules.state import init_session_states, init_remove_input_force_support, init_default_session_states
from modules.ui_parts import ui_storage_sidebar, ui_geometry, ui_pages_sidebar
from modules.geometry import build_structure_from_session_states
from plots import Plotter

ui_pages_sidebar()

#Speichern der Struktur zu jedem Zeitpunkt möglich
ui_storage_sidebar()
init_session_states()                               #Notwendig, damit bei einem refresh der page die Daten geladen werden


st.header("Grundmaße definieren")
st.write(f"Die gewünschten Paramter eingeben und bestätigen. _Ein zu großes 3D Modell lässt sich nicht mehr gut lösen._")

plotter = Plotter()
ui_geometry()

if st.session_state["ui_input_changed"] == True:    #Bei jeder Änderung der Geometrie, werden die gespeicherten Kräfte und Lager gelöscht
    init_remove_input_force_support()

st.write(st.session_state.length, st.session_state.width, st.session_state.depth, st.session_state.EA)

structure = build_structure_from_session_states()                          #Struktur wird gebaut, für den Plot

#Working Structure in session_state speichern
st.session_state["structure"] = structure

placeholder = st.empty()

if st.session_state["depth"] > 1:                      #Je nachdem ob 2d oder 3d werden andere Plot Verfahren genutzt
    fig = plotter.body_undeformed(structure, True, display=False)

else:
    fig = plotter.beam_undeformed(structure, True, 3, 1, display=False)

placeholder.plotly_chart(fig, width="stretch")

st.divider()

if st.button("Weiter", width="stretch"):
    st.switch_page("pages/2_Festlager_und_Kräfte.py")