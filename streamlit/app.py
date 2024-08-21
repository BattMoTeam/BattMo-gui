import streamlit as st
import os
from streamlit_navigation_bar import st_navbar
import pages as pg
from PIL import Image


##############################
# Page Config

st.set_page_config(
    page_title="BattMo",
    page_icon=Image.open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "battmo_logo.png")
    ),
    layout="wide",
)


st.logo(os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "battmo_logo.png"))

##############################
# Remember user changed values
for k, v in st.session_state.items():
    st.session_state[k] = v
##############################


home_page = st.Page("pages/Home.py", title="Home", default=True)  # , icon="🏠")

simulation_page = st.Page("pages/Simulation.py", title="Simulation")  # , icon="🔋")

results_page = st.Page("pages/Results.py", title="Results")  # , icon="📈")

materials_models_page = st.Page(
    "pages/Materials_and_models.py", title="Materials and models"
)  # , icon="🍪")


streamlit_nav = st.navigation(
    pages=[home_page, simulation_page, results_page, materials_models_page]
)

streamlit_nav.run()
