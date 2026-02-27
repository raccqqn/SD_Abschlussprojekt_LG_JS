import streamlit as st
from src.beamBuilder2D import BeamBuilder2D
from src.bodyBuilder3D import BodyBuilder3D

def build_structure_from_session_states():                   #Objekt wird gebaut
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

