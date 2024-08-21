import streamlit as st
import os
from streamlit_option_menu import option_menu
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

with st.sidebar:

    st.text("")
    st.text("")
    st.text("")
    page = option_menu(
        "Main menu",
        ["Home", "Simulation", "Results", "Materials and models"],
        icons=['house', 'cloud-upload', "list-task", 'gear'],
        menu_icon="cast",
        default_index=0,
    )


# home_page = st.Page("pages/Home.py", title="Home", default=True)  # , icon="🏠")

# simulation_page = st.Page("pages/Simulation.py", title="Simulation")  # , icon="🔋")

# results_page = st.Page("pages/Results.py", title="Results")  # , icon="📈")

# materials_models_page = st.Page(
#     "pages/Materials_and_models.py", title="Materials and models"
# )  # , icon="🍪")

if page == "Home":

    # selected = option_menu(
    #     "Home",
    #     ["Home", 'Settings'],
    #     icons=['house', 'gear'],
    #     menu_icon="cast",
    #     default_index=1,
    # )

    # if selected == "Home":
    pg.show_home()

    # streamlit_nav = st.navigation(
    #     pages=[
    #         home_page,
    #     ]
    # )
elif page == "Simulation":

    selected = option_menu(
        None,
        ["Build cell", 'Simulate'],
        icons=['house', 'gear'],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
    )

    # col1, col2, col3 = st.columns((0.5, 6, 0.5))
    if selected == "Build cell":
        # with col2:
        pg.show_build_cell()

    elif selected == "Simulate":
        # with col2:

        pg.show_simulate()

    # streamlit_nav = st.navigation(
    #     pages=[
    #         simulation_page,
    #     ]
    # )
elif page == "Results":

    selected = option_menu(
        None,
        ["Analyse", 'Report'],
        icons=['house', 'gear'],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
    )

    if selected == "Analyse":
        pg.show_results()

    # streamlit_nav = st.navigation(
    #     pages=[
    #         results_page,
    #     ]
    # )
elif page == "Materials and models":

    selected = option_menu(
        None,
        ["Materials and models", 'Extra'],
        icons=['house', 'gear'],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
    )

    if selected == "Materials and models":
        pg.show_materials_and_models()

    # streamlit_nav = st.navigation(
    #     pages=[
    #         materials_models_page,
    #     ]
    # )
# streamlit_nav.run()
