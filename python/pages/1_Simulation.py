import os
import sys
from PIL import Image
import streamlit as st
import pprint
import pdb
import pickle
import json
import numpy as np

##############################
# Page Config
path_to_python_dir = os.path.dirname(os.path.abspath(__file__))
path_to_images = os.path.join(os.path.dirname(path_to_python_dir), 'resources', 'images')
st.set_page_config(
    page_title="BattMo",
    page_icon=Image.open(os.path.join(path_to_images, "battmo_logo.png"))
)
##############################

# set config before import to avoid streamlit error
sys.path.insert(0, path_to_python_dir)
from app_controller import get_app_controller
from resources.db import db_helper, db_access

##############################
# Remember user changed values when switching between pages
for k, v in st.session_state.items():
    st.session_state[k] = v

# Remember widget actions when switching between pages (for example: selectbox choice)
st.session_state.update(st.session_state)
##############################



def run_page():

    if "sim_finished" not in st.session_state:
        st.session_state.sim_finished = False

    if "update_par" not in st.session_state:
        st.session_state.update_par = False

    app = get_app_controller()

    model_id = app.set_model_choice().selected_model

    gui_parameters = app.set_tabs(model_id).user_input

    
    
    

    app.save_parameters(gui_parameters)

    if st.session_state.sim_finished:

        # retrieve saved parameters from json file
        with open(db_access.get_path_to_battmo_formatted_input()) as json_gui_parameters:
            gui_parameters = json.load(json_gui_parameters)

        
        #gui_file_data = json.dumps(gui_parameters, indent=2)

        N = gui_parameters["TimeStepping"]["N"]

        # Retrieve latest results
        with open(os.path.join(db_access.get_path_to_python_dir(), "battmo_result"), "rb") as pickle_result:
            result = pickle.load(pickle_result)

        [
            log_messages,
            number_of_states,
            cell_voltage,
            cell_current,
            time_values,
            negative_electrode_grid,
            electrolyte_grid,
            positive_electrode_grid,
            negative_electrode_concentration,
            electrolyte_concentration,
            positive_electrode_concentration,
            negative_electrode_potential,
            electrolyte_potential,
            positive_electrode_potential

        ] = result 

        print("time = ",number_of_states)
        save_run = st.empty()
        if len(log_messages) > 1:
            c = save_run.container()
            if number_of_states[0] >= N:
                

                c.success("Simulation finished successfully, but some warnings were produced. See the logging below for the warnings and check the results on the next page.")

            else:
                c.success("Simulation did not finish, some warnings were produced. See the logging below for the warnings.")
            
            c.markdown("***Logging:***")
                
            log_message = ''' \n'''
            for message in log_messages:
                log_message = log_message + message+ '''\n'''
            
            c.code(log_message + ''' \n''')

        else:    
            save_run.success("Simulation finished successfully! Check the results by clicking 'Plot latest results'.")


    # pp = pprint.PrettyPrinter(indent=2)
    # pp.pprint(gui_parameters)
    # pdb.set_trace()
    st.divider()
    app.run_simulation()


if __name__ == "__main__":
    run_page()
