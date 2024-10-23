import streamlit as st
import sys
import os
from streamlit_extras.stylable_container import stylable_container

# set config before import to avoid streamlit error
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app_scripts.app_controller import get_app_controller, log_memory_usage, set_acknowlegent_info
from app_scripts import app_view, app_access


def show_cell_design():

    gui_parameters = st.session_state.json_linked_data_input
    app = get_app_controller()

    with stylable_container(
        key="indicator_container",
        css_styles="""
            {
                background-color: #F0F0F0;
                color: white;
                # border-radius: 20px;
            }
            """,
    ):

        cont2 = st.container()

    with cont2:
        st.text("")

        page_name = "Cell_design"
        app.set_indicators(page_name)

    with stylable_container(
        key="green_button",
        css_styles="""
            {
                background-color: #FFFFFF;
                color: white;
                # border-radius: 20px;
            }
            """,
    ):

        cont1 = st.container()

    _, col1, _ = cont1.columns((0.5, 1.5, 0.5))

    with col1:
        st.text("")
        app.set_geometry_visualization(gui_parameters)
        st.text("")
