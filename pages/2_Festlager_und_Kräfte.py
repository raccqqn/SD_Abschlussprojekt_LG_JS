import streamlit as st
from UI.state import init_session_states
from UI.ui_parts import ui_storage_sidebar, ui_pages_sidebar, ui_festlager_2d, ui_festlager_3d, ui_force_2D, ui_force_3D, ui_force_2d_fun, ui_force_3D_fun, ui_force_expander, ui_festlager_expander
from UI.geometry import build_structure_from_session_states
from UI.plots import Plotter

import streamlit as st

#Speichern der Struktur zu jedem Zeitpunkt möglich
ui_storage_sidebar()
ui_pages_sidebar()
init_session_states()           #Notwendig, damit bei einem refresh der page die Daten geladen werden
plotter = Plotter()


st.write(st.session_state.length, st.session_state.width, st.session_state.depth, st.session_state.EA) #Platzhalter Zum Checken 


st.header("Lager und Kraft auswählen")
st.write("Für ESO- und 3D-Analysen sollten Lagerbedinungen statisch sinnvoll definiert werden.")

tab1, tab2 = st.tabs(["**Lager**", "**Kraft**"])

#Lager werden bestimmt, je nachdem ob 2D oder 3D
with tab1:
    if st.session_state["depth"] > 1:
        ui_festlager_3d()
    else:
        ui_festlager_2d()
    
    ui_festlager_expander()

#Je nach 2d oder 3d: Unterschiedliche Funktionen verwenden
with tab2:
    if st.session_state["depth"] > 1:   
        ui_force_3D()
        st.divider()
        ui_force_3D_fun()
    else:
        ui_force_2D()
        st.divider()
        ui_force_2d_fun()
    
    ui_force_expander()
    
placeholder = st.empty()

#IMMER aktuellen Zustand anzeigen, sonst "springt" Seite bei Aktualisierung
if "cached_fig" in st.session_state and st.session_state["cached_fig"] is not None:
    placeholder.plotly_chart(st.session_state["cached_fig"], width="stretch", key="plot_static")

#Sicherstellen, dass Struktur bereits existiert
if "structure" not in st.session_state:
    st.session_state["structure"] = build_structure_from_session_states()

#"ID" der aktuellen Kräfte/Lager speichern
current_config_id = len(st.session_state.get("forces", [])) + len(st.session_state.get("supports", []))

#Überprüfen, ob alte ID bereits existiert
if "last_config_id" not in st.session_state:
    st.session_state["last_config_id"] = None

#Nur speichern, neu plotten falls sich an Konfiguration etwas geändert hat!
if current_config_id != st.session_state["last_config_id"]:

    #Structure laden
    structure = st.session_state["structure"]
    
    #Lager und Kräfte aus Session-State als Dict laden
    supports = st.session_state.get("supports", {})
    forces = st.session_state.get("forces", {})

    #Randbedinungen der Struktur aktualisieren
    structure.update_bnd_cons(supports, forces)

    #Aktuellen Zustand plotten
    if st.session_state["depth"] > 1:              
        fig = plotter.body_undeformed(structure, True, display=False)

    else:
        fig = plotter.beam_undeformed(structure, node_size=2, display=False)

    st.session_state["cached_fig"] = fig
    st.session_state["last_config_id"] = current_config_id

    #Neuen Zustand zeichnen
    placeholder.plotly_chart(fig, width="stretch", key="plot_update")

st.divider()
c1, c2 = st.columns(2)
with c1: 
    if st.button("Zurück", width="stretch", disabled=True):
        st.switch_page("pages/1_Grundmaße.py")
with c2: 
    if st.button("Weiter", width="stretch"):
        sup = st.session_state.get("supports", {})
        forc = st.session_state.get("forces", {})

        if not sup or not forc:
            st.warning("Bitte Lager und Kräfte bestimmen!")
        else:
            st.switch_page("pages/3_Optimierer.py")