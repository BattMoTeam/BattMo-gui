import streamlit as st
import numpy as np
from PIL import Image
import os
import sys
import html 
import json
import sympy as sp


##############################
# Page Config
path_to_images = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"images")
st.set_page_config(
    page_title="BattMo",
    page_icon=Image.open(os.path.join(path_to_images, "battmo_logo.png")),
    layout="wide"
)
##############################

##############################
# Remember user changed values
for k, v in st.session_state.items():
    st.session_state[k] = v
##############################

# set config is done before import to avoid streamlit error
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app_scripts.app_access

from app_scripts.app_controller import set_model_description, set_material_description

def run_page():

    set_model_description()

    set_material_description()
                    
if __name__ == "__main__":
    run_page()
                
