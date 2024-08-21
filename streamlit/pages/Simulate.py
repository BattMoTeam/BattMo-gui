import streamlit as st
import json
import sys
import os


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app_scripts.app_controller import get_app_controller, log_memory_usage, set_acknowlegent_info
from app_scripts import app_view, app_access


def show_simulate():

    app = get_app_controller()

    with open(app_access.get_path_to_linked_data_input()) as f:
        gui_parameters = json.load(f)

    success = app.run_simulation(gui_parameters).success

    app.download_parameters(gui_parameters)

    save_run = st.container()
    app.divergence_check(save_run, st.session_state.success)

    if st.session_state.success and st.session_state.transfer_results:
        st.session_state["toast"](
            ":green-background[Find your results on the results page!]", icon="✅"
        )
        st.session_state.success = False

    st.session_state.response = None
