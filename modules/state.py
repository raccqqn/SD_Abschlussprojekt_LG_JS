import streamlit as st

Default = {
    "page" : 1,
    "length" : 100,
    "width" : 20,
    "depth" : 1,
    "EA" : 1000.0,
    "supports" : {},
    "forces" : {},
    "ui_input_changed" : False,
    "structure" : None,
    "lock_optimization" : False,
    "optimization_done" : False,
    "u_final" : None
}

def init_session_states():                  #Eigentliches Initialisieren der Session States
    for key, value in Default.items():
        if key not in st.session_state:
            st.session_state[key] = value

def init_default_session_states():          #session_states auf default Werte setzen
    for key, value in Default.items():
        st.session_state[key] = value

def init_current_session_states():
    pass 

def init_remove_input_force_support():      #Kraft und Lager entfernen
    st.session_state["forces"].clear()
    st.session_state["supports"].clear()
    st.session_state["ui_input_changed"] = False

def init_empty_structure_state():           #Structur leeren - wird nicht gebraucht bis jetzt
    st.session_state["structure"] = None

def init_max_values():                      #Maximum Werte für Buttons ( Maximale Koordinate) in ui_parts auf "nicht ausgewählt" setzen
    if "x_max" not in st.session_state:
        st.session_state["x_max"] = False
    if "y_max" not in st.session_state:
        st.session_state["y_max"] = False
    if "z_max" not in st.session_state:
        st.session_state["z_max"] = False

def init_all_y_values_values():            #Maximum Werte für Auswahl aller Koordinaten auf "nicht ausgewählt" setzen         
    if "all_z_values" not in st.session_state:
        st.session_state["all_z_values"] = False
    if "all_y_values" not in st.session_state:
        st.session_state["all_y_values"] = False