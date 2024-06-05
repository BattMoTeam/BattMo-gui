import os
import sys
from PIL import Image
import streamlit as st
from streamlit_javascript import st_javascript
import pprint
import pdb
import pickle
import json
import numpy as np
from streamlit_theme import st_theme
import tempfile
import uuid


##############################
# Page Config
path_to_images = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"images")
st.set_page_config(
    page_title="BattMo",
    page_icon=Image.open(os.path.join(path_to_images, "battmo_logo.png"))
)
##############################

# set config before import to avoid streamlit error
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app_scripts.app_controller import get_app_controller, log_memory_usage


# Get page name
url = str(st_javascript("await fetch('').then(r => window.parent.location.href)"))
url_parts = url.rsplit('/',1)

if len(url_parts) > 1:
    # Extract the page name from the last part
    page_name = url_parts[1]
else:
    # Handle the case where '/' is not found in the URL
    page_name = "Unknown"

if "sim_finished" not in st.session_state:
    st.session_state.sim_finished = False

if "update_par" not in st.session_state:
    st.session_state.update_par = False

if "success" not in st.session_state:
    st.session_state.success = None

if "response" not in st.session_state:
    st.session_state.response = None

if "upload" not in st.session_state:
    st.session_state.upload = None

if "theme" not in st.session_state:
    st.session_state.theme = None

if "simulation_results_file_name" not in st.session_state:
    st.session_state.simulation_results_file_name = None

# Generate a unique identifier for the session
if 'unique_id_temp_folder' not in st.session_state:
    st.session_state['unique_id_temp_folder'] = str(uuid.uuid4())

if 'temp_dir' not in st.session_state:
    unique_id = st.session_state['unique_id_temp_folder']
    # Create a temporary directory for the session
    temp_dir = tempfile.mkdtemp(prefix=f"session_{unique_id}_")
    # Store the temp_dir in session state
    st.session_state['temp_dir'] = temp_dir



def run_page():

    ##############################
    # Remember user changed values when switching between pages
    for k, v in st.session_state.items():
        st.session_state[k] = v

    # Remember widget actions when switching between pages (for example: selectbox choice)
    st.session_state.update(st.session_state)
    ##############################


    log_memory_usage()

    app = get_app_controller()

    model_id = app.set_model_choice().selected_model

    gui_parameters = app.set_tabs(model_id).user_input

    app.set_indicators(page_name)
    #st.divider()

    app.set_geometry_visualization(gui_parameters)


    app.download_parameters(gui_parameters)

    
    success = app.run_simulation(gui_parameters).success
    # st.session_state.succes = True
 
    app.divergence_check(success)


    


    ############################################
    # Can be used to check the structure of gui_parameters in the terminal
    # pp = pprint.PrettyPrinter(indent=2)
    # pp.pprint(gui_parameters)
    # pdb.set_trace()
    ############################################
    
    
    


if __name__ == "__main__":
    run_page()
