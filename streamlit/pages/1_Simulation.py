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
from database import db_helper
from app_scripts import app_access

##############################
# Remember user changed values when switching between pages
for k, v in st.session_state.items():
    st.session_state[k] = v

# Remember widget actions when switching between pages (for example: selectbox choice)
st.session_state.update(st.session_state)
##############################


# Get page name
url = str(st_javascript("await fetch('').then(r => window.parent.location.href)"))
page_name = url.rsplit('/',1)[1]


def run_page():

    if "sim_finished" not in st.session_state:
        st.session_state.sim_finished = False

    if "update_par" not in st.session_state:
        st.session_state.update_par = False

    if "succes" not in st.session_state:
        st.session_state.succes = None


    log_memory_usage()

    app = get_app_controller()

    model_id = app.set_model_choice().selected_model

    gui_parameters = app.set_tabs(model_id).user_input

    app.set_indicators(page_name)

    st.divider()

    app.download_parameters(gui_parameters)

    
    app.run_simulation(gui_parameters)


    app.divergence_check()


    


    ############################################
    # Can be used to check the structure of gui_parameters in the terminal
    # pp = pprint.PrettyPrinter(indent=2)
    # pp.pprint(gui_parameters)
    # pdb.set_trace()
    ############################################
    
    
    


if __name__ == "__main__":
    run_page()
