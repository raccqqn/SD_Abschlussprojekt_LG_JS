import streamlit as st
from beamBuilder2D import BeamBuilder2D
from bodyBuilder3D import BodyBuilder3D

def apply_support_forces(builder):                          #Die Freiheitsgrade und Kräfte werden der Builder Klasse übergeben
    for pos, s in st.session_state["supports"].items():
        builder.fix_node(pos, s["mask"])

    for pos, f in st.session_state["forces"].items():
        builder.apply_force(pos, f["vec"] )

def build_object():                                         #Objekt wird gebaut
    length = st.session_state["length"]
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
    




    