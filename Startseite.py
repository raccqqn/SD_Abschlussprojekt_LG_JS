import streamlit as st
from modules.state import init_session_states, init_default_session_states

st.set_page_config("SWD Abschlussprojekt")

init_session_states()

st.title("SWD Abschlussprojekt", text_alignment="center")
st.subheader("Joachim Spitaler und Leonie Graf", text_alignment="center")

if st.button("Neue Modellierung starten", use_container_width=True):
    init_session_states()
    init_default_session_states()
    st.switch_page("pages/1_Grundmaße.py")

st.button("Letzte Berechnung wiederherstellen", use_container_width=True)
    #FOR THE FUTURE: Hier die Verknüpfung zu JSON, damit alte Daten aufgerufen werden
    #Dafür Session state aufrufen, der die JSON gespeicherten Daten beinhaltet