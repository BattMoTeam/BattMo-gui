import os
from PIL import Image

import json
import streamlit as st
from app_parameter_model import *


def st_space(space_number=1):
    for _ in range(space_number):
        st.markdown("#")


class SetHeading:
    def __init__(self, logo):
        self.logo = logo

        self.title = "BattMo"
        self.subtitle = "Framework for continuum modelling of electrochemical devices."
        self.description = """
            BattMO simulates the Current-Voltage response of a battery, using on Physics-based
            models. For each tab below, load pre-defined parameters, modify them and submit a 
            simulation job.
        """

        self.website = "[BatteryModel.com](https://batterymodel.com/)"
        self.doi = "[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6362783.svg)](https://doi.org/10.5281/zenodo.6362783)"
        self.github = "[![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/BattMoTeam/BattMo)"

        # Set heading
        self.set_heading()

    def set_heading(self):
        self.set_title_and_logo()
        self.set_external_links()
        self.set_description()
        st_space()

    def set_title_and_logo(self):
        # Title and subtitle
        logo_col, title_col = st.columns([1, 5])
        logo_col.image(self.logo)
        title_col.title(self.title)
        st.text(self.subtitle)

    def set_external_links(self):
        # External links
        website_col, doi_col, github_col = st.columns([2, 3, 4])
        website_col.markdown(self.website)
        doi_col.markdown(self.doi)
        github_col.markdown(self.github)

    def set_description(self):
        # Description
        st.text(self.description)


class SetTabs:
    def __init__(self, db_helper, images):
        self.db = db_helper
        self.image_dict = images

        self.formatter = FormatParameters()

        # Initialize tabs
        self.all_tabs = st.tabs(self.db.all_tab_display_names)
        self.user_input = {}

        # Fill tabs
        self.set_tabs()

    def set_tabs(self):
        for tab in self.all_tabs:
            tab_parameters = {}
            tab_index = self.db.get_tab_index_from_st_tab(tab)
            db_tab_id = self.db.all_tab_id[tab_index]

            # logo and title
            self.set_logo_and_title(tab, tab_index)

            # get tab's categories
            categories = self.db.get_categories_from_tab_id(db_tab_id)
            len_categories = len(categories)

            if len_categories > 1:  # create one sub tab per category
                all_category_display_names = [a[2] for a in categories]
                all_sub_tabs = tab.tabs(all_category_display_names)

                for i in range(len_categories):
                    category_id, category_name, _, _, _ = categories[i]

                    selected_parameter_set = self.create_parameter_set_dropdown(
                        tab=all_sub_tabs[i],
                        category_id=category_id,
                        category_name=category_name
                    )

                    category_parameters = self.create_parameter_form(
                        tab=all_sub_tabs[i],
                        category_name=category_name,
                        selected_parameter_set=selected_parameter_set
                    )

                    tab_parameters[category_name] = category_parameters
            else:  # no sub tab is needed
                category_id, category_name, _, _, _ = categories[0]

                selected_parameter_set = self.create_parameter_set_dropdown(
                    tab=tab,
                    category_id=category_id,
                    category_name=category_name
                )

                category_parameters = self.create_parameter_form(
                    tab=tab,
                    category_name=category_name,
                    selected_parameter_set=selected_parameter_set
                )

                tab_parameters.update(category_parameters)

            # tab is fully defined, its parameters are saved in the user_input dict
            self.user_input[self.db.all_tab_names[tab_index]] = tab_parameters

    def set_logo_and_title(self, tab, tab_index):
        image_column, title_column = tab.columns([1, 5])
        image_column.image(self.image_dict[str(tab_index)])
        title_column.markdown("###")
        title_column.subheader(self.db.all_tab_display_names[tab_index])

    def create_parameter_set_dropdown(self, tab, category_id, category_name):
        selected_parameter_set = tab.selectbox(
            label=category_name,
            options=self.db.get_all_parameter_sets_by_category_id(category_id),
            key=str(category_id),
            label_visibility="collapsed"
        )
        return selected_parameter_set

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
    def __init__(self, json_data):
        self.json_data = json_data
        self.label = "Json"

        self.set_json_viewer()

    def set_json_viewer(self):
        viewer = st.expander(self.label)
        viewer.json(self.json_data)


class SubmitJob:
    def __init__(self, user_parameters):
        self.header = "Submit simulation"

        self.button_label = "Save Input parameters"

        self.file_data = json.dumps(user_parameters, indent=2)
        self.file_name = "battmo_input_parameters.json"
        self.file_mime_type = "application/json"

        self.set_submit_button()

    def set_submit_button(self):
        # set header
        st.markdown("### " + self.header)

        # set download button
        st.download_button(
            label=self.button_label,
            data=self.file_data,
            file_name=self.file_name,
            mime=self.file_mime_type
        )


class LoadImages:
    def __init__(self, path_to_images):
        self.path_to_images = path_to_images
        self.current_path = os.path.dirname(os.path.abspath(__file__))

        self.image_dict = self.load_images()
        self.logo = self.get_logo()

    def get_logo(self):
        return Image.open(os.path.join(self.path_to_images, "battmo_logo.png"))

    def load_images(self):
        def join_path(path):
            return os.path.join(self.path_to_images, path)

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

