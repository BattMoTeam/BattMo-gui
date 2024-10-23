import streamlit as st
import os
from streamlit_option_menu import option_menu
import app_pages as pg
from PIL import Image
from app_scripts import app_access

# from streamlit_extras.container import style_container


##############################
# Page Config

st.set_page_config(
    page_title="BattMo",
    page_icon=Image.open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "battmo_logo.png")
    ),
    layout="wide",
)

##############################
# Remember user changed values
for k, v in st.session_state.items():
    st.session_state[k] = v
##############################

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


# home_page = st.Page("app_pages/Home.py", title="Home", default=True)  # , icon="🏠")

# simulation_page = st.Page("app_pages/Simulation.py", title="Simulation")  # , icon="🔋")

# results_page = st.Page("app_pages/Results.py", title="Results")  # , icon="📈")

# materials_models_page = st.Page(
#     "app_pages/Materials_and_models.py", title="Materials and models"
# )  # , icon="🍪")


# streamlit_nav = st.navigation(
#     pages=[home_page, simulation_page, results_page, materials_models_page]
# )

# streamlit_nav.run()
with st.sidebar:
    page = option_menu(
        None,
        ["Home", "Simulation", "Results", "Materials and models"],
        icons=['house', 'cloud-upload', "list-task", 'gear'],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"background-color": "transparent"},
        },
    )

if page == "Simulation":

    bar = option_menu(
        None,
        ["Cel design", 'Simulation setup'],
        icons=['house', 'gear'],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
    )

    if bar == "Cel design":
        pg.show_cell_design()
    elif bar == "Simulation setup":
        pg.show_simulation()


if "theme" not in st.session_state:
    st.session_state.theme = False

with st.sidebar:

    theme = st.toggle(
        "Dark theme",
    )

    st.session_state.theme = theme

    # style_container()


if theme == True:
    st.markdown(
        """
    <style>
    body {
        background-color: #ED820E;
        color: white;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
elif theme == False:
    st.markdown(
        """
    <style>
    body {
        background-color: #ffffff;
        color: black;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
