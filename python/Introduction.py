import os
from PIL import Image
import streamlit as st
from streamlit_extras.switch_page_button import switch_page


##############################
# Page Config
path_to_images = os.path.join(os.path.abspath(__file__), '../resources', 'images')
st.set_page_config(
    page_title="BattMo",
    page_icon=Image.open(os.path.join(path_to_images, "battmo_logo.png"))
)

##############################
# Remember user changed values
for k, v in st.session_state.items():
    st.session_state[k] = v
##############################


# set config is done before import to avoid streamlit error
from app_controller import set_heading

def set_external_links():
        # External links
        website_col, doi_col, github_col = st.columns([2, 3, 4])
        website_col.markdown("[BatteryModel.com](https://batterymodel.com/)")
        doi_col.markdown("[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6362783.svg)](https://doi.org/10.5281/zenodo.6362783)")
        github_col.markdown("[![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/BattMoTeam/BattMo)")

def run_app():
    set_heading()

    st.info("Hover over the following buttons to see what you can find on each page.")

    simulation_page = st.button(label = "Simulation",
                     help = "Define your input parameters and run a simulation."
                     )
    
    results_page = st.button(label = "Results",
                     help = "Download and visualize your results."
                     )
    
    materials_and_models_page = st.button(label = "Materials and models",
                     help = "See which pre-defined materials and which simulation models are available."
                     )
    
    
    if simulation_page:
        switch_page("Simulation")

    if results_page:
        switch_page("Results")

    if materials_and_models_page:
        switch_page("Materials and models")
    
    # st.markdown(" ")
    # st.divider()
    # st.text("""BattMo is a framework for continuum modeling of electrochemical devices. It simulates the Current-Voltage response of a battery using Physics-based
    #         models.""")   
    # #set_external_links()
    # st.divider()


if __name__ == "__main__":
    run_app()
