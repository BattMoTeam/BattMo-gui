import os
import pickle
import io
import h5py
import numpy as np
from PIL import Image
import streamlit as st

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
import database.db_helper, app_scripts.app_access


def run_page():

    app = get_app_controller()

    if st.session_state.succes == True:
        results = get_results_data().get_results_data()    

        app.set_download_hdf5_button(results)

        app.set_graphs(results)

    else:
        st.error("Your simulation was not succesful, give it another try.")


if __name__ == "__main__":
    run_page()
