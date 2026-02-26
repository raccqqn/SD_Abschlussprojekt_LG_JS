import streamlit as st
import numpy as np
from UI.state import init_max_values, init_all_y_values_values
from src.structureManager import StructureManager 
from datetime import datetime

def ui_storage_sidebar():
    """Sidebar zum Speichern einer Struktur"""
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
    Automatischer Sidebar vom /pages Ordner wird deaktiviert und mit einem selber erstellen erstzt.
    Dadurch werden manche Pages je nach Bedingung ausgegraut. 
    """
    st.sidebar.divider()
    st.sidebar.subheader("Navigation")
    with st.sidebar:
        if st.button("Zur Startseite", width = "stretch"):
            st.session_state["confirm_reset"] = True
        st.caption("_Neue Struktur erstellen, aktuelle wird verworfen!_", text_alignment="center")
    
        #Wenn reset noch nicht bestätigt wurde: confirm True!
        confirm = st.session_state.get("confirm_reset", False)
        
        if confirm:
            st.warning("Die aktuelle Struktur wird gelöscht! Fortfahren?")
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
                    #Sonst muss Button 2 mal geklickt werden
                    st.rerun()


def ui_pages_sidebar_from_structure():
    with st.sidebar:
        
        #st.page_link("Startseite.py", label = "Startseite", width = "stretch", disabled = True)
        st.page_link("pages/1_Grundmaße.py", label = "Grundmaße", disabled=True)   
        st.page_link("pages/2_Festlager_und_Kräfte.py", label = "Lager und Kräfte")
        st.page_link("pages/3_Optimierer.py", label = "Optimierung")

def sync_session_state_with_struc(structure):
    
    #UI-Attribute aktualisieren
    st.session_state["length"] = structure.length
    st.session_state["width"]  = structure.width
    st.session_state["depth"]  = structure.depth
    st.session_state["EA"]     = structure.EA
    st.session_state["dim"]    = structure.dim

    #UI Input-Felder aktualisieren
    st.session_state["ui_length"] = structure.length
    st.session_state["ui_width"]  = structure.width
    st.session_state["ui_depth"]  = structure.depth
    st.session_state["ui_EA"]     = structure.EA

    #Lagerungen und Kräfte abrufen, speichern
    st.session_state["supports"] = structure.get_supports()
    st.session_state["forces"]   = structure.get_forces()

    #Objekt selbst speichern
    st.session_state["structure"] = structure

def sync_ui_values():                                               #Session_States eingaben aktualisieren: 
    st.session_state["length"] = st.session_state["ui_length"]      #2 unterschiedliche ses-stat, damit im Eingabefeld immer der aktuelle Wert steht.
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
                for i in range(st.session_state["width"]):                              #Iterieren über die ganze Breite
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

#def update_structure():
#    struc = st.session_state.get("structure")
 #   struc.update_force()
  #  struc.update_fixings()
   # struc.assign_dofs()
    #struc.assemble()
    #return struc