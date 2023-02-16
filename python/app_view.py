
import streamlit as st
from app_model import OptionsParameter, NumericalParameter, BooleanParameter


class Heading:

    title = "BattMo"
    subtitle = "Framework for continuum modelling of electrochemical devices."
    description = """BattMO simulates the Current-Voltage response of a battery, using on Physics-based
models. For each tab below, load pre-defined parameters, modify them and submit a 
simulation job."""

    md_website = "[BatteryModel.com](https://batterymodel.com/)"
    md_doi = "[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6362783.svg)](https://doi.org/10.5281/zenodo.6362783)"
    md_github = "[![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/BattMoTeam/BattMo)"

    def __init__(self, logo):
        self.logo = logo

        self.render_title()
        self.render_external_links()
        self.render_description()
        st.markdown("#")  # space

    def render_title(self): 
        # Title and subtitle
        logo_col, title_col = st.columns([1,5])
        logo_col.image(self.logo)
        title_col.title(Heading.title)
        st.text(Heading.subtitle)

    def render_external_links(self):
        # External links
        website_col, doi_col, github_col = st.columns([2, 3, 4])
        website_col.markdown(Heading.md_website)
        doi_col.markdown(Heading.md_doi)
        github_col.markdown(Heading.md_github)

    def render_description(self):
        # Description
        st.text(Heading.description) 


class ParametersForm:

    def __init__(self, label: str, default_parameters: dict):
        self.label = label
        self.default_parameters = default_parameters        
        self.user_inputs = {} 
        self.button_on = False
        self.render_form()

    def render_form(self):       

        with st.form(self.label):

            for param_key, param_value in self.default_parameters.items():

                if isinstance(param_value, NumericalParameter):

                    widget_input = st.number_input(
                        label=param_key,
                        value=param_value.default,
                        min_value= param_value.val_min,
                        max_value=param_value.val_max,
                        key=self.label + "_" + param_key
                    )

                elif isinstance(param_value, OptionsParameter):

                    widget_input = st.selectbox(
                        label=param_key,
                        options=param_value.options,
                        index=0,
                        key=self.label + "_" + param_key
                    )

                elif isinstance(param_value, BooleanParameter):

                    widget_input = st.checkbox(
                        label=param_key,
                        value=param_value.default,
                        key=self.label + "_" + param_key
                    )

                self.user_inputs.update({param_key: widget_input})

            self.button_on = st.form_submit_button("Save")


class Tab:

    def __init__(self, logo, tab_title: str):
        self.logo = logo
        self.tab_title = tab_title

        self.render_tab()

    def render_tab(self):
        # logo and selections
        tab_image_col, tab_title_col = st.columns([1, 5])
        tab_image_col.image(self.logo)
        tab_title_col.markdown("###")
        tab_title_col.subheader(self.tab_title)
        # tab_title_col.selectbox(label= "",
        #                     options=list(self.parameter_sets.keys()), #change with the model
        #                     index=0,
        #                     label_visibility="hidden", 
        #                     key=self.tab_id+"_sets")

    def render_parameters(self):

        with st.expander("Parameters"):  # change with the model
            st.json({
                "Diameter [mm]": 100,
                "Height [mm]": 25
            })


class SubmitJob:
    def __init__(self, user_parameters):
        self.user_parameters = user_parameters
        self.render_submit_btn()
        st.markdown("#")  # space

    def render_submit_btn(self):

        st.markdown("### Submit simulation")
        st.download_button(
            label="Save Input parameters",
            data=self.user_parameters,
            file_name="battmo_input_parameters.json",
            mime="application/json"
        )
