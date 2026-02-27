import streamlit as st
import numpy as np
from UI.state import init_session_states, show_geometry_states
from UI.ui_parts import ui_storage_sidebar, ui_pages_sidebar
from UI.ui_result import plot_optimization_results
from UI.plots import Plotter
from src.optimizerESO import OptimizerESO
from src.optimizerSimp import OptimizerSIMP

#Speichern der Struktur zu jedem Zeitpunkt möglich
ui_storage_sidebar()
ui_pages_sidebar()

init_session_states()   #Notwendig, damit bei einem refresh der page die Daten geladen werden


if "lock_optimization" not in st.session_state:
    st.session_state["lock_optimization"] = False

if "optimization_done" not in st.session_state:
    st.session_state["optimization_done"] = False

if "optimization_error" not in st.session_state:
    st.session_state["optimization_error"] = False


plotter = Plotter()

show_geometry_states()
st.header("Optimierung der Struktur")
c1,c2 = st.columns([0.3 , 0.7])
with c1: option = st.selectbox("Verfahren wählen", ("ESO", "SIMP"), disabled=st.session_state.get("lock_optimization"))
with c2: 
    final_volume = st.slider("Gewünschtes Zielvolumen in %", min_value = 0.0, max_value = 1.0, value = 0.4, format="percent", disabled=st.session_state["lock_optimization"])

    if option == "ESO":
        with c1: st.write("Iteratives Entfernen energiearmer Knoten")
        with c2: aggressivity = st.slider("Aggressivität des Entfernens", min_value = 0.0, max_value = 1.0, value = 0.4, disabled=st.session_state["lock_optimization"])
        
    else:
        with c1: st.write("Materialverteilung zur Minimierung der Nachgiebigkeit")
        with c2:
            cc1, cc2, cc3 = st.columns(3)
            with cc1: 
                max_iter = st.number_input("Iterationen",  min_value=1, value=25, disabled=st.session_state["lock_optimization"])
                
            with cc2: 
                #Filter entweder None oder auf Wert gesetzt
                filter_none = st.segmented_control("Filter", ["Ohne", "Mit"], default="Mit", width="stretch", selection_mode="single", disabled=st.session_state["lock_optimization"])
                
                if filter_none == "Ohne":
                    filter_radius = None
                else:
                    filter_input = st.number_input("Wert eingeben", value = 1.5, key = "filter_input", label_visibility="collapsed", disabled=st.session_state["lock_optimization"])
                    filter_radius = filter_input
            
            with cc3: 
                threshold_input = st.radio("Energie-Schwellenwert", ["Niedrig", "Mittel", "Hoch"], index=1, disabled=st.session_state["lock_optimization"])
                if threshold_input == "Niedrig":
                    threshold = 0.01
                elif threshold_input == "Mittel":
                    threshold = 0.05
                else:
                    threshold = 0.1

struc = st.session_state.get("structure")        #Structur holen
optimieren = st.button("Optimierung durchführen", key = "confirm_optimization", width="stretch", disabled=st.session_state["lock_optimization"])

#Container für Plots, so können Plot und Informationen aktualisiert statt neu gezeichnet werden
plot_container = st.container()         

#Nach dem Klick auf "Optimierung durchführen" werden alle Eingabefelder/Zurückbutton gespeert, um eine Änderung des Models zu verhindern. 
if optimieren:
    st.session_state["lock_optimization"] = True
    st.session_state["optimization_error"] = False
    st.rerun()

#Bei einer Sperrung der Eingabefelder wird die Optimierung ausgeführt
if st.session_state["lock_optimization"] == True:
    #Container vorbereiten
    plot_placeholder = plot_container.empty()

    if option == "ESO" :        
        Opt = OptimizerESO(struc)                                 
        opt = Opt.optimize(final_volume, aggressivity)              #Generator initialisieren, Werte werden über "yield" ausgegeben

        for state in opt:
            #Infomationen aus jedem State aus Dict auslesen
            it = state.get("iter")
            mask = state.get("node_mask")
            vol_frac = state.get("vol_frac")
            n_removed = state.get("n_removed")
            remaining = state.get("remaining_nodes")

            initial_node_ids = Opt.initial_node_ids
            fig = plotter.eso_figure(struc, mask, initial_node_ids, it, n_removed, vol_frac)
            #Individueller Key wird abhängig von Iteration zugewiesen, sonst Plotly-Probleme!
            plot_placeholder.plotly_chart(fig, width="stretch", key=f"eso_plot_iter_{it}")

        st.success(f"Bereinigt: Nach {it} Iterationen noch {n_removed} Knoten erhalten.")

    else:        
        Opt = OptimizerSIMP(struc)
        opt = Opt.optimize(final_volume, max_iter, filter_radius=filter_radius)

        #Yield gibt dic mit aktuellem Status zurück
        for state in opt:
            it = state.get("iter")
            x_vals = state.get("x")

            #Prüfung der x_vals, ob sie NaNs sind, da ansonsten ein ValueError kommt
            if x_vals is None or np.isnan(x_vals).any():
                st.session_state["optimization_error"] = True
                st.session_state["lock_optimization"] = False
                break
             
            compliance = state.get("compliance")
            vol_frac = state.get("frac")

            fig = plotter.simp_figure(struc, x_vals, it, compliance, vol_frac)

            plot_placeholder.plotly_chart(fig, width="stretch", key=f"simp_plot_iter_{it}")

        e_rem, n_rem = struc.cleanup_simp(threshold)
        st.success(f"Bereinigt: {e_rem} Federn und {n_rem} Knoten entfernt.")

    #Nach Optimerung: Falls keine Fehlermeldung kommt, Optimierung fertig
    if not st.session_state["optimization_error"]:
        st.session_state["optimization_done"] = True
    
    #Speere der Input_widgets aufheben und Seite neu laden
    st.session_state["lock_optimization"] = False
    st.rerun()

#Je nach Dimension kommt eine leicht andere Fehlermeldung, muss mit dem Button geschlossen werden. 
if st.session_state["optimization_error"]:
    if struc.dim == 2:
        st.error("Eine SIMP-Optimierung ohne Filter ist aufgrund der derzeitigen Lagerung nicht möglich. \
                Entweder SIMP-Optimierung mit Filter machen, Lagerungen ändern oder ESO-Optimierer nutzen.")
    else:
        st.error("Eine SIMP-Optimierung ist aufgrund der derzeitigen Lagerung nicht möglich. \
                Entweder Lagerungen an die Seite setzen oder ESO-Optimierer nutzen.")
    if st.button("Fehlermeldung schließen", type="primary", width="stretch"):
        st.session_state["optimization_error"] = False
        st.rerun()


#Nach abgeschlossener Optimierung: Ergebnisse darstellen, Logik in Module ausgelagert 
if st.session_state.get("optimization_done"):
    plot_optimization_results(struc, plotter)

st.divider()

if st.button("Randbedingungen bearbeiten", width="stretch"):
    st.switch_page("pages/2_Festlager_und_Kräfte.py")
