import os
import sys
from PIL import Image
import streamlit as st

##############################
# Page Config
path_to_python_dir = os.path.dirname(os.path.abspath(__file__))
path_to_images = os.path.join(path_to_python_dir, 'resources', 'images')
st.set_page_config(
    page_title="BattMo",
    page_icon=Image.open(os.path.join(path_to_images, "battmo_logo.png"))
)
##############################

# set config before import to avoid streamlit error
sys.path.insert(0, path_to_python_dir)
from app_controller import get_app_controller

##############################
# Remember user changed values when switching between pages
for k, v in st.session_state.items():
    st.session_state[k] = v

#Remember widget actions when switching between pages (for example: selectbox choice)
st.session_state.update(st.session_state)
##############################



def run_page():

    app = get_app_controller()

    model_id = app.set_model_choice().selected_model

    #basis, advanced = app.get_tab_data(model_id)

    app.set_basis_input_tabs()

    advanced_input = st.checkbox(
        label ="Show advanced parameter input",
        key = "AdvancedInput")
    
    if advanced_input:
        gui_parameters = app.set_tabs(model_id).user_input

    #app.save_parameters(gui_parameters)


if __name__ == "__main__":
    run_page()
