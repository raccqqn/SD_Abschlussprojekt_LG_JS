import streamlit as st
import numpy as np
import plotly.graph_objects as go

from bodyBuilder3D import BodyBuilder3D

st.set_page_config(page_title="SD_Abschlussprojekt", layout="wide")
st.title("SD_Abschlussprojekt")

def ui_geometry():                                  #Eingaben für die Basisgeometrie - später noch anpassen auf optisch schön.
    st.subheader("Form")

    col1, col2, col3, col4 = st.columns(4)                                          
    with col1: breite = st.number_input("Breite", min_value=1, value=3, step=1)            
    with col2: hoehe = st.number_input("Höhe", min_value=1, value=5, step =1 )
    with col3: tiefe = st.number_input("Tiefe", min_value=1, value = 1, step=1)
    with col4: ea = st.number_input("EA", min_value=1, value=1000, step = 1)
    return breite, hoehe, tiefe, ea

def build_body(breite, hoehe, tiefe, ea):                                                         

    builder = BodyBuilder3D(breite, hoehe, tiefe, ea)     #Werte von zuvor der BuilderClasse übergeben
    builder.create_geometry()
    return builder

def create_plot(builder):
    cords = np.array([data["cords"] for data in builder.nodes_data.values()], dtype= float) #Daten für die Knoten auslesen aus Klasse

    knoten = go.Scatter3d(                          #Knoten zeichnen
        x = cords[:,0],
        y = cords[:,1],
        z = cords[:,2],
        mode = "markers",
        marker = dict(size = 5, color="yellow"),
    )

    xl, yl, zl = [], [], []                         #Liste für die Linien erstellen

    for a, b in builder.elements:                   #Verbindungs Tuple werden wieder aufgerufen. Form:[(x,y,z), (x,y,z)]
        ca = builder.nodes_data[a]["cords"]
        cb = builder.nodes_data[b]["cords"]

        xl.extend((ca[0], cb[0], None))             #Linien definieren und zur Liste hinzufügen.
        yl.extend((ca[1], cb[1], None))             #Mittels extend als einzelne Werte hinzufügen (append machts als Tuple)
        zl.extend((ca[2], cb[2], None))

    federn = go.Scatter3d(                          #Linien zeichnen mittels Plotly in 3D
        x = xl, 
        y = yl,
        z = zl,
        mode = "lines",
        marker = dict(size = 1, color="white"),
    )

    fig = go.Figure([federn, knoten])               #Figure zeichnen 
    fig.update_layout(scene = dict(aspectmode="data"))
    return fig


def ui_festlager(builder, breite, hoehe, tiefe):    #Punkte für Festlager festlegen
    st.subheader("Festlager")

    if "festlager" not in st.session_state:         #Session State für Festlager festlegen
        st.session_state.festlager = []

    col1, col2, col3, col4 = st.columns(4)

    with col1: fix_x = st.number_input("x", min_value=0, max_value=breite-1, value=0, step=1)
    with col2: fix_y = st.number_input("y", min_value=0, max_value=hoehe-1, value=0, step=1)
    with col3: fix_z = st.number_input("z", min_value=0, max_value=tiefe-1, value=0, step=1)
    with col4:
        if st.button("Festlager hinzufügen"):
            pos = (int(fix_x), int(fix_y), int(fix_z))
            if pos in builder.nodes_data:
                if pos not in st.session_state.festlager:
                    st.session_state.festlager.append(pos)
            else:
                st.warning("Knoten nicht auswählbar.")

    with st.expander("Aktive Festlager"):
        st.write(st.session_state.festlager)
        if st.button("Alle Festlager löschen"):
            st.session_state.festlager = []


def apply_festlager(builder):
    for pos in st.session_state.get("festlager", []):
        builder.fix_node(pos, (True, True, True))           #In Maske die gewählten Knoten fixieren. 




# Ausführen der Funktionen im Main 
breite, hoehe, tiefe, ea = ui_geometry()
st.divider()

builder = build_body(breite, hoehe, tiefe, ea)

ui_festlager(builder, breite, hoehe, tiefe)
apply_festlager(builder)

fig = create_plot(builder)
st.plotly_chart(fig, use_container_width=True)