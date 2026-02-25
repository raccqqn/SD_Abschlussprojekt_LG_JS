import streamlit as st
from modules.state import init_session_states, init_remove_input_force_support
from modules.ui_parts import ui_storage_sidebar, ui_geometry
from modules.geometry import build_structure_from_session_states
from plots import Plotter

#Speichern der Struktur zu jedem Zeitpunkt möglich
ui_storage_sidebar()
init_session_states()                               #Notwendig, damit bei einem refresh der page die Daten geladen werden
c1, c2 = st.columns(2)
with c1: 
    if st.button("Zurück", width="stretch"):
        st.switch_page("startseite.py")
with c2: 
    if st.button("Weiter", width="stretch"):
        st.switch_page("pages/2_Festlager_und_Kräfte.py")
st.divider()
st.header("Grundmaße definieren")
st.write("Die gewünschten Paramter eingeben und bestätigen.")

plotter = Plotter()
ui_geometry()

if st.session_state["ui_input_changed"] == True:    #Bei jeder Änderung der Geometrie, werden die gespeicherten Kräfte und Lager gelöscht
    init_remove_input_force_support()

if "geometry_loaded" not in st.session_state:
    st.session_state["geometry_loaded"] = False

st.write(st.session_state.geometry_loaded)
st.write(st.session_state.length, st.session_state.width, st.session_state.depth, st.session_state.EA)

structure = build_structure_from_session_states()                          #Struktur wird gebaut, für den Plot
#update_structure()
st.session_state["geometry_loaded"] = True                              #Status ändern
st.session_state["structure"] = structure                               #Struktur in session state speichern

#Working Structure in session_state speichern
st.session_state["structure"] = structure

placeholder = st.empty()

st.write(st.session_state.geometry_loaded)

if st.session_state["depth"] > 1:                      #Je nachdem ob 2d oder 3d werden andere Plot Verfahren genutzt
    fig = plotter.body_undeformed(structure, True, display=False)

else:
    fig = plotter.beam_undeformed(structure, True, 3, 1, display=False)

placeholder.plotly_chart(fig, width="stretch")