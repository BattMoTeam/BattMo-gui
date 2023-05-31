import os
from PIL import Image
import streamlit as st

##############################
# Page Config
path_to_images = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../resources', 'images')
st.set_page_config(
    page_title="BattMo",
    page_icon=Image.open(os.path.join(path_to_images, "battmo_logo.png"))
)
##############################

# set config before import to avoid streamlit error
from app_controller import set_heading


def run_app():
    set_heading()


if __name__ == "__main__":
    run_app()
