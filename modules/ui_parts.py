import streamlit as st
import numpy as np
from streamlit_elements import elements, mui
from structure import Structure
from modules.state import init_max_values, init_all_y_values_values
from PIL import Image, ImageDraw

def sync_ui_values():                                       #Session_States eingaben aktualisieren: 
    st.session_state["length"] = st.session_state["ui_length"]    #2 unterschiedliche ses-stat, damit im Eingabefeld immer der aktuelle Wert steht.
    st.session_state["width"] = st.session_state["ui_width"]
    st.session_state["depth"] = st.session_state["ui_depth"]
    st.session_state["EA"] = st.session_state["ui_EA"]

def sync_x_max_value():
    if st.session_state["x_max"]:
        st.session_state["x_value"] = st.session_state["length"]-1

def sync_y_max_value():
    if st.session_state["y_max"]:
        st.session_state["y_value"] = st.session_state["width"]-1

def sync_z_max_value():
    if st.session_state["z_max"]:
        st.session_state["z_value"] = st.session_state["depth"]-1


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
        if any(mask):                                                                         #Mindestens 1 Wert muss TRUE sein
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
        all_y_values = st.toggle("Alle y-Werte", value = False, key = "all_y_values", disabled = st.session_state["y_max"] or st.session_state["all_z_values"] )

        #Wert für y definieren, je nach Button
        if y_max: y = st.session_state["width"]-1
        else: y = y_input
       
    with c3: 
        #Wie bei y werden die Widgets deaktiviert
        z_input = st.number_input("z", min_value = 0, max_value = st.session_state["depth"] - 1, value = 0, key = "z_sup", disabled=st.session_state["z_max"] or st.session_state["all_z_values"] )
        z_max = st.checkbox("Maximaler z-Wert", key = "z_max", on_change=sync_z_max_value, disabled=st.session_state["all_z_values"])
        all_z_values = st.toggle("Alle z-Werte", value = False, key = "all_z_values", disabled = st.session_state["z_max"] or st.session_state["all_y_values"] )

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
            if all_y_values == True:
                for i in range(st.session_state["width"]):                                 #Iterieren über die ganze Breite
                    pos = (int(x), int(i), int(z))                                      #Pos aus Eingabe speichern
                    st.session_state["supports"][pos] = {"pos" : pos, "mask" : mask}    #Pos und True/False mask wird gespeichert                                              
            
            elif all_z_values == True:                                                  #Das gleiche mit den z-Koordinaten
                for i in range(st.session_state["depth"]):
                    pos = (int(x), int(y), int(i))
                    st.session_state["supports"][pos] = {"pos" : pos, "mask" : mask}

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



def ui_force_2D():
    st.subheader("Kraft bestimmen - klassisch")
    st.write("Koordinaten der angreifenden Kraft bestimmen und angreifende Kraftstärke definieren.")
    
    c1,c2,c3,c4 = st.columns(4)
    with c1: x = st.number_input("x", min_value = 0, max_value = st.session_state["length"] - 1 , value = 0)       #Standard Koordinaten Eingabe
    with c2: y = st.number_input("y", min_value = 0, max_value = st.session_state["width"] - 1, value = 0)
    with c3: force_x = st.number_input("Fx", value = 0)                                                         #Kräfte Koordinatenweise eingeben
    with c4: force_y = st.number_input("Fy", value = 0)
    add = st.button("Hinzufügen", key = "add_1", width="stretch")

    if add:                                                                 
        pos = (int(x), int(y))                  #Position als Tuple speichern
        f_value = [force_x, force_y]            #Kraft als Vector speichern -> angepasst für apply_force(Tuple, Vektor)
        if any(v != 0 for v in f_value):        #Sinnloses Speichern vermeiden
            st.session_state["forces"][pos] = {"pos" : pos, "vec": f_value}
    
def ui_force_2d_fun():
    st.subheader("Kraft bestimmen - Slider")
    st.write("Vertikale Kraftstärke bestimmen und mit dem Regler den Kraftangriffsbereich auf der x-Achse wählen. \
             _Der Angriff passiert immer oben auf der Balkenoberfläche._")
    c1, c2 =st.columns(2)
    with c1: force_x_plus = st.number_input("Fx", value = 0, key ="force_fun_x")
    with c2: force_y_plus = st.number_input("Fy", value = 0, key="force_fun_y") 

    options = list(range(st.session_state["length"]))
    start_force, end_force = st.select_slider("Kraftangriffsbereich auswählen", options = options, value = [0, st.session_state["length"]-1])
    add2 = st.button("Hinzufügen", key = "add_2", width="stretch")
    st.write(start_force, end_force)

    if add2:
        for i in range(start_force, end_force+1):
            pos = (int(i), int(0))
            f_value = [force_x_plus, force_y_plus]
            if any(v != 0 for v in f_value):
                st.session_state["forces"][pos] = {"pos" : pos, "vec" : f_value}

def ui_force_expander():
    with st.expander("Angreifende Kraft"):
        pos_del = None
        for i, (pos, s) in enumerate(st.session_state["forces"].items()):
            c1, c2 = st.columns([0.8, 0.2])
            with c1:
                st.write(f"{pos}{s['vec']}") 
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
    st.subheader("Kraft bestimmen - Klassisch")
    st.write(f"Die gewünschte Position definieren und den Krafteinfluss an dieser Koordinate wählen.")
    
    c1,c2,c3 = st.columns(3)

    with c1: 
        x = st.number_input("x", min_value = 0, max_value = st.session_state["length"] - 1 , value = 0, key = "x_force_pos") 
        force_x = st.number_input("Fx", value = 0, key = "x_force")
    with c2: 
        y = st.number_input("y", min_value = 0, max_value = st.session_state["width"] - 1, value = 0, key = "y_force_pos")
        force_y = st.number_input("Fy", value = 0, key = "y_force")
    with c3: 
        z = st.number_input("z", min_value = 0, max_value = st.session_state["depth"] - 1, value = 0, key = "z_force_pos")
        force_z = st.number_input("Fz", value = 0, key = "z_force")
        add = st.button("Hinzufügen", key = "add_force", width="stretch")        

    if add:
        pos = (int(x), int(y), int(z))
        f_value = [force_x, force_y, force_z]
        st.session_state["forces"][pos] = {"pos" : pos, "vec": f_value}

def ui_force_3D_fun():
    st.subheader("Kraft bestimmen - Slider")
    st.write(f"Die Slider können auf den bestimmten Bereich gelegt werden, bei welchem die Kraft angreifen soll.\
             _Im Bild ist der gewählte Bereich rot markiert._")
    
    c1, c2, c3 = st.columns(3)
    with c1: force_x_plus = st.number_input("Fx", value = 0, key = "x_force_plus")
    with c2: force_y_plus = st.number_input("Fy", value = 0, key = "y_force_plus")
    with c3: force_z_plus = st.number_input("Fz", value = 0, key = "z_force_plus")

    options_length = list(range(st.session_state["length"]))
    options_depth = list(range(st.session_state["depth"]))
    
    st.select_slider("Kraftangriffsbereich in x-Richtung", options = options_length, value = [0, st.session_state["length"]-1], key="slider_force_x")
    st.select_slider("Kraftangriffsbereich in z-Richtung", options = options_depth, value = [0, st.session_state["depth"]-1], key="slider_force_z")

    ui_force_3d_fun_image()
    
    add3 = st.button("Hinzufügen", key = "add_3", width="stretch")
    start_z, end_z = st.session_state["slider_force_z"]
    start_x, end_x = st.session_state["slider_force_x"]
    
    if add3:
        for i in range(start_z, end_z+1):
            for j in range(start_x, end_x+1):
                pos = (int(j), 0, int(i))
                f_value = [force_x_plus, force_y_plus, force_z_plus]
                if any(v != 0 for v in f_value):
                    st.session_state["forces"][pos] = {"pos" : pos, "vec" : f_value}

def ui_force_3d_fun_image():
    """
    Generiert ein Bild aus der Auswahl der Slider. 
    Stellt dadurch visuell dar, in welchem Bereich bei einer 3D Struktur eine Kraft von oben (y-Richtung) einwirkt.
    """
    width = 700
    height = int(width*st.session_state["depth"]/st.session_state["length"])*4  #Verhältnis: width/height = length/depth -> Bild wird an reales Verhältnis angepasst
                                                                                #Ist auch ein wenig hochskaliert, damit bei geringerer Tiefe eine bessere Darstellung ist. 
    start_force_length, end_force_length = st.session_state["slider_force_x"]   #Werte aus Slider abrufen
    start_force_depth, end_force_depth = st.session_state["slider_force_z"]

    hg = np.array([38, 39, 48], dtype=np.uint8)     #UINT8 = RGB Farbbereich = Zahlen von 0 - 255
                                                    #Gleiche HG Farbe wie st.input_widgets
    x_max = st.session_state["length"]-1        
    z_max = st.session_state["depth"]-1

    z_start = int((start_force_depth/z_max)*height)     #Normierung der Eingabe und skalierung auf die Höhe
    z_end = int((end_force_depth/z_max)*height)

    x_start = int((start_force_length / x_max)*width)
    x_end = int((end_force_length / x_max)*width)

    #Bild entspricht einem array mit: [Höhe x Breite x Farbe]
    img = np.zeros((height, width, 3), dtype=np.uint8)      #Höhe, Breite kommt von oben, Datentyp für die RGB Farbe definiert
    img[:] = hg                                             #Hintergrund einfärben

    mask_x = np.zeros((height, width), dtype=bool)          #True/False Maske für die gewählten x-Werte
    mask_x[:, x_start:x_end+1] = True                       #x_end+1 = letzter Wert inkludiert

    mask_z = np.zeros((height, width), dtype=bool)          #Maske für die ausgewählten z-Werte
    mask_z[z_start:z_end+1, :] = True                       #+1, damit bei z_start=z_end eine Linie dargestellt wird

    color_alone = np.array([0, 70, 70], dtype=np.uint8)     #Einfärben der Bereiche
    color_overlap = np.array([255, 75, 75], dtype=np.uint8) #Überlappungen(tatsächlicher Bereich) wird geefärbt wie rot der Slider

    img[mask_x] = color_alone
    img[mask_z] = color_alone
    img[mask_x & mask_z] = color_overlap
    
    # Bild anzeigen
    st.image(img, caption=f"Ausgewählter Bereich: x: {start_force_length}-{end_force_length} + z: {start_force_depth}-{end_force_depth}")

def update_structure():
    struc = st.session_state.get("structure")
    pass
    struc.update_force()
    struc.update_fixings()
    struc.assign_dofs()
    struc.assemble()
    return struc