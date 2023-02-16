import streamlit as st
from PIL import Image
import os
import json

from app_view import Heading, Tab, SubmitJob, ParametersForm
from app_model import LoaderJsons

THISDIR = os.path.realpath(os.path.dirname(__file__))  
 

# ###################################### INITIALIZATION FUNCTIONS ##################################

@st.cache
def load_images(cwd: str = THISDIR) -> dict:

    resources_dir = os.path.join(cwd, './resources/') 

    return {"logo": Image.open(resources_dir+"battmo_logo.png"),
            "cell_coin": Image.open(resources_dir+"cell_coin.png"),
            "cell_prismatic": Image.open(resources_dir+"cell_prismatic.png"),
            "cell_cylindrical": Image.open(resources_dir+"cell_cylindrical.png"),
            "plus": Image.open(resources_dir+"plus.png"),
            "minus": Image.open(resources_dir+"minus.png"),
            "electrolyte": Image.open(resources_dir+"electrolyte.png"),
            "current": Image.open(resources_dir+"current.png")}


def load_parameter_sets():
    available_params = LoaderJsons()
    return available_params.conform_params_to_app_model()


# ######    Immutable dicts      ######
IMAGES_DICT = load_images()
DEFAULT_PARAMS = load_parameter_sets()


# ########################################### APP #################################################


Heading(IMAGES_DICT["logo"])

cell_tab, positive_electrode_tab, negative_electrode_tab, electrolyte_tab, cycling_tab = st.tabs([
    "Cell",
    "Positive Electrode",
    "Negative Electrode",
    "Electrolyte",
    "Cycling Program"
])

st.markdown("#")  # space


with cell_tab:               

    Tab(IMAGES_DICT["cell_coin"], tab_title="Cell")

    cell_selected_paramset = st.selectbox(
        label="",
        options=list(DEFAULT_PARAMS.cell.keys()),  # change with the model
        index=0,
        label_visibility="collapsed"
    )
    cell_form = ParametersForm(
        label="cell",
        default_parameters=DEFAULT_PARAMS.cell[cell_selected_paramset]
    )

with positive_electrode_tab:
    Tab(IMAGES_DICT["plus"], tab_title="Positive Electrode")

    positive_electrode_selected_paramset = st.selectbox(
        label="",
        options=list(DEFAULT_PARAMS.positive_electrode.keys()),  # change with the model
        index=0,
        label_visibility="collapsed"
    )
    positive_electrode_form = ParametersForm(
        label="positive_electrode",
        default_parameters=DEFAULT_PARAMS.positive_electrode[positive_electrode_selected_paramset]
    )

with negative_electrode_tab:
    Tab(IMAGES_DICT["minus"], tab_title="Negative Electrode")

    negative_electrode_selected_paramset = st.selectbox(
        label="",
        options=list(DEFAULT_PARAMS.negative_electrode.keys()),  # change with the model
        index=0,
        label_visibility="collapsed"
    )
    negative_electrode_form = ParametersForm(
        label="negative_electrode",
        default_parameters=DEFAULT_PARAMS.negative_electrode[negative_electrode_selected_paramset]
    )

with electrolyte_tab:
    Tab(IMAGES_DICT["elyte"], tab_title="Electrolyte")

    electrolyte_selected_paramset = st.selectbox(
        label="",
        options=list(DEFAULT_PARAMS.electrolyte.keys()),  # change with the model
        index=0,
        label_visibility="collapsed"
    )
    electrolyte_form = ParametersForm(
        label="electrolyte",
        default_parameters=DEFAULT_PARAMS.electrolyte[electrolyte_selected_paramset]
    )

with cycling_tab:
    Tab(IMAGES_DICT["current"], tab_title="Cycling Program")

    cycling_selected_paramset = st.selectbox(
        label="",
        options=list(DEFAULT_PARAMS.cycling.keys()),  # change with the model
        index=0,
        label_visibility="collapsed"
    )
    cycling_form = ParametersForm(
        label="cycling",
        default_parameters=DEFAULT_PARAMS.cycling[cycling_selected_paramset]
    )


user_parameters = {
    "cell": cell_form.user_inputs,
    "positive_electrode": positive_electrode_form.user_inputs,
    "negative_electrode": negative_electrode_form.user_inputs,
    "electrolyte": electrolyte_form.user_inputs,
    "cycling": cycling_form.user_inputs
}

with st.expander("Json"):
    st.json(user_parameters)


SubmitJob(user_parameters=json.dumps(user_parameters, indent=2))

