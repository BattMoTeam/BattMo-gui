import streamlit as st
import numpy as np
import os
import sys
from streamlit_toggle_component.src.st_toggle_component import st_toggle_component

##############################
# Remember user changed values
for k, v in st.session_state.items():
    st.session_state[k] = v
##############################

# set config is done before import to avoid streamlit error
path_to_python_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, path_to_python_dir)

from resources.db import db_access, db_helper


models_as_dict = db_helper.get_models_as_dict()
P2D_model= db_helper.get_model_parameters_as_dict(1)
P2D_model_description = db_helper.get_model_description("P2D")[0][0]
st.write(P2D_model_description)







st.title("The available models")

model = st.expander("P2D")

with model:
    
    st.markdown("""Includes : """)
    st.markdown("- Thermal effects = " + str(P2D_model[0]["value"]["hasStringData"]))
    st.markdown("- Current collector = " + str(P2D_model[1]["value"]["hasStringData"]))
    st.markdown("- Solid Diffusion model = " + str(P2D_model[2]["value"]["hasStringData"]))
    st.markdown("- Solid Diffusion model type = " + str(P2D_model[3]["value"]["hasStringData"]))


    st.markdown("Description = " + P2D_model_description)

st.title("The available materials")

material = st.expander("Material")

