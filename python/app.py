import streamlit as st
from PIL import Image
import os
import json

from app_view import Heading, Tab, SubmitJob, ParametersForm
from app_model import LoaderJsons

THISDIR = os.path.realpath(os.path.dirname(__file__))  
 

######################################## INITIALIZATION FUNCTIONS ##################################

@st.cache
def load_images(cwd:str = THISDIR)-> dict:

    resources_dir = os.path.join(cwd, './resources/') 

    return {"logo":Image.open(resources_dir+"battmo_logo.png"), 
            "cell_coin":Image.open(resources_dir+"cell_coin.png"), 
            "cell_prismatic": Image.open(resources_dir+"cell_prismatic.png"),
            "cell_cylindrical":Image.open(resources_dir+"cell_cylindrical.png"),
            "plus": Image.open(resources_dir+"plus.png"),
            "minus": Image.open(resources_dir+"minus.png"),
            "elyte": Image.open(resources_dir+"elyte.png"),
            "current": Image.open(resources_dir+"current.png"),}


# @st.cache
def load_parameter_sets(cwd:str = THISDIR)-> dict:

    params_dir = os.path.join(cwd, './parameters/')

    available_params = LoaderJsons(location=params_dir)
    return available_params.conform_params_to_appmodel()


########    Inmutable dicts      ######
IMAGES_DICT = load_images()
DEFAULT_PARAMS = load_parameter_sets()



############################################# APP ################################################# 


Heading(IMAGES_DICT["logo"])

cell_tab, pe_tab, ne_tab, elyte_tab, cycling_tab = st.tabs(["Cell", "Positive Electrode", "Negative Electrode",
                                                            "Electrolyte", "Cycling Program"])

st.markdown("#") #space


with cell_tab:               

    Tab(IMAGES_DICT["cell_coin"], tab_title= "Cell")

    cell_selected_paramset = st.selectbox(label= "",
                                        options=list(DEFAULT_PARAMS.cell.keys()), #change with the model
                                        index=0,
                                        label_visibility="collapsed")
    cell_form = ParametersForm(label="cell", default_parameters=DEFAULT_PARAMS.cell[cell_selected_paramset]) 



with pe_tab:
    Tab(IMAGES_DICT["plus"], tab_title = "Positive Electrode")

    pe_selected_paramset = st.selectbox(label= "",
                                        options=list(DEFAULT_PARAMS.pe.keys()), #change with the model
                                        index=0,
                                        label_visibility="collapsed")
    pe_form = ParametersForm(label="pe", default_parameters=DEFAULT_PARAMS.pe[pe_selected_paramset])



with ne_tab:
    Tab(IMAGES_DICT["minus"], tab_title= "Negative Electrode")

    ne_selected_paramset = st.selectbox(label= "",
                                        options=list(DEFAULT_PARAMS.ne.keys()), #change with the model
                                        index=0,
                                        label_visibility="collapsed")
    ne_form = ParametersForm(label="ne", default_parameters=DEFAULT_PARAMS.ne[ne_selected_paramset])



with elyte_tab:
    Tab(IMAGES_DICT["elyte"], tab_title= "Electrolyte")

    elyte_selected_paramset = st.selectbox(label= "",
                                        options=list(DEFAULT_PARAMS.elyte.keys()), #change with the model
                                        index=0,
                                        label_visibility="collapsed")
    elyte_form = ParametersForm(label="elyte", default_parameters=DEFAULT_PARAMS.elyte[elyte_selected_paramset])



with cycling_tab:
    Tab(IMAGES_DICT["current"], tab_title = "Cycling Program")

    cycling_selected_paramset = st.selectbox(label= "",
                                        options=list(DEFAULT_PARAMS.cycling.keys()), #change with the model
                                        index=0,
                                        label_visibility="collapsed")
    cycling_form = ParametersForm(label="cycling", default_parameters=DEFAULT_PARAMS.cycling[cycling_selected_paramset])


user_parameters = {"cell":cell_form.user_inputs,
        "pe":pe_form.user_inputs,
        "ne":ne_form.user_inputs,
        "elyte":elyte_form.user_inputs,
        "cycling":cycling_form.user_inputs,}

with st.expander("Json"):
    st.json(user_parameters)


SubmitJob(user_parameters = json.dumps(user_parameters, indent = 2))

