import streamlit as st
import numpy as np
from src.solver_global import Solver
from src.optimizerSimp import OptimizerSIMP


def plot_optimization_results(structure, plotter):
    """
    Finale Visualisierung auslagern
    """
    st.divider()
    st.subheader("Analyse des Endergebnisses")
    
    #Solver sicherheitshalber neu ausführen, da vorwiegend Singularitäten bei ESO Verschiebungen verfälschen
    #In session_state speichern
    if st.session_state.get("u_final") is None:
        with st.spinner("Berechne finale Verformung..."):
            solver = Solver(structure)
            st.session_state["u_final"] = solver.solve()
    
    #Verschiebung einmalig berechnen: Flüssigere Darstellung
    #Maximale Verschiebung zur Bestimmung der Scale speichern
    u_final = st.session_state["u_final"]
    u_max = np.max(np.abs(u_final))

    #Zwei Tabs für finale Struktur, Verformung
    tab1, tab2, tab3, tab4 = st.tabs(["Optimierte Struktur", "Verformungs-Analyse", 
                                      "Normalkraft-Verteilung", "Feder-Energien"])
    
    #Struktur plotten, Funktionen wiederverwenden, so werden auch Lager und Kräfte angezeigt
    with tab1:
        st.write("#### Lager und Kräfte am optimierten Bauteil")
        if structure.dim == 3:
            plotter.body_undeformed(structure)
        else:
            plotter.beam_undeformed(structure)

    #Verformungs-Analyse    
    with tab2:
        st.write("#### Vergleich: Unverformt / Verformt")
        
        #Standard-Skalierung abhängig von Länge, Verformung bestimmen
        length = st.session_state.get("length", 1.0)
        #Keine Verformung
        if u_max == 0:
            default_scale = 1.0
        else: default_scale = 0.1*length/u_max

        #Maximum Slider: 10-fache Standardskalierung
        scale = st.slider("Verformungs-Skalierung", 0.0, float(default_scale * 10), 
                          value=float(default_scale), key="res_scale_slider")
        
        fig_res = plotter.plot_result_comparison(structure, u_final, scale=scale)
        st.plotly_chart(fig_res, width="stretch", key="final_comparison_plot")
        
    with tab3:
        st.write("#### Visualisierung der Feder-Kräfte")
        
        #Federkräfte berechnen
        forces = structure.calc_element_forces(u_final)

        fig_forces = plotter.plot_colored_structure(structure, u_final, forces)
        st.plotly_chart(fig_forces, width="stretch", key="spring_forces_plot")

    with tab4:
        st.write("#### Visualisierung der Feder-Energien")
        
        energies = structure.calc_element_energies(u_final)

        fig_energy = plotter.plot_colored_structure(structure, u_final, energies, 
                                                    color_scheme="inferno", symmetric=False)
        st.plotly_chart(fig_energy, width="stretch", key="spring_energies_plot")