import streamlit as st
from UI.state import init_session_states, init_remove_input_force_support, show_geometry_states
from UI.ui_parts import ui_storage_sidebar, ui_pages_sidebar
from UI.ui_geometry import ui_geometry
from UI.geometry import build_structure_from_session_states
from UI.plots import Plotter

#Speichern der Struktur zu jedem Zeitpunkt möglich
ui_storage_sidebar()
ui_pages_sidebar()

init_session_states()                               #Notwendig, damit bei einem refresh der page die Daten geladen werden


st.header("Grundmaße definieren")
st.write(f"Die gewünschten Parameter eingeben und bestätigen.")
st.write("_Sehr große Strukturen können aufgrund begrenzter Arbeitsspeicherkapazität und hoher Rechenzeit nicht mehr optimiert werden._")

plotter = Plotter()
ui_geometry()

if st.session_state["ui_input_changed"] == True:    #Bei jeder Änderung der Geometrie, werden die gespeicherten Kräfte und Lager gelöscht
    init_remove_input_force_support()
show_geometry_states()
structure = build_structure_from_session_states()   #Struktur wird gebaut, für den Plot

#Working Structure in session_state speichern
st.session_state["structure"] = structure

placeholder = st.empty()

if st.session_state["depth"] > 1:                      #Je nachdem ob 2d oder 3d werden andere Plot Verfahren genutzt
    fig = plotter.body_undeformed(structure, show_nodes=True, node_size=3, linewidth=1, display=False, )

else:
    fig = plotter.beam_undeformed(structure, show_nodes=True, node_size=3, linewidth=1, display=False, line_color="#262730")

placeholder.plotly_chart(fig, width="stretch")

st.divider()

if st.button("Weiter", width="stretch"):
    st.switch_page("pages/2_Festlager_und_Kräfte.py")