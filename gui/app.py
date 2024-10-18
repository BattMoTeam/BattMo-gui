import streamlit as st
import os
from streamlit_navigation_bar import st_navbar
import app_pages as pg
from PIL import Image
from app_scripts import app_access


##############################
# Page Config

st.set_page_config(
    page_title="BattMo",
    page_icon=Image.open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "battmo_logo.png")
    ),
    layout="wide",
)


st.logo(
    image=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "images", "battmo_logo_text.png"
    ),
    link="https://batterymodel.com/",
    icon_image=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "images", "battmo_logo.png"
    ),
    size="large",
)

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] img {
        width: 200px !important;  /* Adjust this value to your desired width */
        height: auto;  /* Maintain the aspect ratio */
        margin: 0 auto;  /* Center the logo */
        display: block;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

##############################
# Remember user changed values
for k, v in st.session_state.items():
    st.session_state[k] = v
##############################


home_page = st.Page("app_pages/Home.py", title="Home", default=True)  # , icon="🏠")

simulation_page = st.Page("app_pages/Simulation.py", title="Simulation")  # , icon="🔋")

results_page = st.Page("app_pages/Results.py", title="Results")  # , icon="📈")

materials_models_page = st.Page(
    "app_pages/Materials_and_models.py", title="Materials and models"
)  # , icon="🍪")


streamlit_nav = st.navigation(
    pages=[home_page, simulation_page, results_page, materials_models_page]
)

streamlit_nav.run()
