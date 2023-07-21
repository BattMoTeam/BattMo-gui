import os
import sys
import json
from PIL import Image
import streamlit as st

##############################
# Page Config
path_to_python_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path_to_images = os.path.join(path_to_python_dir, 'resources', 'images')
st.set_page_config(
    page_title="BattMo",
    page_icon=Image.open(os.path.join(path_to_images, "battmo_logo.png")),
    layout="wide"
)
##############################

# set config is done before import to avoid streamlit error
sys.path.insert(0, path_to_python_dir)
from app_controller import get_app_controller
from resources.db import db_access

##############################
# Remember user changed values
for k, v in st.session_state.items():
    st.session_state[k] = v
##############################



def run_page():
   
   
    app = get_app_controller()

    with open(db_access.get_path_to_battmo_input()) as json_gui_parameters:
        gui_parameters = json.load(json_gui_parameters)
    battmo_parameters = app.match_json(gui_parameters)

    app.set_json_viewer(gui_parameters, "Json LD format")
    app.set_json_viewer(battmo_parameters, "BattMo format")

    app.run_simulation()


if __name__ == "__main__":
    run_page()
