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
# Remember user changed values
for k, v in st.session_state.items():
    st.session_state[k] = v

#Remember widget actions when switching between pages (for example: selectbox choice)
st.session_state.update(st.session_state)
##############################

from app_controller import get_results_data, get_app_controller


def run_page():

    app = get_app_controller()

    results = get_results_data().get_results_data()

    app.set_download_hdf5_button(results)

    app.set_graphs(results)


if __name__ == "__main__":
    run_page()
