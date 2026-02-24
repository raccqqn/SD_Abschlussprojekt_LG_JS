import streamlit as st
from modules.state import init_session_states, init_default_session_states
from structureManager import StructureManager

st.set_page_config("SWD Abschlussprojekt")
init_session_states()
st.image("cover.png")

if st.button("Neue Modellierung starten", width = "stretch"):
    init_session_states()
    init_default_session_states()
    st.switch_page("pages/1_Grundmaße.py")

st.button("Letzte Berechnung wiederherstellen", width = "stretch")
    #FOR THE FUTURE: Hier die Verknüpfung zu JSON, damit alte Daten aufgerufen werden
    #Dafür Session state aufrufen, der die JSON gespeicherten Daten beinhaltet