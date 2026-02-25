import streamlit as st
from modules.state import init_session_states
from modules.ui_parts import ui_storage_sidebar
from modules.ui_result import plot_optimization_results
from plots import Plotter
from optimizerESO import OptimizerESO
from optimizerSimp import OptimizerSIMP

#Speichern der Struktur zu jedem Zeitpunkt möglich
ui_storage_sidebar()
init_session_states()   #Notwendig, damit bei einem refresh der page die Daten geladen werden
plotter = Plotter()

c1, c2 = st.columns(2)
with c1: 
    if st.button("Zurück", width="stretch", disabled=st.session_state["lock_optimization"]):
        st.switch_page("pages/2_Festlager_und_Kräfte.py")
with c2: 
    if st.button("Hauptseite", width = "stretch"):
        st.switch_page("Startseite.py")
st.divider()
st.write(st.session_state.length, st.session_state.width, st.session_state.depth, st.session_state.EA) #Zum Checken derweil

st.subheader("Optimierer wählen")
c1,c2 = st.columns(2)
with c1: option = st.selectbox("Optimierungs-Wunschkonzert", ("Eso", "SIMP"), disabled=st.session_state["lock_optimization"])
with c2: 
    final_volume = st.slider("Gewünschtes Zielvolumen in %", min_value = 0.0, max_value = 1.0, value = 0.6, format="percent", disabled=st.session_state["lock_optimization"])

    if option == "Eso":
        with c1: st.write("Dieser Optimierer nutzt das Verfahren, was in der Vorlesung vorgschlagen wurde. Es ist abhängig von den Federenergien.")
        with c2: aggressivity = st.slider("Aggressivität des Entfernens", min_value = 0.0, max_value = 1.0, value = 0.4, disabled=st.session_state["lock_optimization"])
        
    else:
        with c1: st.write("Eigens entwickelter Optimierer, der mit der Nachgiebigkeit der einzelnen Federn arbeitet.")
        with c2:
            cc1, cc2 = st.columns(2)
            with cc1: 
                max_iter = st.number_input("Iterationen",  min_value=1, value=25, disabled=st.session_state["lock_optimization"])

            with cc2: 
                #Filter entweder None oder auf Wert gesetzt
                filter_none = st.segmented_control("Filter", ["Ohne", "Mit"], default="Mit", width="stretch", selection_mode="single", disabled=st.session_state["lock_optimization"])
                if filter_none == "Ohne":
                    filter = None
                else:
                    filter_input = st.number_input("Wert eingeben", value = 1.5, label_visibility="collapsed", disabled=st.session_state["lock_optimization"])
                    filter = filter_input


struc = st.session_state.get("structure")                           #Structur holen
optimieren = st.button("Optimierung durchführen", key = "lock_optimization", width="stretch")
#Nach dem Klick auf Optimierung durchführen werden alle Eingabefelder/Zurückbutton gespeert, um eine Änderung des Models zu verhindern. 

#Container für Plots, so können Plot und Informationen aktualisiert statt neu gezeichnet werden
plot_container = st.container()         

if optimieren:
    #Container vorbereiten
    plot_placeholder = plot_container.empty()

    if option == "Eso" :                                            #Somit kann immer wieder auf das Original zurückgewiesen werden
        Opt = OptimizerESO(struc)                                 
        opt = Opt.optimize(final_volume, aggressivity)              #Generator initialisieren, Werte werden über "yield" ausgegeben

        for state in opt:
            #Infomationen aus jedem State aus Dict auslesen
            it = state.get("iter")
            mask = state.get("node_mask")
            vol_frac = state.get("vol_frac")
            n_removed = state.get("n_removed")

            initial_node_ids = Opt.initial_node_ids
            fig = plotter.eso_figure(struc, mask, initial_node_ids, it, n_removed, vol_frac)
            #Individueller Key wird abhängig von Iteration zugewiesen, sonst Plotly-Probleme!
            plot_placeholder.plotly_chart(fig, width="stretch", key=f"eso_plot_iter_{it}")
    
    else:        
        Opt = OptimizerSIMP(struc)
        opt = Opt.optimize(final_volume, max_iter, filter)

        #Yield gibt dic mit aktuellem Status zurück
        for yield_dict in opt:
            it = yield_dict.get("iter")
            x_vals = yield_dict.get("x")
            compliance = yield_dict.get("compliance")
            vol_frac = yield_dict.get("frac")

            fig = plotter.simp_figure(struc, x_vals, it, compliance, vol_frac)

            plot_placeholder.plotly_chart(fig, width="stretch", key=f"simp_plot_iter_{it}")

        
        e_rem, n_rem = struc.cleanup_simp()
        st.success(f"Bereinigt: {e_rem} Federn und {n_rem} Knoten entfernt.")
    
    #Nach Optimerung: Trigger setzen, Seite neu laden
    st.session_state["optimization_done"] = True
    st.rerun()

#Nach abgeschlossener Optimierung: Ergebnisse darstellen, Logik in Module ausgelagert 
if st.session_state.get("optimization_done"):
    plot_optimization_results(struc, plotter)