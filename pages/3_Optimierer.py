import streamlit as st
from modules.ui_optimizer import plot_opt
from modules.state import init_session_states
from plots import Plotter
from optimizerESO import OptimizerESO
from optimizerSimp import OptimizerSIMP
import copy

init_session_states()   #Notwendig, damit bei einem refresh der page die Daten geladen werden
plotter = Plotter()

c1, c2 = st.columns(2)
with c1: 
    if st.button("Zurück", use_container_width=True):
        st.switch_page("pages/2_Festlager_und_Kräfte.py")
with c2: 
    if st.button("Hauptseite", use_container_width=True):
        st.switch_page("Startseite.py")
st.divider()
st.write(st.session_state.length, st.session_state.width, st.session_state.depth, st.session_state.EA) #Zum Checken derweil

st.subheader("Optimierer wählen")
c1,c2 = st.columns(2)
with c1: option = st.selectbox("Optimierungs-Wunschkonzert", ("Eso", "SIMP"))
with c2: 
    final_volume = st.slider("Gewünschtes Zielvolumen in %", min_value = 0.0, max_value = 1.0, value = 0.6)

    if option == "Eso":
        with c1: st.write("Dieser Optimierer nutzt das Verfahren, was in der Vorlesung vorgschlagen wurde. Es ist abhängig von den Federenergien.")
        with c2: aggressivity = st.slider("Aggressivität des Entfernens", min_value = 0.0, max_value = 1.0, value = 0.4)
        
    else:
        with c1: st.write("Eigens entwickelter Optimierer, der mit der Nachgiebigkeit der einzelnen Federn arbeitet.")
        with c2:
            cc1, cc2 = st.columns(2)
            with cc1: max_iter = st.number_input("Iterationen",  min_value=1, value=10)
            with cc2: filter = st.radio("Filter", [1, 1.5], horizontal=True, )

struc = st.session_state.get("structure")                      #Structur holen
optimieren = st.button("Optimierung durchführen", width="stretch")

#Container für Plots, so können Plot und Informationen aktualisiert statt neu gezeichnet werden
plot_container = st.container()         
info_container = st.container()

if optimieren:
    #struc_copy = struc_orig                                         #Kopieren der Structur, da die Optimierung die Werte ändert
    #Container vorbereiten
    plot_placeholder = plot_container.empty()
    info_placeholder = info_container.empty()

    if option == "Eso" :                                            #Somit kann immer wieder auf das Original zurückgewiesen werden
        Opt = OptimizerESO(struc)                                 
        opt = Opt.optimize(final_volume, aggressivity)              #Generator initialisieren, Werte werden über "yield" ausgegeben

        for state in opt:
            #Infomationen aus jedem State aus Dict auslesen
            it = state.get("iter")
            mask = state.get("node_mask")
            remaining = state.get("remaining_nodes")

            initial_node_ids = Opt.initial_node_ids
            fig = plotter.eso_figure(struc, mask, initial_node_ids)
            #Individueller Key wird abhängig von Iteration zugewiesen, sonst Plotly-Probleme!
            plot_placeholder.plotly_chart(fig, width="stretch", key=f"eso_plot_iter_{it}")

            info_placeholder.write(f"Iter: {it} — remaining nodes: {remaining}")
    
    else:        
        Opt = OptimizerSIMP(struc)
        opt = Opt.optimize(final_volume, max_iter, filter)

        #Yield gibt dic mit aktuellem Status zurück
        for yield_dict in opt:
            it = yield_dict.get("iter")
            x_vals = yield_dict.get("x")
            compliance = yield_dict.get("compliance")
            volume = yield_dict.get("volume")

            fig = plotter.simp_figure(struc, x_vals)

            plot_placeholder.plotly_chart(fig, width="stretch", key=f"simp_plot_iter_{it}")
    
            info_placeholder.write(f"Iter: {it} — compliance: {compliance:.4e} — volume: {volume:.3f}")