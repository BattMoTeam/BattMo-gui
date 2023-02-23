import os
import json
from PIL import Image
import streamlit as st
from app_model import *


class AppController:
    def __init__(self):
        self.current_path = os.path.dirname(os.path.abspath(__file__))

        self.image_dict = self.load_images()
        self.logo = self.get_logo()

    def get_path_to_images(self):
        return os.path.join(self.current_path, 'resources', 'images')

    def get_logo(self):
        return Image.open(os.path.join(self.get_path_to_images(), "battmo_logo.png"))

    def load_images(self):
        path_to_images = self.get_path_to_images()

        def join_path(path):
            return os.path.join(path_to_images, path)

        # TBD, images for all, proper naming
        return {
            "0": Image.open(join_path("cell_coin.png")),
            "9": Image.open(join_path("cell_prismatic.png")),
            "4": Image.open(join_path("cell_cylindrical.png")),
            "1": Image.open(join_path("plus.png")),
            "2": Image.open(join_path("minus.png")),
            "3": Image.open(join_path("electrolyte.png")),
            "5": Image.open(join_path("current.png")),
            "6": Image.open(join_path("current.png")),
            "7": Image.open(join_path("current.png")),
            "8": Image.open(join_path("current.png"))
        }


class InitializeHeading:

    title = "BattMo"
    subtitle = "Framework for continuum modelling of electrochemical devices."
    description = """
        BattMO simulates the Current-Voltage response of a battery, using on Physics-based
        models. For each tab below, load pre-defined parameters, modify them and submit a 
        simulation job.
    """

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
        logo_col, title_col = st.columns([1, 5])
        logo_col.image(self.logo)
        title_col.title(InitializeHeading.title)
        st.text(InitializeHeading.subtitle)

    def render_external_links(self):
        # External links
        website_col, doi_col, github_col = st.columns([2, 3, 4])
        website_col.markdown(InitializeHeading.md_website)
        doi_col.markdown(InitializeHeading.md_doi)
        github_col.markdown(InitializeHeading.md_github)

    def render_description(self):
        # Description
        st.text(InitializeHeading.description)


class InitializeTabs:
    def __init__(self, db_helper, images):
        self.image_dict = images
        self.db = db_helper
        self.formatter = FormatParameters()
        self.all_tabs = st.tabs(self.db.all_tab_display_names)

        st.markdown("#")  # space
        self.user_input = {}
        self.initialize_tabs()

    def initialize_tabs(self):
        for tab in self.all_tabs:
            tab_parameters = {}
            tab_index = self.db.get_tab_index_from_st_tab(tab)
            db_tab_id = self.db.all_tab_id[tab_index]

            # logo and title
            self.set_logo_and_title(tab, tab_index)

            categories = self.db.get_categories_from_tab_id(db_tab_id)
            has_subcategories = len(categories) > 1

            for category in categories:

                selected_parameter_set, category_name = self.create_parameter_set_dropdown(
                    tab=tab,
                    category=category,
                    has_subcategories=has_subcategories
                )

                category_parameters = self.create_parameter_form(
                    tab=tab,
                    category_name=category_name,
                    selected_parameter_set=selected_parameter_set
                )

                if has_subcategories:
                    tab_parameters.update(category_parameters)
                else:
                    tab_parameters[category_name] = category_parameters

            self.user_input[self.db.all_tab_names[tab_index]] = tab_parameters

    def set_logo_and_title(self, tab, tab_index):
        image_column, title_column = tab.columns([1, 5])
        image_column.image(self.image_dict[str(tab_index)])
        title_column.markdown("###")
        title_column.subheader(self.db.all_tab_display_names[tab_index])

    def create_parameter_set_dropdown(self, tab, category, has_subcategories):
        category_id, category_name, category_display_name, _, _ = category
        selected_parameter_set = tab.selectbox(
            label=category_display_name,
            options=self.db.get_all_parameter_sets_by_category_id(category_id),
            key=str(category_id),
            label_visibility="visible" if has_subcategories else "collapsed"
        )
        return selected_parameter_set, category_name

    def create_parameter_form(self, tab, category_name, selected_parameter_set):
        parameter_form = tab.form(category_name)
        raw_parameters = self.db.extract_parameters_by_parameter_set_name(selected_parameter_set)
        formatted_parameters = self.formatter.format_parameters(raw_parameters)

        category_parameters = {}
        for parameter in formatted_parameters:
            value_for_json = parameter.value

            if parameter.is_shown_to_user:
                user_input = None

                if isinstance(parameter, NumericalParameter):
                    user_input = parameter_form.number_input(
                        label=parameter.name,
                        value=parameter.value,
                        min_value=parameter.min_value,
                        max_value=parameter.max_value,
                        key=str(parameter.id) + category_name
                    )

                elif isinstance(parameter, StrParameter):
                    parameter_form.selectbox(
                        label=parameter.name,
                        options=[parameter.value],
                        index=0,
                        key=str(parameter.id) + category_name
                    )

                if user_input:
                    value_for_json = user_input

            category_parameters[parameter.name] = value_for_json

        parameter_form.form_submit_button("Save")

        return category_parameters


class JsonViewer:
    def __init__(self, user_parameters_input):
        expander = st.expander("Json")
        expander.json(user_parameters_input)


class SubmitJob:
    def __init__(self, user_parameters):
        self.user_parameters = json.dumps(user_parameters, indent=2)
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
