import streamlit as st
import numpy as np

def ui_force_2D():
    st.subheader("Kraft bestimmen - klassisch")
    st.write("Angriffspunkt festlegen und zugehörigen Kraftvektor definieren.")
    
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
    """
    Kraft wird anhand von der Position des Input Sliders bestimmt. 
    Angriffsfläche ist immer die obere Kante. 
    """
    
    st.subheader("Kraftbereich bestimmen")
    st.write("Kraftvektor festlegen und mit dem Regler den Kraftangriffsbereich auf der x-Achse wählen. \
             _Die Kraft greift immer an der Außenkante an._")
    c1, c2 =st.columns(2)
    with c1: force_x_plus = st.number_input("Fx", value = 0, key ="force_fun_x")
    with c2: force_y_plus = st.number_input("Fy", value = 0, key="force_fun_y") 

    options = list(range(st.session_state["length"]))
    start_force, end_force = st.select_slider("Kraftangriffsbereich wählen", options = options, value = [0, st.session_state["length"]-1])
    add2 = st.button("Hinzufügen", key = "add_2", width="stretch")
    st.write(start_force, end_force)

    if add2:
        if not any([force_x_plus, force_y_plus]):               #Warnmeldung, falls Kräfte = 0
            st.warning("Kraftstärke (Fx, Fy) definieren!")

        else:
            for i in range(start_force, end_force+1):
                pos = (int(i), int(0))
                f_value = [force_x_plus, force_y_plus]
                if any(v != 0 for v in f_value):
                    st.session_state["forces"][pos] = {"pos" : pos, "vec" : f_value}

def ui_force_expander():
    with st.expander("Angreifende Kräfte"):
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
    st.write(f"Angriffspunkt festlegen und zugehörigen Kraftvektor definieren.")
    
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
    st.subheader("Kraftbereich bestimmen")
    st.write(f"Mit den Slidern den Kraftangriffsbereich festlegen. Der gewählte Bereich ist rot markiert.\
             _Die Kraft greift immer an der Oberfläche an._")
    
    c1, c2, c3 = st.columns(3)
    with c1: force_x_plus = st.number_input("Fx", value = 0, key = "x_force_plus")
    with c2: force_y_plus = st.number_input("Fy", value = 0, key = "y_force_plus")
    with c3: force_z_plus = st.number_input("Fz", value = 0, key = "z_force_plus")

    options_length = list(range(st.session_state["length"]))
    options_width = list(range(st.session_state["width"]))
    z_max = st.session_state["depth"]-1
    
    st.select_slider("Kraftangriffsbereich in x-Richtung", options = options_length, value = [0, st.session_state["length"]-1], key="slider_force_x")
    st.select_slider("Kraftangriffsbereich in y-Richtung", options = options_width, value = [0, st.session_state["width"]-1], key="slider_force_y")

    ui_force_3d_fun_image()
    
    add3 = st.button("Hinzufügen", key = "add_3", width="stretch")
    start_z, end_z = st.session_state["slider_force_y"]
    start_x, end_x = st.session_state["slider_force_x"]
    
    if add3:
        if not any([force_x_plus, force_y_plus, force_z_plus]):
            st.warning("Kraftstärke (Fx, Fy, Fz) definieren!")
            
        else:
            for i in range(start_z, end_z+1):
                for j in range(start_x, end_x+1):
                    pos = (int(j), int(i), z_max)
                    f_value = [force_x_plus, force_y_plus, force_z_plus]
                    if any(v != 0 for v in f_value):
                        st.session_state["forces"][pos] = {"pos" : pos, "vec" : f_value}

def ui_force_3d_fun_image():
    """
    Generiert ein Bild aus der Auswahl der Slider. 
    Stellt dadurch visuell dar, in welchem Bereich bei einer 3D Struktur eine Kraft von oben (y-Richtung) einwirkt.
    """
    width = 700
    height = int(width*st.session_state["width"]/st.session_state["length"])    #Verhältnis: width/height = st.length/st.width -> Bild wird an reales Verhältnis angepasst
    start_force_length, end_force_length = st.session_state["slider_force_x"]   #Werte aus Slider abrufen
    start_force_width, end_force_width = st.session_state["slider_force_y"]

    hg = np.array([38, 39, 48], dtype=np.uint8)     #UINT8 = RGB Farbbereich = Zahlen von 0 - 255
                                                    #Gleiche HG Farbe wie st.input_widgets
    x_max = st.session_state["length"]-1        
    y_max = st.session_state["width"]-1

    y_start = int((start_force_width/y_max)*height)     #Normierung der Eingabe und skalierung auf die Höhe
    y_end = int((end_force_width/y_max)*height)

    x_start = int((start_force_length / x_max)*width)
    x_end = int((end_force_length / x_max)*width)

    #Bild entspricht einem array mit: [Höhe x Breite x Farbe]
    img = np.zeros((height, width, 3), dtype=np.uint8)      #Höhe, Breite kommt von oben, Datentyp für die RGB Farbe definiert
    img[:] = hg                                             #Hintergrund einfärben

    mask_x = np.zeros((height, width), dtype=bool)          #True/False Maske für die gewählten x-Werte
    mask_x[:, x_start:x_end+1] = True                       #x_end+1 = letzter Wert inkludiert

    mask_y = np.zeros((height, width), dtype=bool)          #Maske für die ausgewählten z-Werte
    mask_y[y_start:y_end+1, :] = True                       #+1, damit bei z_start=z_end eine Linie dargestellt wird

    color_alone = np.array([0, 70, 70], dtype=np.uint8)     #Einfärben der Bereiche
    color_overlap = np.array([255, 75, 75], dtype=np.uint8) #Überlappungen(tatsächlicher Bereich) wird rot geefärbt wie der Slider

    img[mask_x] = color_alone
    img[mask_y] = color_alone
    img[mask_x & mask_y] = color_overlap
    
    # Bild anzeigen
    st.image(img, caption=f"Ausgewählter Bereich: x: {start_force_length}-{end_force_length} + y: {start_force_width}-{end_force_width}")
