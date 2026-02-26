import streamlit as st
from UI.state import init_session_states, init_default_session_states
from UI.ui_parts import sync_session_state_with_struc
from src.structureManager import StructureManager
from datetime import datetime

st.session_state.clear()
st.cache_data.clear()
st.cache_resource.clear()

st.set_page_config("SWD Abschlussprojekt")

init_session_states()

if "optimization_from_structure" not in st.session_state:
    st.session_state["optimization_from_structure"] = False

st.image("resources/cover.png")

if st.button("Neue Struktur erstellen", width = "stretch"):
    init_session_states()
    init_default_session_states()
    st.switch_page("pages/1_Grundmaße.py")

manager = StructureManager()

with st.expander("Vorhandene Struktur laden"):

    #Alle Einträge aus TinyDB laden
    all_entries = manager.table.all()

    #Wenn Einträge existieren:
    if all_entries:
        #Liste der Namen anzeigen
        names = [entry["name"] for entry in all_entries]
        selected_name = st.selectbox("Wähle eine gespeicherte Struktur:", names)

        #Entry auswählen, Metadata der ausgewählten Structure anzeigen
        selected_entry = next(e for e in all_entries if e["name"] == selected_name)

        #Metadata vorbereiten, Zeit in lesbares Format wandeln
        date = datetime.fromisoformat(selected_entry["date"])
        clean_date = date.strftime("%d.%m.%Y, %H:%M")
        st.caption(f"Datum: {clean_date} | Dimension: {selected_entry["dim"]}D | EA: {selected_entry["EA"]}")

        #Spalten für Laden, Löschen
        col1, col2 = st.columns([3, 1])

        with col1:
            #Button zum Bestätigen des Ladens
            if st.button("Laden bestätigen", width="stretch"):
                #Ladekreis anzeigen
                with st.spinner(f"Lade {selected_name}..."):
                    #Struktur laden
                    loaded_struct = manager.load(selected_name)

                    #Struktur und alle Attribute in Session State speichern
                    sync_session_state_with_struc(loaded_struct)
                    st.session_state["optimization_from_structure"] = True
                    st.switch_page("pages/3_Optimierer.py")    #query_params gibt Info mit, woher man kommt bei Klick
                        
                    
                    st.toast(f"✅ {selected_name} erfolgreich geladen!")

                    #Trigger setzen
                    st.session_state["ui_input_changed"] = True  

            with col2:
                if st.button("Löschen", type="primary", width="stretch"):
                    manager.delete(selected_name)
                    st.toast(f"Projekt {selected_name} gelöscht.")
                    #Neu laden
                    st.rerun()
                    
    else: st.info("Keine gespeicherten Strukturen in der Datenbank gefunden!")
