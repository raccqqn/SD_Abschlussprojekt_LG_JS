import streamlit as st

def sync_ui_values():                                       #Session_States eingaben aktualisieren: 
    st.session_state.length = st.session_state.ui_length    #2 unterschiedliche ses-stat, damit im Eingabefeld immer der aktuelle Wert steht.
    st.session_state.width = st.session_state.ui_width
    st.session_state.depth = st.session_state.ui_depth
    st.session_state.EA = st.session_state.ui_EA

def ui_geometry():                          #In Value wird der aktuelle Wert gespeichert und auch beim Wechseln der Seiten angezeigt.
    with st.form("geom_form"):              #Die Eingabe wird im key gespeichert
        c1, c2, c3, c4 = st.columns(4)
        with c1: laenge = st.number_input("Länge",  min_value=2, value=st.session_state.length,  key="ui_length", width=150)
        with c2: breite = st.number_input("Breite", min_value=3, value=st.session_state.width,  key="ui_width", width=150)
        with c3: tiefe = st.number_input("Tiefe", min_value=1, value=st.session_state.depth,  key="ui_depth", width=150)
        with c4: ea = st.number_input("Steifigkeit", value=st.session_state.EA, key="ui_EA", min_value=1.0)
    
        submitted = st.form_submit_button("Bestätigen" )    
        if submitted:                               
            sync_ui_values()         #Beim Bestätigen wird die Eingabe mit dem gespeicherten ses-sta. gleichgestellt. 
            st.session_state["ui_input_changed"] = True

def ui_festlager_2d():
    c1,c2,c3,c4 = st.columns(4)

    with c1: x = st.number_input("x", min_value = 0, max_value = st.session_state.length - 1 , value = 0, key = "x_sup")
    with c2: y = st.number_input("y", min_value = 0, max_value = st.session_state.width - 1, value = 0, key = "y_sup")
    with c3: 
        selection = st.segmented_control("Fixierte Freiheitsgrade", ["Ux", "Uy"], selection_mode="multi", key = "dofs_sup")
        mask = ["Ux" in selection, "Uy" in selection]
    with c4: add = st.button("Hinzufügen", key = "add_sup", width="stretch")
    
    if add:
        if any(mask):                                                                           #Mindestens 1 Wert muss TRUE sein
            pos = (int(x), int(y))                                                              #Knoten Koordinate
            st.session_state["supports"][pos] = {"pos" : pos, "mask" : mask}                    #Speichern im Dictionary - Überschreibt Position, falls da schon ein Wert drinnen war

    with st.expander("Aktuelle Lager"):
        pos_del = None                                                                  #Platzhalter
        for i, (pos, s) in enumerate(st.session_state["supports"].items(), start=1):    
            c1, c2 = st.columns([0.8, 0.2])
            with c1:
                st.write(f"{pos}  {s['mask']}")                                         #Angeben der Position und Kraft
            with c2:
                if st.button("Entfernen", key=f"sup_del_{i}"):                          #Beim Klick auf entfernen, wird die pos gespeichert    
                    pos_del = pos

        if pos_del is not None:                                                         #Beim Verändern von pos_del
            st.session_state["supports"].pop(pos_del, None)                             #wird dieser wert gePOPt = gelöscht aus dem dict
            st.rerun()

        if st.button("Alle löschen", key="sup_clear"):
            st.session_state["supports"].clear()
            st.rerun()

def ui_festlager_3d():
    c1,c2,c3,c4 = st.columns(4)

    with c1: x = st.number_input("x", min_value = 0, max_value = st.session_state.length - 1 , value = 0, key = "x_sup") 
    with c2: y = st.number_input("y", min_value = 0, max_value = st.session_state.width - 1, value = 0, key = "y_sup")
    with c3: 
        z = st.number_input("z", min_value = 0, max_value = st.session_state.depth - 1, value = 0, key = "z_sup")
        full_row = st.checkbox("Ganze Tiefe", value = False, key = "full_row")
    with c4: 
        selection = st.segmented_control("Fixierte Freiheitsgrade", ["Ux", "Uy", "Uz"], selection_mode="multi", key = "dofs_sup")
        mask = ["Ux" in selection, "Uy" in selection, "Uz" in selection]                #Maske mit True/False, je nach Auswahl
        add = st.button("Hinzufügen", key = "add_sup")
        
    if add:                                                                             #Hinzufügen der Freiheitsgrade in ein Dictionary
        if any(mask):                                                                   #wenn full_row gewählt wird, ist die gesamt Reihe gemeint
            if full_row == True:
                for i in range(st.session_state.depth):                                 #Iterieren über die ganze Tiefe
                    pos = (int(x), int(y), int(i))                                      #Pos aus Eingabe speichern
                    st.session_state["supports"][pos] = {"pos" : pos, "mask" : mask}    #Pos und True/False mask wird gespeichert                                              
            else:
                pos = (int(x), int(y), int(z))                                          # Koordinate
                st.session_state["supports"][pos] = {"pos" : pos, "mask" : mask}        #Speichern im Dictionary - Überschreibt Position, falls da schon ein Wert drinnen war

    with st.expander("Aktuelle Lager"):
        pos_del = None                                                                  #Platzhalter
        for i, (pos, s) in enumerate(st.session_state["supports"].items(), start=1):    
            c1, c2 = st.columns([0.8, 0.2])
            with c1:
                st.write(f"{pos}  {s['mask']}")                                         #Angeben der Position und Kraft
            with c2:
                if st.button("Entfernen", key=f"sup_del_{i}"):                          #Beim Klick auf entfernen, wird die pos gespeichert    
                    pos_del = pos

        if pos_del is not None:                                                         #Beim Verändern von pos_del
            st.session_state["supports"].pop(pos_del, None)                             #wird dieser wert gePOPt = gelöscht aus dem dict
            st.rerun()

        if st.button("Alle löschen", key="sup_clear"):
            st.session_state["supports"].clear()
            st.rerun()


def ui_force_2D():

    c1,c2,c3,c4 = st.columns(4)

    with c1: x = st.number_input("x", min_value = 0, max_value = st.session_state.length - 1 , value = 0)       #Standard Koordinaten Eingabe
    with c2: y = st.number_input("y", min_value = 0, max_value = st.session_state.width - 1, value = 0)
    with c3: force_x = st.number_input("Fx", value = 0)                                                         #Kräfte Koordinatenweise eingeben
    with c4: 
        force_y = st.number_input("Fy", value = 0)
        add = st.button("Hinzufügen", key = "add_1", width="stretch")

        if add:                                                                 
            pos = (int(x), int(y))                  #Position als Tuple speichern
            f_value = [force_x, force_y]            #Kraft als Vector speichern -> angepasst für apply_force(Tuple, Vektor)
            if any(v != 0 for v in f_value):        #Sinnloses Speichern vermeiden
                st.session_state["forces"][pos] = {"pos" : pos, "vec": f_value}
    st.divider()
    st.subheader("Kraft bestimmen - aber mit Spaß")
    st.write("Jaja, ich mach's ja nochmal schöner, aber derweil noch Platzhalter. " \
    "Muss klären, was wir da machen mit der y-Koordinate und wie wir das in 3D machen. ")

    options = list(range(st.session_state["length"]))
    start_force, end_force = st.select_slider("Kraftangriffsbereich auswählen", options = options, value = [0, st.session_state.length-1])
    add2 = st.button("Hinzufügen", key = "add_2", width="stretch")
    st.write(start_force, end_force)

    if add2:
        for i in range(start_force, end_force+1):
            pos = (int(i), int(y))
            f_value = [force_x, force_y]
            if any(v != 0 for v in f_value):
                st.session_state["forces"][pos] = {"pos" : pos, "vec" : f_value}


    with st.expander("Angreifende Kraft"):
        pos_del = None
        for i, (pos, s) in enumerate(st.session_state["forces"].items()):
            c1, c2 = st.columns([0.8, 0.2])
            with c1:
                st.write(f"{pos} {s['vec']}") 
            with c2:
                if st.button("Entfernen", key=f"force_del_{i}"):
                    pos_del = pos
        
        if pos_del is not None:
            st.session_state["forces"].pop(pos_del, None)
            st.rerun()

        if st.button("Alle löschen", key="forces_clear"):
            st.session_state["forces"].clear()
            st.rerun()
        


def ui_force_3D():

    c1,c2,c3,c4, c5, c6 = st.columns(6)

    with c1: x = st.number_input("x", min_value = 0, max_value = st.session_state.length - 1 , value = 0, key = "x_force_pos") 
    with c2: y = st.number_input("y", min_value = 0, max_value = st.session_state.width - 1, value = 0, key = "y_force_pos")
    with c3: z = st.number_input("z", min_value = 0, max_value = st.session_state.depth - 1, value = 0, key = "z_force_pos")
    
    with c4: force_x = st.number_input("Fx", value = 0, key = "x_force")
    with c5: force_y = st.number_input("Fy", value = 0, key = "y_force")
    with c6: 
        force_z = st.number_input("Fz", value = 0, key = "z_force")
        add = st.button("Hinzufügen", key = "add_force")

        if add:
            pos = (int(x), int(y), int(z))
            f_value = [force_x, force_y, force_z]
            st.session_state["forces"][pos] = {"pos" : pos, "vec": f_value}

    with st.expander("Angreifende Kraft"):
        pos_del = None
        for i, (pos, s) in enumerate(st.session_state["forces"].items()):
            c1, c2 = st.columns([0.8, 0.2])
            with c1:
                st.write(f"{pos} {s['vec']}") 
            with c2:
                if st.button("Entfernen", key=f"force_del_{i}"):
                    pos_del = pos
        
        if pos_del is not None:
            st.session_state["forces"].pop(pos_del, None)
            st.rerun()

        if st.button("Alle löschen", key="forces_clear"):
            st.session_state["forces"].clear()
            st.rerun()