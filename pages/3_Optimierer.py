import streamlit as st
from optimizerESO import OptimizerESO
from modules.ui_optimizer import opt_eso, plot_opt, opt_SIMP
from modules.state import init_session_states
from plots import Plotter
import copy
init_session_states()   #Notwendig, damit bei einem refresh der page die Daten geladen werden

c1, c2 = st.columns(2)
with c1: 
    if st.button("Zurück", use_container_width=True):
        st.switch_page("pages/2_Festlager_und_Kräfte.py")
with c2: 
    if st.button("Hauptseite", use_container_width=True):
        st.switch_page("Startseite.py")
st.divider()
st.write(st.session_state.length, st.session_state.width, st.session_state.depth, st.session_state.EA) #Zum Checken

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
            max_iter = st.number_input("Iterationen",  min_value=1, value=10)
            filter = st.number_input("Filter", min_value = 1.0, value = 1.5)

struc_orig = st.session_state.get("structure")                      #Structur holen
optimieren = st.button("Optimierung durchführen", width="stretch")

if optimieren:
    struc_copy = copy.deepcopy(struc_orig)                          #Kopieren der Structur, da die Optimierung die Werte ändert
    if option == "Eso" :                                            #Somit kann immer wieder auf das Original zurückgewiesen werden
        result = opt_eso(struc_copy, final_volume, aggressivity)
        plot_opt(result)
    
    else:
        result2 = opt_SIMP(struc_copy, final_volume, 4, 1.5)
        plot_opt(result2)