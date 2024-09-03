import streamlit as st
import numpy as np
from PIL import Image
import os
import sys
import html
import json
import sympy as sp


# ##############################
# # Page Config
# path_to_images = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")
# st.set_page_config(
#     page_title="BattMo",
#     page_icon=Image.open(os.path.join(path_to_images, "battmo_logo.png")),
#     layout="wide",
# )
# ##############################

# ##############################
# # Remember user changed values
for k, v in st.session_state.items():
    st.session_state[k] = v

# Remember widget actions when switching between pages (for example: selectbox choice)
st.session_state.update(st.session_state)
# ##############################

# set config is done before import to avoid streamlit error
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app_scripts import app_access, app_view

from app_scripts.app_controller import (
    set_model_description,
    set_material_description,
    set_acknowlegent_info,
)


# def show_materials_and_models():
st.text("")
st.text("")
set_model_description()

set_material_description()

with st.sidebar:
    app_view.st_space(space_width=3)
    set_acknowlegent_info()
