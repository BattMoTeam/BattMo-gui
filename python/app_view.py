import os
from PIL import Image

import json
import streamlit as st
from app_parameter_model import *
from resources.db import db_helper


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


class SetModelChoice:
    def __init__(self):

        self.title = "Model"
        self.selected_model = None

        # Set Model choice
        self.set_model_choice()

    def set_model_choice(self):
        self.set_title()
        self.set_dropdown()
        st_space()

    def set_title(self):
        st.markdown("### " + self.title)

    def set_dropdown(self):
        models_as_dict = db_helper.get_models_as_dict()
        selected_model_id = st.selectbox(
            label="model choice",
            options=[model_id for model_id in models_as_dict],
            format_func=lambda x: models_as_dict.get(x),
            key="model_choice",
            label_visibility="collapsed"
        )
        self.selected_model = selected_model_id


class SetTabs:
    def __init__(self, images, model_id, context):
        self.image_dict = images
        self.model_templates = db_helper.get_templates_by_id(model_id)

        self.formatter = FormatParameters()
        self.has_quantitative_property = "hasQuantitativeProperty"

        # Initialize tabs
        self.title = "Parameters"
        self.set_title()
        self.all_tabs = st.tabs(db_helper.all_tab_display_names)
        self.user_input = {
            "@context": context,
            "battery:P2DModel": db_helper.get_model_parameters_as_dict(model_id)
        }

        # Fill tabs
        self.set_tabs()

    def set_title(self):
        st.markdown("### " + self.title)

    def set_tabs(self):
        for tab in self.all_tabs:
            tab_index = db_helper.get_tab_index_from_st_tab(tab)
            db_tab_id = db_helper.all_tab_id[tab_index]

            tab_context_type, tab_context_type_iri = db_helper.get_context_type_and_iri_by_id(db_tab_id)
            tab_parameters = {
                "label": db_helper.all_tab_display_names[tab_index],
                "@type": tab_context_type + "  " + tab_context_type_iri
            }

            # logo and title
            self.set_logo_and_title(tab, tab_index)

            # get tab's categories
            categories = db_helper.get_categories_from_tab_id(db_tab_id)

            if len(categories) > 1:  # create one sub tab per category

                all_category_display_names = [a[5] for a in categories]
                all_sub_tabs = tab.tabs(all_category_display_names)
                i = 0

                for category in categories:
                    category_id, category_name, category_context_type, category_context_type_iri, emmo_relation, _, _, default_template_id, _ = category

                    category_parameters, emmo_relation = self.fill_category(
                        category_id=category_id,
                        category_name=category_name,
                        emmo_relation=emmo_relation,
                        default_template_id=default_template_id,
                        tab=all_sub_tabs[i]
                    )
                    i += 1

                    category_parameters["label"] = category_name
                    category_parameters["@type"] = category_context_type + "  " + category_context_type_iri

                    if emmo_relation is None:
                        tab_parameters[category_context_type] = category_parameters

                    else:
                        tab_parameters[emmo_relation] = [category_parameters]

            else:  # no sub tab is needed

                category_id, category_name, category_context_type, category_context_type_iri, emmo_relation, _, _, default_template_id, _ = categories[0]
                category_parameters, _ = self.fill_category(
                        category_id=category_id,
                        category_name=category_name,
                        emmo_relation=emmo_relation,
                        default_template_id=default_template_id,
                        tab=tab
                    )

                tab_parameters.update(category_parameters)

            # tab is fully defined, its parameters are saved in the user_input dict
            self.user_input[tab_context_type] = tab_parameters

    def set_logo_and_title(self, tab, tab_index):
        image_column, title_column = tab.columns([1, 5])
        image_column.image(self.image_dict[str(tab_index)])
        title_column.text(" ")
        title_column.subheader(db_helper.all_tab_display_names[tab_index])

    def fill_category(self, category_id, category_name, emmo_relation, default_template_id, tab):

        category_parameters = []
        select_box_col, input_col = tab.columns([4, 5])

        template_name = self.model_templates.get(category_name)
        template_id = db_helper.sql_template.get_id_from_name(template_name) if template_name else default_template_id

        raw_template_parameters = db_helper.get_template_parameters_from_template_id(template_id)

        parameter_sets = db_helper.get_all_parameter_sets_by_category_id(category_id)

        parameter_sets_name_by_id = {}
        for id, name, _ in parameter_sets:
            parameter_sets_name_by_id[id] = name

        raw_parameters = []
        for parameter_set_id in parameter_sets_name_by_id:
            raw_parameters += db_helper.extract_parameters_by_parameter_set_id(parameter_set_id)

        formatted_parameters = self.formatter.format_parameters(raw_parameters, raw_template_parameters, parameter_sets_name_by_id)

        for parameter_id in formatted_parameters:
            parameter = formatted_parameters.get(parameter_id)
            if parameter.is_shown_to_user:
                selected_value_id = select_box_col.selectbox(
                    label="[{}]({})".format(parameter.display_name, parameter.context_type_iri),
                    options=parameter.options,
                    key="{}_{}".format(category_id, parameter_id),
                    label_visibility="visible",
                    format_func=lambda x: parameter.options.get(x).display_name
                )

                if isinstance(parameter, NumericalParameter):
                    user_input = input_col.number_input(
                        label=parameter.unit,
                        value=parameter.options.get(selected_value_id).value,
                        min_value=parameter.min_value,
                        max_value=parameter.max_value,
                        key="input_{}_{}".format(category_id, parameter_id),
                        format=parameter.format,
                        step=parameter.increment,
                        label_visibility="visible"
                    )
                else:
                    user_input = input_col.selectbox(
                        label=parameter.display_name,
                        options=[parameter.options.get(selected_value_id).value],
                        key="input_{}_{}".format(category_id, parameter_id),
                        label_visibility="hidden",
                    )
                parameter.set_selected_value(user_input)

            formatted_value_dict = parameter.selected_value

            if isinstance(parameter, NumericalParameter):
                formatted_value_dict = {
                    "@type": "emmo:Numerical",
                    "hasNumericalData": parameter.selected_value
                }

            elif isinstance(parameter, StrParameter):
                formatted_value_dict = {
                    "@type": "emmo:String",
                    "hasStringData": parameter.selected_value
                }

            elif isinstance(parameter, BooleanParameter):
                formatted_value_dict = {
                    "@type": "emmo:Boolean",
                    "hasStringData": parameter.selected_value
                }

            parameter_details = {
                "label": parameter.name,
                "@type": parameter.context_type + "  " + parameter.context_type_iri if parameter.context_type and parameter.context_type_iri else "None",
                "value": formatted_value_dict
            }
            if isinstance(parameter, NumericalParameter):
                parameter_details["unit"] = parameter.unit

            category_parameters.append(parameter_details)

        return {self.has_quantitative_property: category_parameters}, emmo_relation


class JsonViewer:
    def __init__(self, json_data, label="Json"):
        self.json_data = json_data
        self.label = label

        self.set_json_viewer()

    def set_json_viewer(self):
        viewer = st.expander(self.label)
        viewer.json(self.json_data)


class SubmitJob:
    def __init__(self, gui_dict, battmo_dict):
        self.header = "Save parameters"

        self.gui_button_label = "Save GUI output parameters"
        self.battmo_button_label = "Save BattMo input parameters"

        self.file_mime_type = "application/json"
        self.gui_file_data = json.dumps(gui_dict, indent=2)
        self.gui_file_name = "gui_output_parameters.json"

        self.battmo_file_data = json.dumps(battmo_dict, indent=2)
        self.battmo_file_name = "battmo_input_parameters.json"

        self.set_submit_button()

    def set_submit_button(self):
        # set header
        st.markdown("### " + self.header)

        # set download button
        st.download_button(
            label=self.gui_button_label,
            data=self.gui_file_data,
            file_name=self.gui_file_name,
            mime=self.file_mime_type
        )
        st.download_button(
            label=self.battmo_button_label,
            data=self.battmo_file_data,
            file_name=self.battmo_file_name,
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

        l, w = 80, 80

        def image_open(file_name):
            image = Image.open(join_path(file_name))
            return image.resize((l, w))

        # TBD, images for all, proper naming
        return {
            "0": image_open("cell_coin.png"),
            "9": image_open("cell_prismatic.png"),
            "4": image_open("plus.png"),
            "1": image_open("plus.png"),
            "2": image_open("minus.png"),
            "3": image_open("electrolyte.png"),
            "5": image_open("current.png"),
            "6": image_open("current.png"),
            "7": image_open("current.png"),
            "8": image_open("cell_cylindrical.png")
        }

