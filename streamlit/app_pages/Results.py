import os
import pickle
import io
import h5py
import numpy as np
from PIL import Image
import streamlit as st
import time
from queue import Queue
import sys
import uuid
import tempfile
import shutil


# ##############################
# # Page Config
# path_to_images = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")
# st.set_page_config(
#     page_title="BattMo",
#     page_icon=Image.open(os.path.join(path_to_images, "battmo_logo.png")),
#     layout="wide",
# )

##############################
# # Remember user changed values
for k, v in st.session_state.items():
    st.session_state[k] = v

# Remember widget actions when switching between pages (for example: selectbox choice)
st.session_state.update(st.session_state)
##############################
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app_scripts.app_controller import (
    get_app_controller,
    get_results_data,
    set_acknowlegent_info,
)
from app_scripts import app_view

# Get page name
# url = str(st_javascript("await fetch('').then(r => window.parent.location.href)"))
# url_parts = url.rsplit('/',1)

# if len(url_parts) > 1:
#     # Extract the page name from the last part
#     page_name = url_parts[1]
# else:
#     # Handle the case where '/' is not found in the URL
#     page_name = "Unknown"


##############################
# Remember user changed values
# for k, v in st.session_state.items():
#     st.session_state[k] = v

# Remember widget actions when switching between pages (for example: selectbox choice)
# st.session_state.update(st.session_state)
##############################


# def show_results():

st.text("")
st.text("")
page_name = "Results"

if "success" not in st.session_state:
    st.session_state.success = None

if "transfer_results" not in st.session_state:
    st.session_state.transfer_results = None

if "hdf5_upload" not in st.session_state:
    st.session_state.hdf5_upload = None

# Generate a unique identifier for the session
if "unique_id_temp_folder" not in st.session_state:
    st.session_state["unique_id_temp_folder"] = str(uuid.uuid4())

if "temp_dir" not in st.session_state:
    unique_id = st.session_state["unique_id_temp_folder"]
    # Create a temporary directory for the session
    temp_dir = tempfile.mkdtemp(prefix=f"session_{unique_id}_")

    # Store the temp_dir in session state
    st.session_state["temp_dir"] = temp_dir

if "selected_data" not in st.session_state:
    st.session_state["selected_data"] = None

app = get_app_controller()

app.set_hdf5_upload().set_results_uploader()
selected_data_sets = app.set_data_set_selector().set_selector()

if (
    st.session_state.transfer_results == True
    or st.session_state.hdf5_upload == True
    or selected_data_sets
):
    session_temp_folder = st.session_state["temp_dir"]
    file_names = [
        f
        for f in os.listdir(session_temp_folder)
        if os.path.isfile(os.path.join(session_temp_folder, f))
    ]
    # st.divider()

    # app_view.st_space(space_number=1)
    if selected_data_sets:

        results, indicators, input_files = get_results_data(selected_data_sets).get_results_data(
            selected_data_sets
        )

        if len(selected_data_sets) <= 1:
            results = results[0]
            indicators = indicators[0]

        app.set_indicators(page_name, indicators, selected_data_sets)

        app.set_graphs(results, selected_data_sets)

        app_view.st_space(space_number=1)

        app.set_download_hdf5_button(results, selected_data_sets)
    elif file_names:
        last_file_name = file_names[-1]
        st.session_state["selected_data"] = last_file_name
        selected_data_sets = last_file_name

        results, indicators, input_files = get_results_data(last_file_name).get_results_data(
            last_file_name
        )

        app.set_indicators(page_name, indicators, last_file_name)

        app.set_graphs(results, selected_data_sets)

        app_view.st_space(space_number=1)

        app.set_download_hdf5_button(results, selected_data_sets)

elif st.session_state.success == None:
    st.error(
        "You have not executed a simulation yet. Go to the 'Simulation' page to run a simulation or upload your previous results to visualize them."
    )

elif (
    st.session_state.success == False
    and st.session_state.transfer_results == False
    and not selected_data_sets
):
    st.error("Your simulation was not succesful unfortunately, give it another try.")

with st.sidebar:
    st.divider()
    set_acknowlegent_info()
