import os
from PIL import Image
import streamlit as st
import sys




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
    
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# set config is done before import to avoid streamlit error
from app_scripts.app_controller import set_heading, set_page_navigation, set_external_links, set_acknowlegent_info

def run_app():

    #Set Introduction page heading wil title, BattMo logo, and BattMo info.
    set_heading()

    pages, funding = st.columns(2)
    #Set page navigation
    set_page_navigation(pages)

    #Set funding acknowledgement
    set_acknowlegent_info(funding)

    #Set external links to websites and documentation 
    set_external_links()

if __name__ == "__main__":
    run_app()
