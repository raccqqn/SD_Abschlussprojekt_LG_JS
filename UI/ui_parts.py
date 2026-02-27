import streamlit as st
import numpy as np
import base64   # Für Hintergrundbild
from UI.state import init_max_values, init_all_y_values_values, init_remove_input_force_support
from src.structureManager import StructureManager 
from datetime import datetime

def ui_storage_sidebar():
    """Sidebar zum Speichern einer Struktur"""

    #Logo einfügen - Achtung beim klick darauf werden alle Eingaben gelöscht 
    if st.logo("resources/logo_1.png", icon_image="resources/logo_2_1.png"):
        init_remove_input_force_support()
        st.session_state.clear()
        st.cache_data.clear()
        st.cache_resource.clear()
 
    st.sidebar.subheader("Struktur speichern")

    with st.sidebar.expander("Aktuelle Struktur speichern", expanded=False):
        manager = StructureManager()        
        
        #Existierende Namen für Überschreiben aus Datenbank holen
        try:
            existing_saves = [entry["name"] for entry in manager.table.all()]
        except:
            existing_saves = []

        if "save_name_input" not in st.session_state:
            st.session_state["save_name_input"] = f"Projekt_{datetime.now().strftime("%H%M")}"

        #Namensvorschlag updaten
        def update_save_name():
            sel = st.session_state.overwrite_select
            #Wurde Save ausgewählt: Als Namensvorschlag einfügen
            if sel != "|NEU ERSTELLEN|":
                st.session_state.save_name_input = sel
            else:
                #Falls zurück auf "NEW SAVE" gewechselt wird, Standardvorschlag anzeigen
                st.session_state.save_name_input = f"Projekt_{datetime.now().strftime("%H%M")}"
        
        #Struktur aus Liste auswählen
        if existing_saves:
            #on_change: Bei Änderung der Auswahl: Vorschlag über Funktion aktualisieren!
            selected_existing = st.selectbox("Vorhandene Struktur wählen", 
                                options=["|NEU ERSTELLEN|"] + existing_saves,
                                key="overwrite_select", on_change=update_save_name)
    
        else:
            suggested_name = f"Projekt_{datetime.now().strftime("%H%M")}"
       
        #Speichername festlegen, Key in Session-State nutzen
        save_name = st.text_input("Name festlegen", key="save_name_input")

        #Warnung, falls Save schon existiert
        if save_name in existing_saves:
            st.warning(f"/{save_name}/ existiert bereits und wird überschrieben.")
        
        if st.sidebar.button("Speichern", width="stretch", key="save_button_global"):
            structure = st.session_state.get("structure")
            
            if structure is not None:
                try:
                    manager.save(save_name, structure)
                    #Erfolgmeldung, Toast
                    st.toast(f"{save_name} erfolgreich gespeichert!")
                except Exception as e:
                    st.sidebar.error(f"Fehler beim Speichern: {e}")
            else:
                st.sidebar.warning("Keine Struktur zum Speichern vorhanden.")

def ui_pages_sidebar():
    """
    Automatischer Sidebar vom /pages Ordner wird deaktiviert und mit einem eigens erstellen ersetzt.
    """
    st.sidebar.divider()
    st.sidebar.subheader("Navigation")
    with st.sidebar:
        if st.button("Zur Startseite", width = "stretch"):
            st.session_state["confirm_reset"] = True
        st.caption("_Neue Struktur erstellen, Aktuelle wird verworfen!_", text_alignment="center")
    
        #Wenn reset noch nicht bestätigt wurde: confirm True!
        confirm = st.session_state.get("confirm_reset", False)
        
        if confirm:
            st.warning("Die aktuelle Struktur wird gelöscht, falls sie nicht gespeichert wurde! Fortfahren?")
            #Spalten für ja, nein festlegen
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Ja"):
                    st.session_state.clear()
                    st.cache_data.clear()
                    st.cache_resource.clear()
                    st.switch_page("Startseite.py")
            with col2:
                if st.button("Nein"):
                    st.session_state["confirm_reset"] = False
                    st.session_state["structure_got_saved"] = False
                    #Sonst muss Button 2 mal geklickt werden
                    st.rerun()


def set_bg_hack(main_bg):       #Quelle:  https://discuss.streamlit.io/t/how-do-i-use-a-background-image-on-streamlit/5067
    bin_str = base64.b64encode(open(main_bg, 'rb').read()).decode()
    
    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)
