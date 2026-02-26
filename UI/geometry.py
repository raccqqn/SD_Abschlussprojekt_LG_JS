import streamlit as st
from src.beamBuilder2D import BeamBuilder2D
from src.bodyBuilder3D import BodyBuilder3D

def apply_support_forces(builder):                          #Die Freiheitsgrade und Kräfte werden der Builder Klasse übergeben
    for pos, s in st.session_state["supports"].items():
        builder.fix_node(pos, s["mask"])

    for pos, f in st.session_state["forces"].items():
        builder.apply_force(pos, f["vec"] )

def build_structure_from_session_states():                     #Objekt wird gebaut
    length = st.session_state["length"]
    width = st.session_state["width"]
    depth = st.session_state["depth"]
    ea = st.session_state["EA"]

    if depth > 1:                                           #Bauen des 3d Modells
        bld = BodyBuilder3D(length, width, depth, ea)
        bld.create_geometry()
        body = bld.build()
        body.assemble()
        return body
    
    else:                                                  #Bauen des 2d Models
        bld = BeamBuilder2D(length, width, ea)
        bld.create_geometry()
        beam = bld.build()
        beam.assemble()
        return beam

def build_structure_with_support_forces():                  #Objekt wird gebaut - aber noch aus session_states
    length = st.session_state["length"]                     #Ja, wird hier aktuell noch aus den Session states komplett gebaut - wird geändert
    width = st.session_state["width"]
    depth = st.session_state["depth"]
    ea = st.session_state["EA"]

    if depth > 1:                                           #Bauen des 3d Modells
        bld = BodyBuilder3D(length, width, depth, ea)
        bld.create_geometry()
        apply_support_forces(bld)
        body = bld.build()
        body.assemble()
        return body
    
    else:                                                  #Bauen des 2d Models
        bld = BeamBuilder2D(length, width, ea)
        bld.create_geometry()
        apply_support_forces(bld)
        beam = bld.build()
        beam.assemble()
        return beam