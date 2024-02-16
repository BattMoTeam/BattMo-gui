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
import juliacall as jl
import sys


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
url = st_javascript("await fetch('').then(r => window.parent.location.href)")
page_name = url.rsplit('/',1)[1]


def run_page():

    if "succes" not in st.session_state:
        st.session_state.succes = None

    app = get_app_controller()

    if st.session_state.succes == True:
        results = get_results_data().get_results_data()

        app.set_indicators(page_name)
        #st.divider()

        #app_view.st_space(space_number=1) 

        app.set_graphs(results)

        app_view.st_space(space_number=1)

        app.set_download_hdf5_button(results)

    elif st.session_state.succes == None:
        st.error("You have not executed a simulation yet. Go to the 'Simulation' page to run a simulation.")

    else: 
        st.error("Your simulation was not succesful unfortunately, give it another try.")


if __name__ == "__main__":
    run_page()
