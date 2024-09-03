import os
import sys
from PIL import Image
import streamlit as st
import pprint
import pdb
import pickle
import json
import numpy as np
import tempfile
import uuid
import h5py
from streamlit_extras.stylable_container import stylable_container


# ##############################
# # Page Config
# path_to_images = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")
# st.set_page_config(
#     page_title="BattMo",
#     page_icon=Image.open(os.path.join(path_to_images, "battmo_logo.png")),
# )
# ##############################

# set config before import to avoid streamlit error
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app_scripts.app_controller import get_app_controller, log_memory_usage, set_acknowlegent_info
from app_scripts import app_view, app_access


# with open(app_access.get_path_to_custom_style_css()) as f:
#     style = st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

##############################
# Remember user changed values when switching between pages
for k, v in st.session_state.items():
    st.session_state[k] = v

# Remember widget actions when switching between pages (for example: selectbox choice)
st.session_state.update(st.session_state)
##############################


# JSON file session states

if "json_uploaded_input" not in st.session_state:
    st.session_state.json_uploaded_input = {}

if "json_battmo_formatted_input" not in st.session_state:
    st.session_state.json_battmo_formatted_input = {}

if "json_linked_data_input" not in st.session_state:
    st.session_state.json_linked_data_input = {}

if "json_gui_calculated_quantities" not in st.session_state:
    st.session_state.json_gui_calculated_quantities = {}

if "json_indicator_quantities" not in st.session_state:
    st.session_state.json_indicator_quantities = {}

# Other session states

if "sim_finished" not in st.session_state:
    st.session_state.sim_finished = False

if "update_par" not in st.session_state:
    st.session_state.update_par = False

if "success" not in st.session_state:
    st.session_state.success = None

if "transfer_results" not in st.session_state:
    st.session_state.transfer_results = None

if "simulation_uuid" not in st.session_state:
    st.session_state.simulation_uuid = None

if "simulation_results" not in st.session_state:
    st.session_state.simulation_results = None

if "simulation_progress" not in st.session_state:
    st.session_state.simulation_progress = 0

if "response" not in st.session_state:
    st.session_state.response = None

if "upload" not in st.session_state:
    st.session_state.upload = None

if "clear_upload" not in st.session_state:
    st.session_state.clear_upload = None

if "theme" not in st.session_state:
    st.session_state.theme = None

if "simulation_results_file_name" not in st.session_state:
    st.session_state.simulation_results_file_name = None

# Generate a unique identifier for the session
if "unique_id_temp_folder" not in st.session_state:
    st.session_state["unique_id_temp_folder"] = str(uuid.uuid4())

if "temp_dir" not in st.session_state:
    unique_id = st.session_state["unique_id_temp_folder"]
    # Create a temporary directory for the session
    temp_dir = tempfile.mkdtemp(prefix=f"session_{unique_id}_")
    # Store the temp_dir in session state
    st.session_state["temp_dir"] = temp_dir

if "toast" not in st.session_state:
    st.session_state["toast"] = st.toast

if "gui_schema" not in st.session_state:
    st.session_state.gui_schema = None

if "number_of_states" not in st.session_state:
    st.session_state.number_of_states = None

if "log_messages" not in st.session_state:
    st.session_state.log_messages = None

if "stop_simulation" not in st.session_state:
    st.session_state.stop_simulation = None

page_name = "Simulation"

log_memory_usage()

app = get_app_controller()

model_id = app.set_model_choice().selected_model

# if st.session_state.success and st.session_state.transfer_results:
#     st.session_state["toast"](":green-background[Gathering the results!]", icon="💤")

gui_parameters = app.set_tabs(model_id).user_input

app.set_indicators(page_name)
# st.divider()

app.set_geometry_visualization(gui_parameters)

app.download_parameters(gui_parameters)

success = app.run_simulation(gui_parameters).success

if st.session_state.sim_finished == True:

    # with h5py.File(app_access.get_path_to_battmo_results(), "r") as f:
    #     data = f

    save_run = st.container()
    app.divergence_check(save_run, True)

if st.session_state.success and st.session_state.transfer_results:
    # st.session_state["toast"](
    #     ":green-background[Find your results on the results page!]", icon="✅"
    # )
    st.session_state.success = None
    st.session_state.sim_finished = None


st.session_state.response = None

with st.sidebar:
    # app_view.st_space(space_width=3)

    st.divider()
    set_acknowlegent_info()

############################################
# Can be used to check the structure of gui_parameters in the terminal
# pp = pprint.PrettyPrinter(indent=2)
# pp.pprint(gui_parameters)
# pdb.set_trace()
############################################
