import streamlit as st

def sync_ui_values():                                               #Session_States eingaben aktualisieren: 
    st.session_state["length"] = st.session_state["ui_length"]      #2 unterschiedliche ses-stat, damit im Eingabefeld immer der aktuelle Wert steht.
    st.session_state["width"] = st.session_state["ui_width"]
    st.session_state["depth"] = st.session_state["ui_depth"]
    st.session_state["EA"] = st.session_state["ui_EA"]

def ui_geometry():                          #In Value wird der aktuelle Wert gespeichert und auch beim Wechseln der Seiten angezeigt.
    with st.form("geom_form"):              #Die Eingabe wird im key gespeichert
        c1, c2, c3, c4 = st.columns(4)
        with c1: laenge = st.number_input("Länge",  min_value=2, value=st.session_state["length"],  key="ui_length", width=150)
        with c2: breite = st.number_input("Breite", min_value=3, value=st.session_state["width"],  key="ui_width", width=150)
        with c3: tiefe = st.number_input("Tiefe", min_value=1, value=st.session_state["depth"],  key="ui_depth", width=150)
        with c4: ea = st.number_input("Dehnsteifigkeit", value=st.session_state["EA"], key="ui_EA", min_value=1.0)
    
        submitted = st.form_submit_button("Bestätigen" )    
        if submitted:                               
            sync_ui_values()         #Beim Bestätigen wird die Eingabe mit dem gespeicherten ses-sta. gleichgestellt. 
            st.session_state["ui_input_changed"] = True