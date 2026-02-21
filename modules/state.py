import streamlit as st

Default = {
    "page" : 1,
    "length" : 9,
    "width" : 4,
    "depth" : 1,
    "EA" : 1000.0,
    "supports" : {},
    "forces" : {},
    "ui_input_changed" : False,
    "structure" : None,
}

def init_session_states():
    for key, value in Default.items():
        if key not in st.session_state:
            st.session_state[key] = value

def init_default_session_states():
    for key, value in Default.items():
        st.session_state[key] = value

def init_current_session_states():
    pass 

def init_remove_input_force_support():
    st.session_state["forces"].clear()
    st.session_state["supports"].clear()
    st.session_state["ui_input_changed"] = False

def init_empty_structure_state():
    st.session_state["structure"] = None
