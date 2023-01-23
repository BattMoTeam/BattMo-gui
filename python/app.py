import streamlit as st
from PIL import Image
import os

THISDIR = os.path.realpath(os.path.dirname(__file__))
RESOURCES_DIR = os.path.join(THISDIR, './resources/')

######################################## INITIALIZATION FUNCTIONS ##################################
@st.cache
def load_images(resources_dir: str = RESOURCES_DIR)-> dict:
    return {"logo":Image.open(resources_dir+"battmo_logo.png"), 
            "cell_coin":Image.open(resources_dir+"cell_coin.png"), 
            "cell_prismatic": Image.open(resources_dir+"cell_prismatic.png"),
            "cell_cylindrical":Image.open(resources_dir+"cell_cylindrical.png"),
            "plus": Image.open(resources_dir+"plus.png"),
            "minus": Image.open(resources_dir+"minus.png"),
            "elyte": Image.open(resources_dir+"elyte.png"),
            "current": Image.open(resources_dir+"current.png"),}

############################################# APP ################################################# 


image_dict = load_images()


######## Headings ######

logo_col, title_col = st.columns([1,5]) 

logo_col.image(image_dict["logo"])
title_col.markdown("# BattMO")


st.markdown("Framework for continuum modelling of electrochemical devices.")


website_col, doi_col, github_col = st.columns([2,3,4])

website_col.markdown("[BatteryModel.com](https://batterymodel.com/)")
doi_col.markdown("[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6362783.svg)](https://doi.org/10.5281/zenodo.6362783)")
github_col.markdown("[![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/BattMoTeam/BattMo)")

st.markdown("""BattMO simulates the Current-Voltage response of a battery, using on Physics-based models. 
            For each tab below, load pre-defined parameters, modify them and submit a simulation job.""")



cell_tab, pe_tab, ne_tab, elyte_tab = st.tabs(["Cell", "Positive Electrode", "Negative Electrode",
                                                            "Electrolyte"])



######## Cell ######

with cell_tab:
    st.markdown("### Cell")

    cell_image_col, cell_widget_col = st.columns([1,5]) 
    cell_image_col.image(image_dict["cell_coin"])
    cell_widget_col.selectbox(label= "",
                            options=["Coin cell", "Cylindrical cell", "Pouch cell", "Prismatic cell"],
                            index=0,
                            label_visibility="collapsed")

    with st.expander("Parameters"):
        st.json({"Diameter [mm]": 100,
                "Height [mm]": 25})


######## Positive Electrode ###### 
with pe_tab:
    st.markdown("### Positive Electrode")

    pe_image_col, pe_widget_col = st.columns([1,5]) 
    pe_image_col.image(image_dict["plus"])
    pe_widget_col.selectbox(label= "", key="pe",
                            options=["LCO", "NCA", "NCM", "LFP"],
                            index=0,
                            label_visibility="hidden")

    with st.expander("Parameters"):
        st.json({"Particle radius [m]": 4.12e-06,
                "Thickness [m]": 5.62e-05,})


######## Negative Electrode ###### 
with ne_tab:
    st.markdown("### Negative Electrode")

    ne_image_col, ne_widget_col = st.columns([1,5]) 
    ne_image_col.image(image_dict["minus"])
    ne_widget_col.selectbox(label= "",key="ne",
                            options=["Graphite", "Silicon", "Si:Gr 1:100", "Si:Gr 2:100"],
                            index=0,
                            label_visibility="hidden")

    with st.expander("Parameters"):
        st.json({"Particle radius [m]": 4.12e-06,
                "Thickness [m]": 5.62e-05})


######## Electrolyte ###### 
with elyte_tab:
    st.markdown("### Electrolyte")

    elyte_image_col, elyte_widget_col = st.columns([1,5]) 
    elyte_image_col.image(image_dict["elyte"])
    elyte_widget_col.selectbox(label= "",key="elyte",
                            options=["LP57", "LP30", "LC30"],
                            index=0,
                            label_visibility="hidden")

    with st.expander("Parameters"):
        st.json({"Initial concentration [mol.m-3]": 1000,
                "Cation transference number": 0.2594})



######## Cycling Protocol ###### 

cp_image_col, cp_widget_col = st.columns([1,5]) 
cp_image_col.image(image_dict["current"])
cp_widget_col.selectbox(label= "Cycling program",key="cp",
                            options=["CC", "CV", "CCCV", "GITT"],
                            index=0,
                            label_visibility="hidden")

with st.expander("Parameters"):
    st.json({"Lower voltage cut-off [V]": 2.7,
            "Upper voltage cut-off [V]": 4.2,})


######## Submit ###### 
st.markdown("### Submit simulation")
st.button("Submit") 