import streamlit as st
from UI.state import init_max_values, init_all_y_values_values

def sync_x_max_value():
    if st.session_state["x_max"]:
        st.session_state["x_value"] = st.session_state["length"]-1

def sync_y_max_value():
    if st.session_state["y_max"]:
        st.session_state["y_value"] = st.session_state["width"]-1

def sync_z_max_value():
    if st.session_state["z_max"]:
        st.session_state["z_value"] = st.session_state["depth"]-1


def ui_festlager_2d():
    st.subheader("Lager definieren")
    st.write("Koordinate des Lagers bestimmen und die Freiheitsgrade beschränken. ")
    c1,c2,c3,c4 = st.columns(4)
    init_max_values()
    
    with c1: 
        #Eingabe Feld für X-Wert - bei aktiver Chekbox wird Eingabefeld deaktiviert
        x_input = st.number_input("x", min_value = 0, max_value = st.session_state["length"] - 1 , value = 0, key = "x_sup", disabled=st.session_state["x_max"])
        x_max = st.checkbox("Maximaler x-Wert", key = "x_max", on_change=sync_x_max_value)

        if x_max:                               #Bei aktiver Checkbox wird max. Wert ausgegeben
            x = st.session_state["length"]-1
        else:
            x = x_input

    with c2: 
        y_input = st.number_input("y", min_value = 0, max_value = st.session_state["width"] - 1, value = 0, key = "y_sup", disabled=st.session_state["y_max"])
        y_max = st.checkbox("Maximaler y-Wert", key = "y_max", on_change=sync_y_max_value)

        if y_max:
            y = st.session_state["width"]-1

        else:
            y = y_input    

    with c3: 
        selection = st.segmented_control("Fixierte Freiheitsgrade", ["Ux", "Uy"], selection_mode="multi", key = "dofs_sup")
        mask = ["Ux" in selection, "Uy" in selection]
    with c4: add = st.button("Hinzufügen", key = "add_sup", width="stretch")
    
    if add:
        if any(mask):                                                                           #Mindestens 1 Wert muss TRUE sein
            pos = (int(x), int(y))                                                              #Knoten Koordinate
            st.session_state["supports"][pos] = {"pos" : pos, "mask" : mask}                    #Speichern im Dictionary - Überschreibt Position, falls da schon ein Wert drinnen war

def ui_festlager_3d():
    c1,c2,c3,c4 = st.columns(4)
    init_max_values()
    init_all_y_values_values()

    with c1: 
        x_input = st.number_input("x", min_value = 0, max_value = st.session_state["length"] - 1 , value = 0, key = "x_sup", disabled=st.session_state["x_max"]) 
        x_max = st.checkbox("Maximaler x-Wert", key = "x_max", on_change=sync_x_max_value)
    
        if x_max:
            x = st.session_state["length"]-1
        else:
            x = x_input

    with c2: 
        #Die Input Widgets (checkbox/toggle) werden je nach gewählten Widget deaktiviert mit disabled =
        y_input = st.number_input("y", min_value = 0, max_value = st.session_state["width"] - 1, value = 0, key = "y_sup", disabled = st.session_state["all_y_values"] or st.session_state["y_max"] )
        y_max = st.checkbox("Maximaler y-Wert", key = "y_max", on_change=sync_y_max_value, disabled=st.session_state["all_y_values"] )
        all_y_values = st.toggle("Alle y-Werte", value = False, key = "all_y_values", disabled = st.session_state["y_max"])

        #Wert für y definieren, je nach Button
        if y_max: y = st.session_state["width"]-1
        else: y = y_input
       
    with c3: 
        #Wie bei y werden die Widgets deaktiviert
        z_input = st.number_input("z", min_value = 0, max_value = st.session_state["depth"] - 1, value = 0, key = "z_sup", disabled=st.session_state["z_max"] or st.session_state["all_z_values"] )
        z_max = st.checkbox("Maximaler z-Wert", key = "z_max", on_change=sync_z_max_value, disabled=st.session_state["all_z_values"])
        all_z_values = st.toggle("Alle z-Werte", value = False, key = "all_z_values", disabled = st.session_state["z_max"] )

        #Wert für z definieren, je nach Button
        if z_max: z = st.session_state["depth"]-1
        else: z = z_input
        
    with c4: 
        #Freiheitsgrade definieren - auch mehrere können gewählt werden mit selection_mode = "multi"
        selection = st.segmented_control("Fixierte Freiheitsgrade", ["Ux", "Uy", "Uz"], selection_mode="multi", key = "dofs_sup")
        mask = ["Ux" in selection, "Uy" in selection, "Uz" in selection]                #Maske mit True/False, je nach Auswahl
        add = st.button("Hinzufügen", key = "add_sup", width = "stretch")
        
    if add:                                                                             #Hinzufügen der Freiheitsgrade in ein Dictionary
        if any(mask):                                                                   
            if all_y_values == True and all_z_values == False:
                for i in range(st.session_state["width"]):                              #Iterieren über die ganze Breite
                    pos = (int(x), int(i), int(z))                                      #Pos aus Eingabe speichern
                    st.session_state["supports"][pos] = {"pos" : pos, "mask" : mask}    #Pos und True/False mask wird gespeichert                                              
            
            elif all_z_values == True and all_y_values == False:                                                  #Das gleiche mit den z-Koordinaten
                for i in range(st.session_state["depth"]):
                    pos = (int(x), int(y), int(i))
                    st.session_state["supports"][pos] = {"pos" : pos, "mask" : mask}

            elif all_y_values == True and all_z_values == True:
                for i in range(st.session_state["width"]):                              #Iterieren über die ganze Breite
                    for j in range(st.session_state["depth"]):
                        pos = (int(x), int(i), int(j))                                      #Pos aus Eingabe speichern
                        st.session_state["supports"][pos] = {"pos" : pos, "mask" : mask}    #Pos und True/False mask wird gespeichert 

            else:
                pos = (int(x), int(y), int(z))                                          #Koordinate aus den normalen inupt_widgets
                st.session_state["supports"][pos] = {"pos" : pos, "mask" : mask}        #Speichern im Dictionary - Überschreibt Position, falls da schon ein Wert drinnen war

def ui_festlager_expander():
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