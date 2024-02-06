import os
from PIL import Image
import streamlit as st




##############################
# Page Config

st.set_page_config(
    page_title="BattMo",
    page_icon=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"images", "battmo_logo.png"))
)

##############################
# Remember user changed values
for k, v in st.session_state.items():
    st.session_state[k] = v
##############################


# set config is done before import to avoid streamlit error
from app_scripts.app_controller import set_heading, set_page_navigation, set_external_links

def run_app():

    #Set Introduction page heading wil title, BattMo logo, and BattMo info.
    set_heading()

    #Set page navigation
    set_page_navigation()

    #Set external links to websites and documentation 
    set_external_links()

if __name__ == "__main__":
    run_app()
