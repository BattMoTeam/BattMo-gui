import os
import pickle
import io
import h5py
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_javascript import st_javascript
import time
from queue import Queue
import sys
import uuid
import tempfile
import shutil


##############################
# Page Config
path_to_images = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"images")
st.set_page_config(
    page_title="BattMo",
    page_icon=Image.open(os.path.join(path_to_images, "battmo_logo.png")),
    layout="wide"
)

##############################
# Remember user changed values
for k, v in st.session_state.items():
    st.session_state[k] = v

#Remember widget actions when switching between pages (for example: selectbox choice)
st.session_state.update(st.session_state)
##############################
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app_scripts.app_controller import get_app_controller, get_results_data
from app_scripts import app_view

# Get page name
url = str(st_javascript("await fetch('').then(r => window.parent.location.href)"))
url_parts = url.rsplit('/',1)

if len(url_parts) > 1:
    # Extract the page name from the last part
    page_name = url_parts[1]
else:
    # Handle the case where '/' is not found in the URL
    page_name = "Unknown"


def run_page():

    ##############################
    # Remember user changed values
    for k, v in st.session_state.items():
        st.session_state[k] = v

    #Remember widget actions when switching between pages (for example: selectbox choice)
    st.session_state.update(st.session_state)
    ##############################

    if "succes" not in st.session_state:
        st.session_state.succes = None

    if "hdf5_upload" not in st.session_state:
        st.session_state.hdf5_upload = None

    # Generate a unique identifier for the session
    if 'unique_id_temp_folder' not in st.session_state:
        st.session_state['unique_id_temp_folder'] = str(uuid.uuid4())

    if 'temp_dir' not in st.session_state:
        unique_id = st.session_state['unique_id_temp_folder']
        # Create a temporary directory for the session
        temp_dir = tempfile.mkdtemp(prefix=f"session_{unique_id}_")

        st.write("Themp dir has been made: ", temp_dir)
        # Store the temp_dir in session state
        st.session_state['temp_dir'] = temp_dir
    
    if "selected_data" not in st.session_state:
        st.session_state["selected_data"] = None
    
    


    app = get_app_controller()

    if st.session_state.succes == True:
        results_simulation = get_results_data().get_results_data()

    results_uploaded = app.set_hdf5_upload().set_results_uploader()
    selected_data_sets = app.set_data_set_selector().set_selector()

    if st.session_state.succes == True or st.session_state.hdf5_upload == True:
        if st.session_state.succes == True:
            app.set_indicators(page_name, results_simulation)
        #st.divider()

        #app_view.st_space(space_number=1)
        if st.session_state.succes == True: 
            results = results_simulation
        else:
            results = results_uploaded
    
        app.set_graphs(results)

        app_view.st_space(space_number=1)

        if st.session_state.succes == True:
            app.set_download_hdf5_button(results_simulation)


    elif st.session_state.succes == None:
        st.error("You have not executed a simulation yet. Go to the 'Simulation' page to run a simulation or upload your previous results to visualize them.")

    else: 
        st.error("Your simulation was not succesful unfortunately, give it another try.")


if __name__ == "__main__":
    run_page()
