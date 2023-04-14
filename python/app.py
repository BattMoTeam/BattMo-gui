import os
from PIL import Image
import streamlit as st

##############################
# Page Config
path_to_images = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'images')
st.set_page_config(
    page_title="BattMo",
    page_icon=Image.open(os.path.join(path_to_images, "battmo_logo.png"))
)
##############################

# set config before import to avoid streamlit error
from app_controller import *


def run_app():

    app = get_app_controller()

    set_heading()
    model_id = app.set_model_choice().selected_model
    gui_parameters = app.set_tabs(model_id).user_input
    # battmo_parameters = app.match_json(gui_parameters)

    app.set_json_viewer(gui_parameters, "GUI output")
    # app.set_json_viewer(battmo_parameters, "BattMo input")
    app.submit(gui_parameters, gui_parameters)


if __name__ == "__main__":
    run_app()
