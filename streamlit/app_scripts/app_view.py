from PIL import Image
import pprint
import json
import pickle
import io
import h5py
import streamlit as st
import numpy as np
from uuid import uuid4
import sys
import requests
import pdb
from streamlit_extras.switch_page_button import switch_page
import sympy as sp
import matplotlib.pyplot as plt
import os
import plotly.express as px
import plotly.graph_objects as go
import streamlit_elements as el
import ast
import pandas as pd
import random


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app_scripts.app_parameter_model import *
from database import db_helper, db_handler
from app_scripts import app_access, match_json_LD, match_json_upload, app_controller
from app_scripts import app_calculations as calc
#con, cur = app_access.get_sqlite_con_and_cur()


#####################################
# Convenient random functions
#####################################


def get_theme_style():


    if st.session_state.theme == "dark":
        with open(app_access.get_path_to_dark_style_css()) as f:
            style = st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    else:
        with open(app_access.get_path_to_light_style_css()) as f:
            style = st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    return style



def reset_func(category_id, parameter_id, parameter):
    """
    Function needed for the selectboxes and number_inputs to work properly together.
    """
    value = parameter.options[st.session_state["select_{}_{}".format(category_id, parameter_id)]].value
    if isinstance(parameter, FunctionParameter):
        value = value.get("functionname")
    else:
        value = value
    st.session_state["input_{}_{}".format(category_id, parameter_id)] = value



def st_space(tab=None, space_width=1, space_number=1):
    """
    function meant to be a shortcut for adding space in streamlit. Not important.
    """
    space = ""
    for _ in range(space_width):
        space += "#"

    if tab:
        for _ in range(space_number):
            tab.markdown(space)
    else:
        for _ in range(space_number):
            st.markdown(space)



#########################################
# Classes used on the Introduction page
#########################################


class SetHeading:
    """
    Only used in the "Introduction" page, nothing important here, opened for complete modification.
    """
    def __init__(self, logo):
        self.logo = logo

        self.title = "BattMo"
        self.subtitle = "Framework for continuum modelling of electrochemical devices."
        self.description = """
            This graphical user interface can be used to run (cell level) battery simulations
            with BattMo. BattMo is a framework for continuum modelling of electrochemical
            devices. It simulates the Current-Voltage response of a battery using
            Physics-based models.
        """
        self.info = "Hover over the following buttons to see what you can find on each page."

        # Set heading
        self.set_heading()


    def set_heading(self):
        self.set_title_and_logo()
        self.set_description()
        self.set_info()

    def set_title_and_logo(self):
        # Title and subtitle
        logo_col, title_col = st.columns([1, 5])
        logo_col.image(self.logo)
        title_col.title(self.title)
        #st.text(self.subtitle)

    def set_description(self):
        # Description
        st.write(self.description)

    def set_info(self):

        st.info(self.info)


class SetPageNavigation:
    """
    Used in the "Introduction" page, sets the navigation info and buttons to to the other pages.
    """
    def __init__(self):

        self.help_simulation = "Define your input parameters and run a simulation."
        self.help_results = "Download and visualize your results."
        self.help_materials_and_models = "See which pre-defined materials and which simulation models are available."
        self.set_page_navigation()

    def set_page_navigation(self):

        col = self.set_page_buttons()

        return col


    def set_page_buttons(self):

        _,col1,_ = st.columns(3)
        #st_space(space_width=6)
        _,col2,_ = st.columns(3)
        #st_space(space_width=6)
        _,col3,col4 = st.columns(3)
        st_space(space_width=6)

        simulation_page = col1.button(label = "Simulation",
                        help = self.help_simulation,
                        use_container_width=True
                        )

        results_page = col2.button(label = "Results",
                        help = self.help_results,
                        use_container_width=True
                        )

        materials_and_models_page = col3.button(label = "Materials and models",
                        help = self.help_materials_and_models,
                        use_container_width=True
                        )

        if simulation_page:
            switch_page("Simulation")

        if results_page:
            switch_page("Results")

        if materials_and_models_page:
            switch_page("Materials and models")

        return col4


class SetAcknowledgementInfo:
    """
    Used to render the info on the funding of the project on the 'Introduction' page.
    """
    def __init__(self,col):

        self.col = col
        self.text = "This project has received [funding](https://github.com/BattMoTeam/BattMo#) from the European Union"
        self.flag_image = Image.open(os.path.join(app_access.get_path_to_images_dir(), "flag_of_europe.jpg"))

        self.set_acknowledgement()

    def set_acknowledgement(self):

        #col1,col2,col3 = st.columns([1,2,3])
        #_,col2 = st.columns([4,1.5])
        self.set_europe_flag()
        self.set_funding_info()


    def set_funding_info(self):

        st.write(self.text)

    def set_europe_flag(self):

        st.image(self.flag_image, width = 90)



class SetExternalLinks:
    """
    Used in the "Introduction" page, sets the links to external information.
    """
    def __init__(self):

        self.batterymodel = "[BatteryModel.com](https://batterymodel.com/)"
        self.zenodo = "[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6362783.svg)](https://doi.org/10.5281/zenodo.6362783)"
        self.github = "[![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/BattMoTeam/BattMo)"
        self.documentation = "[![Repo](https://badgen.net/badge/Doc/BattMo-app)](https://battmoteam.github.io/BattMo/gui.html)"

        self.set_external_links()

    def set_external_links(self):

        st.divider()
        website_col, doi_col, github_col, doc_col = st.columns([3.5, 5, 3,3])
        website_col.markdown(self.batterymodel)
        doi_col.markdown(self.zenodo)
        github_col.markdown(self.github)
        doc_col.markdown(self.documentation)
        st.divider()



#########################################
# Classes used on the Simulation page
#########################################


class SetModelChoice:
    """
    Rendering of small section for model choice.
    For now (03/07/23) only P2D is used, so there's no "real" choice; could be removed if we stick to P2D only
    """
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


class SetupLinkedDataStruct():

    def __init__(self):
        # Ontology definitions

        self.id = "@id"
        self.type = "@type"
        self.label = "rdfs:label"

        self.hasInput = "hasInput"
        self.hasActiveMaterial = "hasActiveMaterial"
        self.hasBinder = "hasBinder"
        self.hasConductiveAdditive = "hasConductiveAdditive"
        self.hasElectrode = "hasElectrode"
        self.hasNegativeElectrode = "hasNegativeElectrode"
        self.hasPositiveElectrode = "hasPositiveElectrode"
        self.hasElectrolyte = "hasElectrolyte"
        self.hasSeparator = "hasSeparator"
        self.hasBoundaryConditions = "hasBoundaryConditions"
        self.hasCyclingProcess = "hasCyclingProcess"
        self.hasBatteryCell = "hasBatteryCell"

        self.hasQuantitativeProperty = "hasQuantitativeProperty"
        self.hasObjectiveProperty = "hasObjectiveProperty"
        self.hasConstituent = "hasConstituent"
        self.hasNumericalData = "hasNumericalData"
        self.hasNumericalPart = "hasNumericalPart"
        self.hasNumericalValue = "hasNumericalValue"
        self.hasStringData = "hasStringData"
        self.hasStringValue = "hasStringValue"
        self.hasStringPart = "hasStringPart"
        self.hasModel = "hasModel"
        self.hasCell = "hasCell"

        self.universe_label = "MySimulationSetup"
        self.cell_label = "MyCell"
        self.cell_type = "battery:Cell"


        self.context= {
                        "schema":"https://schema.org/",
                        "":"https://raw.githubusercontent.com/BIG-MAP/BattINFO/master/context.json",
                        "emmo": "https://w3id.org/emmo#",
                        "echem": "https://w3id.org/emmo/domain/electrochemistry#",
                        "battery": "https://w3id.org/emmo/domain/battery#",
                        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                        "hasConstituent": "emmo:hasConstituent",


                        # "hasNumericalData": "emmo:hasNumericalData",
                        # "hasStringData": "emmo:hasStringData",
                        # "value": "emmo:hasQuantityValue",
                        # "unit": "emmo:hasReferenceUnit",
                        # "label": "skos:prefLabel"

                        # "skos": "http://www.w3.org/2004/02/skos/core#",
                        # "bkb": "https://w3id.org/emmo/domain/battery_knowledge_base#",
                        # "qudt": "http://qudt.org/vocab/unit/",
                    }

    def setup_linked_data_dict(self, model_id, model_name):

        model_label = "{} model".format(model_name)
        id = ""
        model_type = "battery:{}Model".format(model_name)

        dict = {
            "@context": self.context,

            self.universe_label:{
                self.hasModel:{
                    "label": model_label,
                    "@type": model_type,
                    self.hasQuantitativeProperty: db_helper.get_model_parameters_as_dict(model_name)
                }
            }
        }

        # dict = {
        #     "@context": self.context,

        #     self.id:id,
        #     self.type:["Dataset"],
        #     "schema:headline": headline,
        #     "battinfo:hasModel":{
        #         self.type: model_type,
        #         self.id: model_id,
        #         self.label: model_label,

        #         self.hasInput: db_helper.get_model_parameters_as_dict(model_id)
        #     }
        #     }

        return dict

    def fill_sub_dict(self,dict,relation_dict_1, parameters,existence,relation_dict_2 = None,relation_par=None):
        parameters = parameters.copy()
        if self.universe_label in dict:
            if relation_par:
                if existence == "new":
                    dict[self.universe_label][relation_dict_1] = parameters[relation_par]
                elif existence == "existing":
                    dict[self.universe_label][relation_dict_1] += parameters[relation_par]
            else:
                if existence == "new":
                    dict[self.universe_label][relation_dict_1] = parameters
                elif existence == "existing":
                    dict[self.universe_label][relation_dict_1] += parameters
        else:
            if relation_par:
                if existence == "new":
                    if relation_dict_2:
                        dict[relation_dict_1][relation_dict_2] = parameters[relation_par]
                    else:
                        dict[relation_dict_1] = parameters[relation_par]
                elif existence == "existing":
                    if relation_dict_2:
                        dict[relation_dict_1][relation_dict_2] += parameters[relation_par]
                    else:
                        dict[relation_dict_1] += parameters[relation_par]
            else:
                if existence == "new":
                    if relation_dict_2:
                        dict[relation_dict_1][relation_dict_2] = parameters
                    else:
                        dict[relation_dict_1] = parameters

                elif existence == "existing":
                    dict[relation_dict_1] += parameters
        return dict

    @st.cache_data
    def setup_sub_dict(_self,dict=None,display_name=None, context_type=None, type=None, existence = None):

        if type:
            if type == "cell":
                dict = {
                    "label": _self.cell_label,
                    "@type": _self.cell_type
                }
        elif existence =="new":
            dict = {
                    "label": display_name,
                    "@type": context_type
                }


        else:
            dict["label"] = display_name
            dict["@type"] = context_type

        return dict

    def fill_linked_data_dict(self, user_input, content):
        user_input[self.universe_label][self.hasCell] = content

        return user_input

    def setup_parameter_struct(self, parameter,component_parameters=None, value = None):
        if component_parameters is None:
            component_parameters = []

        numeric = isinstance(parameter, NumericalParameter)
        # print("numeric =", numeric)
        # print("object =", parameter)

        try:

            if isinstance(parameter, NumericalParameter):

                formatted_value_dict = {
                    "@type": "emmo:Numerical",
                    self.hasNumericalData: parameter.selected_value
                }

            elif isinstance(parameter, StrParameter):

                formatted_value_dict = {
                    "@type": "emmo:String",
                    self.hasStringData: parameter.selected_value
                }

            elif isinstance(parameter, BooleanParameter):
                formatted_value_dict = {
                    "@type": "emmo:Boolean",
                    self.hasStringData: parameter.selected_value
                }
            elif isinstance(parameter, FunctionParameter):
                formatted_value_dict = {
                    "@type": "emmo:String",
                    self.hasStringData: parameter.selected_value
                }


            parameter_details = {
                "label": parameter.name,
                "@type": parameter.context_type if parameter.context_type else "string",
                "value": formatted_value_dict
            }
            if isinstance(parameter, NumericalParameter):
                parameter_details["unit"] = {
                        "label": parameter.unit_name if parameter.unit_name else parameter.unit,
                        "symbol": parameter.unit,
                        "@type": "emmo:"+parameter.unit_name if parameter.unit_name else parameter.unit,
                    }
            component_parameters.append(parameter_details)

            return component_parameters

        except Exception as e:
            #st.error("An error occurred 1: {}".format(e))
            

            try:
                parameter_id, \
                            name, \
                            model_name, \
                            par_class, \
                            difficulty, \
                            template_id, \
                            context_type, \
                            context_type_iri, \
                            parameter_type, \
                            unit, \
                            unit_name, \
                            unit_iri, \
                            max_value, \
                            min_value, \
                            is_shown_to_user, \
                            description,  \
                            display_name = np.squeeze(parameter)



                formatted_value_dict = value


                formatted_value_dict = {
                    "@type": "emmo:Numerical",
                    self.hasNumericalData: value
                }

                parameter_details = {
                    "label": name,
                    "@type": context_type,
                    "value": formatted_value_dict
                }

                parameter_details["unit"] = {
                    "label": unit_name,
                    "symbol": unit,
                    "@type": "emmo:"+unit_name
                }

                component_parameters.append(parameter_details)
            except Exception as e:
                st.error("An error occurred 2: {}".format(e))


                st.error("This instance of parameter is not handled: {}".format(type(parameter)))
                st.info(NumericalParameter)

            return component_parameters


    @st.cache_data
    def get_relation(_self, id, type):

        if type == "tab":
            context_type= db_helper.get_context_type_and_iri_by_id(id)

        elif type == "category":
            context_type = db_helper.get_categories_context_type_from_id(id)
        elif type == "component":
            context_type = db_helper.get_components_context_type_from_id(id)
        else:
            print("Error: The relation for type {} is non-existing.".format(type))

        relation = "has" + context_type.split(':')[1]
        return relation

    @st.cache_data
    def fill_component_dict(_self,component_parameters,existence, dict = None, relation = None):
        component_parameters = component_parameters.copy()
        if existence == "new":
            dict = {_self.hasQuantitativeProperty: component_parameters}

        elif existence == "existing":
            if _self.hasQuantitativeProperty in component_parameters:

                if _self.hasQuantitativeProperty in dict:
                    dict[_self.hasQuantitativeProperty] += component_parameters[_self.hasQuantitativeProperty]
                elif relation in dict:
                    if _self.hasQuantitativeProperty in dict[relation]:
                        dict[relation][_self.hasQuantitativeProperty] += component_parameters[_self.hasQuantitativeProperty]
                    else:
                        dict[relation][_self.hasQuantitativeProperty] = component_parameters
                else:
                    if relation:
                        dict[relation] = component_parameters

                    else:
                        dict[_self.hasQuantitativeProperty] = component_parameters[_self.hasQuantitativeProperty]
            else:

                dict[relation] = component_parameters

        return dict

    def change_numerical_value(self,dict, index, value):
        try:
            dict[index]["value"][self.hasNumericalData]=value
        except:
            dict[index]["value"]=value

        return dict

    @st.cache_data
    def add_indicators_to_struct(_self, dict, n_to_p, cell_mass, cell_cap, specific_cap_ne, specific_cap_pe, cap_ne,cap_pe,rte):
        dict[_self.universe_label][_self.hasCell][_self.hasBatteryCell][_self.hasQuantitativeProperty] += n_to_p
        dict[_self.universe_label][_self.hasCell][_self.hasBatteryCell][_self.hasQuantitativeProperty] += cell_mass
        dict[_self.universe_label][_self.hasCell][_self.hasBatteryCell][_self.hasQuantitativeProperty] += cell_cap
        dict[_self.universe_label][_self.hasCell][_self.hasBatteryCell][_self.hasQuantitativeProperty] += rte
        dict[_self.universe_label][_self.hasCell][_self.hasElectrode][_self.hasNegativeElectrode][_self.hasNegativeElectrode][_self.hasQuantitativeProperty] += specific_cap_ne
        dict[_self.universe_label][_self.hasCell][_self.hasElectrode][_self.hasPositiveElectrode][_self.hasPositiveElectrode][_self.hasQuantitativeProperty] += specific_cap_pe
        dict[_self.universe_label][_self.hasCell][_self.hasElectrode][_self.hasNegativeElectrode][_self.hasActiveMaterial][_self.hasQuantitativeProperty] += cap_ne
        dict[_self.universe_label][_self.hasCell][_self.hasElectrode][_self.hasPositiveElectrode][_self.hasActiveMaterial][_self.hasQuantitativeProperty] += cap_pe

        return dict


def set_select(raw_parameters, material_display_names, material_values, material_component_id, id):
    key_input_number = "input_number_{}_{}".format(material_component_id, id)
    key_select = "select_{}_{}".format(material_component_id, id)

    selected_parameter_set = st.session_state[key_select]
    index = material_display_names.index(selected_parameter_set)

    if index >= 0:
        material_value = material_values[index]
        st.session_state[key_input_number] = material_value
        
def set_number_input(material_component_id,id):
    pass

class SetTabs:
    """
    - Rendering of almost all the Define Parameter tab
    - formatting parameters, json data creation

    Steps and hierarchy:

    - Model is chosen, cf class SetModelChoice (for now only P2D, but might be other choices later)
    -  corresponding templates are retrieved from database (db). cf templates in python/resources/db/resources/templates
        2 options for each category: either a custom template is defined, or if not the default template is used.
        Currently (03/07/23) only default templates are defined.

    - initialize tabs:
        create tab, check if there's more than one category
        if more than one, create subtabs (st.tab in a st.tab)

    - fill each category:
        retrieve raw parameters from db
        format them by creating python objects (easier to handle)
        create st.selectbox and number_input etc

        careful to optimize this section because it's rerun by streamlit at every click for every single parameter.
    """
    def __init__(self, images, model_id, context):
        # image dict stored for easier access
        self.image_dict = images
        self.model_id = model_id
        self.model_name = db_helper.get_model_name_from_id(model_id)

        # retrieve corresponding templates (not implemented yet)
        #self.model_templates = db_helper.get_templates_by_id(model_id)

        # initialize formatter
        self.formatter = FormatParameters()

        # File input feature
        self.info = "Upload here your JSON input parameter file to automatically fill the parameter inputs."
        self.help = "Check the documentation for the correct format. A link to the documentation can be found on the 'Introduction' page."

        # Initialize tabs
        self.title = "Parameters"
        self.set_title()

        # Import functions for calculations
        self.validate_mass_fraction = calc.validate_mass_fraction
        self.calc_density_mix = calc.calc_density_mix
        self.calc_density_eff = calc.calc_density_eff
        self.calc_mass_loading = calc.calc_mass_loading
        self.calc_thickness = calc.calc_thickness
        self.calc_porosity = calc.calc_porosity
        self.calc_n_to_p_ratio = calc.calc_n_to_p_ratio
        self.calc_cell_mass = calc.calc_cell_mass
        self.calc_capacity_electrode = calc.calc_capacity_electrode
        self.calc_specific_capacity_active_material = calc.calc_specific_capacity_active_material
        self.calc_cell_capacity = calc.calc_cell_capacity

        # user_input is the dict containing all the json LD data
        self.LD = SetupLinkedDataStruct()
        self.user_input = self.LD.setup_linked_data_dict(self.model_id, self.model_name)

        # Create file input
        #self.set_file_input()

        # Fill tabs
        self.set_tabs()

    def set_title(self):
        st.markdown("### " + self.title)

    def set_file_input(self):


        """ Function that create a file input at the Simulation page
        """

        upload, update = st.columns((3,1))
        uploaded_file = upload.file_uploader(self.info, type='json', help= self.help)

        if uploaded_file:
            uploaded_file = uploaded_file.read()
            uploaded_file_dict = json.loads(uploaded_file)
            #uploaded_file_str = str(uploaded_file_dict)

            with open(app_access.get_path_to_uploaded_input(), "w") as outfile:
                json.dump(uploaded_file_dict, outfile,  indent=3)

            gui_formatted_dict = match_json_upload.GuiInputFormatting(self.model_name).gui_dict

            with open(app_access.get_path_to_gui_formatted_input(), "w") as outfile:
                json.dump(gui_formatted_dict,outfile,  indent=3)


            st.success("Your file is succesfully uploaded. Click on the 'PUSH' button to automatically fill in the parameter inputs specified in your file.")

        update.text(" ")
        update.text(" ")

        push = update.button("PUSH")
        if push:
            if uploaded_file is not None:

                with open(app_access.get_path_to_gui_formatted_input(), "r") as outfile:
                    uploaded_input = json.load(outfile)

                self.uploaded_input = uploaded_input
                st.session_state.upload = True

                st.success("The input values are succesfully adapted to your input file. You can still change some settings below if wanted.")

            else:
                st.error("ERROR: No file has been uploaded yet.")

    def set_logo_and_title(self, tab, tab_index):
        if tab_index == 0:
            image_collumn,image_collumn_2, title_column = tab.columns([0.9,0.9,6])
            image_collumn.image(self.image_dict[str(tab_index)])
            image_collumn_2.image(self.image_dict[str(tab_index+1)])
        else:

            image_column, title_column = tab.columns([1, 5])
            image_column.image(self.image_dict[str(tab_index+1)])

        title_column.text(" ")
        title_column.subheader(db_helper.get_basis_tabs_display_names(self.model_name)[tab_index])

    @st.cache_data
    def set_format(_self,value):
        if isinstance(value, int):
            format = "%d"

        else:
            max_readable_value = 10000
            min_readable_value = 0.001
            is_readable = value < max_readable_value and value > min_readable_value
            format = "%g" if is_readable else "%.2e"
        return format

    def set_tabs(self):

        cell_parameters = self.LD.setup_sub_dict(type="cell")

        all_tab_display_names = db_helper.get_basis_tabs_display_names(self.model_name)

        all_tabs = st.tabs(all_tab_display_names)

        db_tab_ids = db_helper.get_db_tab_id(self.model_name)

        index = 0
        for tab in all_tabs:

            db_tab_id = db_tab_ids[index][0]


            tab_context_type= db_helper.get_context_type_and_iri_by_id(db_tab_id)
            tab_name = db_helper.get_tab_name_by_id(db_tab_id)

            tab_parameters = self.LD.setup_sub_dict(display_name=db_helper.get_basis_tabs_display_names(self.model_name)[index], context_type=tab_context_type, existence="new")

            tab_relation = self.LD.get_relation(db_tab_id, "tab")

            # logo and title
            self.set_logo_and_title(tab, index)

            # get tab's categories
            categories = db_helper.get_basis_categories_from_tab_id(db_tab_id)

            if len(categories) > 1:  # create one sub tab per category

                all_category_display_names = [a[7] for a in categories]
                all_sub_tabs = tab.tabs(all_category_display_names)
                i = 0
                mass_loadings = {}

                for category in categories:
                    category_id, category_name,_,_, category_context_type, category_context_type_iri, emmo_relation, category_display_name, _, default_template_id, _ = category

                for category in categories:

                    category_parameters = self.LD.setup_sub_dict(display_name=db_helper.get_basis_categories_display_names(db_tab_id)[i][0],
                                                            context_type=db_helper.get_categories_context_type(db_tab_id)[i][0],
                                                            existence="new"
                                                            )

                    category_id, category_name,_,_, category_context_type, category_context_type_iri, emmo_relation, category_display_name, _, default_template_id, _ = category

                    category_relation = self.LD.get_relation(category_id, "category")

                    category_parameters, emmo_relation, mass_loadings = self.fill_category(
                        category_id=category_id,
                        category_display_name=category_display_name,
                        category_name=category_name,
                        emmo_relation=emmo_relation,
                        default_template_id=default_template_id,
                        tab=all_sub_tabs[i],
                        category_parameters = category_parameters,
                        mass_loadings = mass_loadings,
                    )
                    i += 1

                    tab_parameters[category_relation] = category_parameters
                    cell_parameters[tab_relation] = tab_parameters



            else:  # no sub tab is needed

                category_parameters = {}

                category_id, category_name,_,_, category_context_type, category_context_type_iri, emmo_relation, category_display_name, _, default_template_id, _= categories[0]

                if category_name == "protocol":

                    # different way of filling parameters for protocol section, the idea is to choose the name of the
                    # protocol and then the parameters are filled. Could be done also for the Cell tab
                    category_parameters = self.fill_category_protocol(
                        category_id=category_id,
                        category_display_name= category_display_name,
                        category_name=category_name,
                        emmo_relation=emmo_relation,
                        default_template_id=default_template_id,
                        tab=tab,
                        category_parameters = category_parameters
                    )


                    cell_parameters[tab_relation] = category_parameters[tab_relation]
                    #cell_parameters = LD.fill_sub_dict(cell_parameters, tab_relation, protocol_parameters,"new",relation_dict_2=tab_relation)

                else:

                    category_parameters, _,_ = self.fill_category(
                            category_id=category_id,
                            category_display_name =category_display_name,
                            category_name=category_name,
                            emmo_relation=emmo_relation,
                            default_template_id=default_template_id,
                            tab=tab,
                            category_parameters = category_parameters,
                            mass_loadings = None
                        )

                    cell_parameters[tab_relation] = category_parameters[tab_relation]

                    #cell_parameters = LD.fill_sub_dict(cell_parameters, tab_relation, category_parameters,"new",relation_dict_2=tab_relation)


            # cell is fully defined, its parameters are saved in the user_input dict
            self.user_input = self.LD.fill_linked_data_dict(self.user_input, cell_parameters)

            index +=1

        self.user_input = self.calc_indicators(self.user_input)
        self.update_json_LD()
        self.update_json_battmo_input()

    def update_json_LD(self):

        path_to_battmo_input = app_access.get_path_to_linked_data_input()

        # save formatted parameters in json file
        with open(path_to_battmo_input, "w") as new_file:
            json.dump(
                self.user_input,
                new_file,
                indent=3)

    def update_json_battmo_input(self):

        # Format parameters from json-LD to needed format
        path_to_battmo_formatted_input = app_access.get_path_to_battmo_formatted_input()

        # save formatted parameters in json file
        with open(path_to_battmo_formatted_input, "w") as new_file:
            json.dump(
                match_json_LD.get_batt_mo_dict_from_gui_dict(self.user_input),
                new_file,
                indent=3
            )

    @st.cache_data
    def calc_indicators(_self,user_input):

        input_dict = match_json_LD.GuiDict(user_input)
        with open(app_access.get_path_to_calculated_values(), 'r') as f:
            calculated_values = json.load(f)["calculatedParameters"]

        # Retrieve parameter values
        mf_ne = input_dict.ne.am.get("mass_fraction").get("value")
        mf_pe = input_dict.pe.am.get("mass_fraction").get("value")
        length = input_dict.cell.get("length").get("value")
        width = input_dict.cell.get("width").get("value")
        CC_thickness = input_dict.ne.properties.get("current_collector_thickness").get("value")
        packing_mass = input_dict.cell.get("packing_mass").get("value")
        c_max_ne = input_dict.ne.am.get("maximum_concentration").get("value")
        c_max_pe = input_dict.pe.am.get("maximum_concentration").get("value")
        densities = {
            "negative_electrode_active_material": input_dict.ne.am.get("density").get("value"),
            "positive_electrode_active_material": input_dict.pe.am.get("density").get("value"),
            "negative_electrode": calculated_values["effective_density"]["negative_electrode"],
            "positive_electrode": calculated_values["effective_density"]["positive_electrode"],
            "separator": input_dict.sep_mat.get("density").get("value"),
            "electrolyte": input_dict.elyte_mat.get("density").get("value")
        }
        porosities = {
            "negative_electrode": input_dict.ne.properties.get("coating_porosity").get("value"),
            "positive_electrode": input_dict.pe.properties.get("coating_porosity").get("value"),
            "separator": input_dict.sep_prop.get("porosity").get("value")
        }
        volumes = {
            "negative_electrode": length*width*input_dict.ne.properties.get("coating_thickness").get("value")*10**(-6),
            "positive_electrode": length*width*input_dict.pe.properties.get("coating_thickness").get("value")*10**(-6),
            "separator": length*width*input_dict.sep_prop.get("thickness").get("value")*10**(-6),
            "current_collector": length*width*CC_thickness*10**(-6)
        }

        li_stoich_max_ne =  input_dict.ne.am.get("maximum_lithium_stoichiometry").get("value")
        li_stoich_min_ne = input_dict.ne.am.get("minimum_lithium_stoichiometry").get("value")
        li_stoich_max_pe =  input_dict.pe.am.get("maximum_lithium_stoichiometry").get("value")
        li_stoich_min_pe = input_dict.pe.am.get("minimum_lithium_stoichiometry").get("value")
        n = input_dict.pe.am.get("number_of_electrons_transferred").get("value")

        # Specific capacity active materials
        specific_capacity_am_ne = _self.calc_specific_capacity_active_material(c_max_ne, densities["negative_electrode_active_material"],
                                                                     li_stoich_max_ne,
                                                                     li_stoich_min_ne,
                                                                     n)
        specific_capacity_am_pe = _self.calc_specific_capacity_active_material(c_max_pe, densities["positive_electrode_active_material"],
                                                                     li_stoich_max_pe,
                                                                     li_stoich_min_pe,
                                                                     n)

        raw_template_am_ne = db_helper.get_template_parameter_by_parameter_name("specific_capacity")
        raw_template_am_pe = db_helper.get_template_parameter_by_parameter_name("specific_capacity")
        # specific_cap_am_ne_parameter = self.formatter.initialize_parameters(raw_template_am_ne)
        # specific_cap_am_ne_parameter["selected_value"] = specific_capacity_am_ne
        # specific_cap_am_pe_parameter = self.formatter.initialize_parameters(raw_template_am_pe)
        # specific_cap_am_pe_parameter["selected_value"] = specific_capacity_am_pe

        specific_capacities_category_parameters_am_ne = _self.LD.setup_parameter_struct(raw_template_am_ne[0], value = specific_capacity_am_ne)
        specific_capacities_category_parameters_am_pe = _self.LD.setup_parameter_struct(raw_template_am_pe[1], value = specific_capacity_am_pe)

        # Specific capacity electrodes
        specific_capacity_ne = _self.calc_capacity_electrode(specific_capacity_am_ne,
                                                                    mf_ne,
                                                                    densities["negative_electrode"],
                                                                    volumes["negative_electrode"],
                                                                    porosities["negative_electrode"])
        specific_capacity_pe = _self.calc_capacity_electrode(specific_capacity_am_pe,
                                                                    mf_pe,
                                                                    densities["positive_electrode"],
                                                                    volumes["positive_electrode"],
                                                                    porosities["positive_electrode"])
        specific_capacities_electrodes = {
            "negative_electrode": specific_capacity_ne,
            "positive_electrode": specific_capacity_pe
        }
        raw_template_ne = db_helper.get_template_parameter_by_parameter_name("electrode_capacity")
        raw_template_pe = db_helper.get_template_parameter_by_parameter_name("electrode_capacity")
        specific_capacities_category_parameters_ne= _self.LD.setup_parameter_struct(raw_template_ne,value=specific_capacity_ne)
        specific_capacities_category_parameters_pe= _self.LD.setup_parameter_struct(raw_template_pe,value=specific_capacity_pe)

        # N to P ratio
        n_to_p_ratio = _self.calc_n_to_p_ratio(specific_capacities_electrodes)
        raw_template_np = db_helper.get_template_parameter_by_parameter_name("n_to_p_ratio")
        n_to_p_category_parameters= _self.LD.setup_parameter_struct(raw_template_np, value=n_to_p_ratio)

        # Cell Mass
        cc_mass = volumes["current_collector"]* 8950
        cell_mass, ne_mass, pe_mass = _self.calc_cell_mass(densities, porosities, volumes, cc_mass, packing_mass)
        raw_template_cellmass = db_helper.get_template_parameter_by_parameter_name("cell_mass")
        cell_mass_category_parameters= _self.LD.setup_parameter_struct(raw_template_cellmass,value=cell_mass)

        # Cell Capacity
        masses = {
            "negative_electrode": ne_mass,
            "positive_electrode": pe_mass
        }
        cell_capacity = _self.calc_cell_capacity(specific_capacities_electrodes)
        raw_template_cellcap = db_helper.get_template_parameter_by_parameter_name("nominal_cell_capacity")
        cell_capacity_category_parameters= _self.LD.setup_parameter_struct(raw_template_cellcap,value=cell_capacity)

        # Round trip efficiency
        raw_template_rte = db_helper.get_template_parameter_by_parameter_name("round_trip_efficiency")
        rte_category_parameters= _self.LD.setup_parameter_struct(raw_template_rte,value=None)


        # Include indicators in linked data input dict
        user_input = _self.LD.add_indicators_to_struct(user_input,n_to_p_category_parameters,cell_mass_category_parameters,cell_capacity_category_parameters,specific_capacities_category_parameters_ne,specific_capacities_category_parameters_pe,specific_capacities_category_parameters_am_ne,specific_capacities_category_parameters_am_pe,rte_category_parameters)

        return user_input

    def fill_category(self, category_id, category_display_name,category_name, emmo_relation, default_template_id, tab, category_parameters,mass_loadings,uploaded_input = None, selected_am_value_id=None):

        density_mix = None

        # get components associated with material parameter sets
        if category_name == "boundary_conditions":
            material_components = None
        else:
            material_components = db_helper.get_material_components_from_category_id(category_id)


        if category_name == "negative_electrode" or category_name == "positive_electrode":

            component_col, material_col, mass_fraction_col = tab.columns(3)
            component_col.markdown("**Component**")
            material_col.markdown("**Material**")


            material_component_id, component_name, _,_,_,_,material_comp_display_name,_,_,_,material_comp_default_template_id,material_comp_context_type,material_comp_context_type_iri,_ = material_components[0]
            parameter_id, \
                    name, \
                    model_name, \
                    par_class, \
                    difficulty, \
                    template_id, \
                    context_type, \
                    mf_context_type_iri, \
                    parameter_type, \
                    mf_unit, \
                    unit_name, \
                    mf_unit_iri, \
                    max_value, \
                    min_value, \
                    is_shown_to_user, \
                    description,  \
                    mf_display_name = tuple(np.squeeze(db_helper.get_mf_template_by_template_id(material_comp_default_template_id)))
            mass_fraction_col.write("[{}]({})".format(mf_display_name, mf_context_type_iri) + " / " + "[{}]({})".format(mf_unit, mf_unit_iri))

            mass_fraction_id_dict = {}
            density = {}

        elif category_name == "electrolyte" or category_name == "separator":
            mass_fraction_id_dict = None
            density = None
            mass_fraction_col = None
            component_col, material_col = tab.columns((1,2))


        if material_components:

            for material_component in material_components:
                component_parameters_ = []
                component_parameters = {}
                material_component_id, component_name, _,_,_,_,material_comp_display_name,_,_,_,material_comp_default_template_id,material_comp_context_type,material_comp_context_type_iri,_ = material_component

                component_col.write("[{}]({})".format(material_comp_display_name, material_comp_context_type_iri))
                component_col.text(" ")



                material_formatted_parameters,formatted_materials, selected_value_id, component_parameters_, emmo_relation, density = self.fill_material_components(component_name,component_parameters,component_parameters_,material_comp_default_template_id,material_component_id,material_col,material_comp_display_name,material_comp_context_type_iri,material_component,category_parameters,density,tab)

                component_parameters_ = self.LD.fill_component_dict(component_parameters_, "new")
                component_parameters = self.LD.setup_sub_dict(display_name=material_comp_display_name,context_type=material_comp_context_type, existence="new")
                component_parameters = self.LD.fill_component_dict(component_parameters=component_parameters_,existence="existing",dict=component_parameters)

                material_comp_relation = self.LD.get_relation(material_component_id,"component")
                category_parameters = self.LD.fill_sub_dict(category_parameters,material_comp_relation,component_parameters,"new",)
                material_choice = formatted_materials.options.get(selected_value_id).display_name

                material = formatted_materials.options.get(selected_value_id)
                parameters = material.parameters

                if material_choice == "User defined":
                    component_parameters_ = []
                    component_parameters = {}
                    category_parameters = self.fill_user_defined_expander(parameters,category_parameters,component_parameters,component_parameters_,density,tab,category_id,component_name,material_comp_display_name,material_component_id,material_comp_context_type,selected_value_id)

                component_parameters_ = []
                component_parameters = {}
                parameter, user_input, component_parameters_, emmo_relation, mass_fraction_id_dict = self.fill_mass_fraction_column(mass_fraction_col,category_id,material_comp_default_template_id,material_component_id,component_parameters_,mass_fraction_id_dict)

                if parameter:
                    component_parameters_ = self.LD.fill_component_dict(component_parameters_, "new")
                    component_parameters = self.LD.setup_sub_dict(dict=component_parameters,display_name=material_comp_display_name,context_type=material_comp_context_type)
                    component_parameters = self.LD.fill_component_dict(component_parameters_, "existing",dict=component_parameters)

                    material_comp_relation = self.LD.get_relation(material_component_id,"component")

                    category_parameters = self.LD.fill_component_dict(component_parameters,"existing",dict=category_parameters,relation=material_comp_relation)
        else:
            mass_fraction_id_dict = None
            density = None

        non_material_component = db_helper.get_non_material_components_from_category_id(category_id)

        non_material_component_id, non_material_component_name, _,_,_,_,non_material_comp_display_name,_,_,_,non_material_comp_default_template_id,non_material_comp_context_type,non_material_comp_context_type_iri,_ = non_material_component

        tab.markdown("**%s**" % non_material_comp_display_name)
        if category_name == "negative_electrode" or category_name == "positive_electrode":
            check_col, property_col, value_col= tab.columns((0.3,1,2))
        else:
            property_col, value_col= tab.columns(2)
            check_col = None

        non_material_parameters_sets = db_helper.get_non_material_set_id_by_component_id(non_material_component_id)

        component_parameters_ = []
        component_parameters = {}
        non_material_parameter,user_input,category_parameters, mass_loadings = self.fill_non_material_components(density,category_display_name,category_parameters,component_parameters,non_material_comp_display_name,non_material_comp_context_type, category_id,category_name,non_material_comp_default_template_id,non_material_component_id,property_col,value_col,non_material_parameters_sets,self.model_id, component_parameters_, check_col,non_material_component_name,tab, mass_fraction_id_dict, mass_loadings)

        category_parameters = self.fill_advanced_expander(tab,category_name, category_display_name, category_parameters)
        return category_parameters, emmo_relation, mass_loadings


    def fill_category_protocol(self, category_id,category_display_name, category_name, emmo_relation, default_template_id, tab,category_parameters):
        """
        same idea as fill category, just choosing a Protocol to set all params
        """
        component_parameters_ = []
        component_parameters = {}
        non_material_component = db_helper.get_non_material_components_from_category_id(category_id)

        non_material_component_id, non_material_component_name, _,_,_,_,non_material_comp_display_name,_,_,_,non_material_comp_default_template_id,non_material_comp_context_type,non_material_comp_context_type_iri,_ = non_material_component

        raw_template_parameters = db_helper.get_non_material_template_by_template_id(default_template_id,self.model_name)

        parameter_sets = db_helper.get_all_parameter_sets_by_component_id(non_material_component_id)

        parameter_sets_name_by_id = {}
        for id, name, _,_,_ in parameter_sets:
            parameter_sets_name_by_id[id] = name

        selected_parameter_set_id = tab.selectbox(
            label="Protocol",
            options=parameter_sets_name_by_id,
            key="{}_{}".format(category_id, "parameter_sets"),
            label_visibility="visible",
            format_func=lambda x: parameter_sets_name_by_id.get(x)
        )

        Protocol_name = parameter_sets_name_by_id[selected_parameter_set_id]

        raw_parameters = db_helper.extract_parameters_by_parameter_set_id(selected_parameter_set_id)

        formatted_parameters = self.formatter.format_parameters(raw_parameters, raw_template_parameters, parameter_sets_name_by_id)

        for parameter_id in formatted_parameters:
            parameter = formatted_parameters.get(parameter_id)

            if parameter.is_shown_to_user:


                selected_parameter_id = db_helper.get_parameter_id_from_template_parameter_and_parameter_set(
                    template_parameter_id=parameter.id,
                    parameter_set_id=selected_parameter_set_id
                )


                if parameter.options.get(selected_parameter_id):

                    name_col, input_col = tab.columns([1, 2])

                    if isinstance(parameter, NumericalParameter):

                        name_col.write("[{}]({})".format(parameter.display_name, parameter.context_type_iri) + " /" + "[{}]({})".format(parameter.unit, parameter.unit_iri))

                        user_input = input_col.number_input(
                            label=parameter.name,
                            value=parameter.options.get(selected_parameter_id).value,
                            min_value=parameter.min_value,
                            max_value=parameter.max_value,
                            key="input_{}_{}".format(non_material_component_id, parameter_id),
                            #format=parameter.format,
                            format = self.set_format(parameter.options.get(selected_parameter_id).value),
                            step=parameter.increment,
                            label_visibility="collapsed"
                        )
                    else:
                        value_list = ast.literal_eval(parameter.options.get(selected_parameter_id).value)
                        name_col.write(parameter.display_name)
                        user_input = input_col.selectbox(
                            label=parameter.display_name,
                            options=value_list,
                            key="input_{}_{}".format(non_material_component_id, parameter_id),
                            label_visibility="collapsed",
                        )
                    parameter.set_selected_value(user_input)

                component_parameters_ = self.LD.setup_parameter_struct(parameter,component_parameters=component_parameters_)

        parameter_details = {
                "label": "protocol_name",
                "value": {
                    "@type": "emmo:String",
                    "hasStringData": Protocol_name
                }
            }
        component_parameters_.append(parameter_details)
        component_parameters_ = self.LD.fill_component_dict(component_parameters_,"new")
        component_parameters = self.LD.setup_sub_dict(existence="new",display_name=non_material_comp_display_name,context_type=non_material_comp_context_type)
        component_parameters = self.LD.fill_component_dict(component_parameters_,"existing", dict=component_parameters)

        relation = self.LD.get_relation(non_material_component_id, "component")
        category_parameters = self.LD.fill_sub_dict(category_parameters,relation, component_parameters, "new")

        category_parameters= self.fill_advanced_expander(tab,category_name, category_display_name,category_parameters)

        return category_parameters

    def fill_user_defined_expander(self,parameters,category_parameters,component_parameters,component_parameters_,density,tab,category_id,component_name,material_comp_display_name,material_component_id,material_comp_context_type,selected_value_id):


        ex = tab.expander("Fill in '%s' parameters" % material_comp_display_name)

        with ex:
            for parameter_id in parameters:
                parameter = parameters.get(parameter_id)
                parameter_options =parameter.options.get(selected_value_id)



                if not isinstance(parameter, FunctionParameter):
                    property_col, value_col= ex.columns((1.5,2))

                    if isinstance(parameter, StrParameter):
                                property_col.write("[{}]({})".format(parameter.display_name, parameter.context_type_iri))


                                user_input = value_col.text_input(
                                label=parameter.name,
                                value=parameter_options.value,
                                key="input_{}_{}".format(category_id, parameter.id),
                                label_visibility="collapsed"
                                )

                    else:

                        property_col.write("[{}]({})".format(parameter.display_name, parameter.context_type_iri)+ " / " + "[{}]({})".format(parameter.unit, parameter.unit_iri))

                        user_input = value_col.number_input(
                            label=parameter.name,
                            value=parameter.default_value,
                            min_value=parameter.min_value,
                            max_value=parameter.max_value,
                            key="input_{}_{}".format(category_id, parameter.id),
                            # format=parameter.format,
                            format = self.set_format(parameter.default_value),
                            step=parameter.increment,
                            label_visibility="collapsed"
                            )

                elif isinstance(parameter, FunctionParameter):

                    st.divider()
                    st.write("[{}]({})".format(parameter.display_name, parameter.context_type_iri))

                    if component_name == "negative_electrode_active_material" or component_name == "positive_electrode_active_material":


                        ref_ocp = "ref_ocp_{}".format(material_component_id)
                        variables = "variables_{}".format(material_component_id)

                        if variables not in st.session_state:

                            st.session_state[variables] = r'c,cmax'
                        if ref_ocp not in st.session_state:
                            if component_name == "negative_electrode_active_material":
                                st.session_state[ref_ocp] = r'''1.9793 * exp(-39.3631*(c/cmax)) + 0.2482 - 0.0909 * tanh(29.8538*((c/cmax) - 0.1234)) - 0.04478 * tanh(14.9159*((c/cmax) - 0.2769)) - 0.0205 * tanh(30.4444*((c/cmax) - 0.6103))'''
                            elif component_name == "positive_electrode_active_material":
                                st.session_state[ref_ocp] = r'''-0.8090 * (c/cmax) + 4.4875 - 0.0428 * tanh(18.5138*((c/cmax) - 0.5542)) - 17.7326 * tanh(15.7890*((c/cmax) - 0.3117)) + 17.5842 * tanh(15.9308*((c/cmax) - 0.3120))'''

                        info = ex.toggle(label="OCP guidelines", key = "toggle_{}".format(material_component_id))
                        if info:
                            parameters,language  = ex.columns(2)
                            language.markdown(r'''
                                    **Allowed language**
                                    - Use '^' to indicate a superscript
                                    - Use '*' to indicate a multiplication
                                    - Use 'exp(a)' to indicate an exponential with power a
                                    - Use 'tanh()' for hyperbolic tangent
                                    - Use '/' for dividing

                                    ''')

                            parameters.markdown(r'''
                                    **Allowed variables**
                                    - Surface concentration : c
                                    - Maximum concentration : cmax
                                    - Temperature    : T
                                    - Reference Temperature : refT
                                    - State of charge: SOC



                                    ''')

                        ex.text_input(
                            label = "OCP",
                            value = st.session_state[ref_ocp],
                            key = ref_ocp,
                            label_visibility= "visible"
                        )
                        ref_ocp_str = st.session_state[ref_ocp]
                        func_ocpref = ex.toggle(label="Visualize OCP_ref", key = "toggle_vis_{}".format(material_component_id))

                        if func_ocpref:
                            # Convert the input string to a SymPy equation
                            try:
                                ref_ocp_str_py = ref_ocp_str.replace("^", "**")
                                eq_ref_ocp = sp.sympify(ref_ocp_str_py)
                                ex.latex("OCP = "+ sp.latex(eq_ref_ocp))

                            except sp.SympifyError:
                                ex.warning("Invalid equation input. Please enter a valid mathematical expression.")


                        ex.text_input(
                            label = "Variables (ex: c,T,refT,cmax)",
                            value = st.session_state[variables],
                            key = variables,
                            label_visibility= "visible"
                        )


                        variables_str = st.session_state[variables]


                        if variables_str == "":
                            ex.warning("You haven't specified the variables your equation depends on.")

                        else:
                            variables_array = variables_str.split(',')
                            #user_input = {'@type': 'emmo:String', 'hasStringData': {'function': ref_ocp_str, 'argument_list':variables_array}}
                            user_input = {'function': ref_ocp_str, 'argument_list':variables_array}


                    if component_name == "electrolyte_materials":



                        variables = "variables_{}".format(parameter_id)

                        if variables not in st.session_state:

                            st.session_state[variables] = r'c'

                        if "conductivity" not in st.session_state:
                            st.session_state.conductivity = r'''0.1297*(c/1000)^3 - 2.51*(c/1000)^(1.5) + 3.329*(c/1000)'''

                        if "diffusion_coefficient" not in st.session_state:
                            st.session_state.diffusion_coefficient = r'''8.794*10^(-11)*(c/1000)^2 - 3.972*10^(-10)*(c/1000) + 4.862*10^(-10)'''


                        info = ex.toggle(label="{} Guidelines".format(parameter.display_name), key = "toggle_{}".format(parameter_id))
                        if info:
                            parameters_col,language_col  = ex.columns(2)
                            language_col.markdown(r'''
                                    **Allowed language**
                                    - Use '^' to indicate a superscript
                                    - Use '*' to indicate a multiplication
                                    - Use 'exp(a)' to indicate an exponential with power a
                                    - Use 'tanh()' for hyperbolic tangent
                                    - Use '/' for dividing

                                    ''')

                            parameters_col.markdown(r'''
                                    **Allowed variables**
                                    - Surface concentration : c
                                    - Temperature    : T

                                    ''')

                        #quantity = ex.toggle(label="Create your own {} function".format(parameter.display_name), key = "toggle_quantity_{}".format(parameter_id))

                        #if quantity:
                        ex.text_input(
                            label = "{}".format(parameter.display_name),
                            value = st.session_state[parameter.name],
                            key = parameter.name,
                            label_visibility= "visible"
                        )
                        quantity_str = st.session_state[parameter.name]
                        func_quantity = ex.toggle(label="Visualize {}".format(parameter.display_name), key = "toggle_vis_{}".format(parameter_id))

                        if func_quantity:
                            # Convert the input string to a SymPy equation
                            try:
                                quantity_str_py = quantity_str.replace("^", "**")
                                eq_quantity = sp.sympify(quantity_str_py)
                                ex.latex("{} = ".format(parameter.display_name) + sp.latex(eq_quantity))

                            except sp.SympifyError:
                                ex.warning("Invalid equation input. Please enter a valid mathematical expression.")


                        ex.text_input(
                            label = "Variables (ex: c,T)",
                            value = st.session_state[variables],
                            key = variables,
                            label_visibility= "visible"
                        )


                        variables_str = st.session_state[variables]


                        if variables_str == "":
                            ex.warning("You haven't specified the variables your equation depends on.")

                        else:
                            variables_array = variables_str.split(',')
                            user_input = {'function': quantity_str, 'argument_list':variables_array}

                if parameter:

                    parameter.set_selected_value(user_input)
                    component_parameters_ = self.LD.setup_parameter_struct(parameter, component_parameters=component_parameters_)

                    if parameter.name == "density" and density:
                        density[material_component_id] = parameter.selected_value

            component_parameters_ = self.LD.fill_component_dict(component_parameters_,"new")

            component_parameters = self.LD.setup_sub_dict(existence="new",display_name=material_comp_display_name,context_type=material_comp_context_type)
            component_parameters = self.LD.fill_component_dict(component_parameters_,"existing",dict=component_parameters)

            material_comp_relation = self.LD.get_relation(material_component_id, "component")

            category_parameters = self.LD.fill_sub_dict(category_parameters, material_comp_relation, component_parameters,"new")

        return category_parameters

    def fill_non_material_components(self,density,category_display_name,category_parameters,component_parameters,non_material_comp_display_name,non_material_comp_context_type, category_id,category_name,non_material_comp_default_template_id,non_material_component_id,property_col,value_col,non_material_parameters_sets,model_id, component_parameters_, check_col,non_material_component_name,tab, mass_fraction_id_dict, mass_loadings):
        par_index = None
        non_material_parameters_raw_template = db_helper.get_non_material_template_by_template_id(non_material_comp_default_template_id,self.model_name)
        non_material_parameter_sets_name_by_id = {}
        non_material_parameter_set_id, non_material_parameters_set_name, _ ,_,_ = non_material_parameters_sets

        parameter_id = []
        non_material_parameters_raw = []
        for non_material_parameter_raw_template in non_material_parameters_raw_template:

            non_material_parameter_id,name,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_ = non_material_parameter_raw_template

            non_material_parameter_raw = db_helper.get_non_material_raw_parameter_by_template_parameter_id_and_parameter_set_id(non_material_parameter_id, non_material_parameter_set_id)[0]

            parameter_id.append(str(non_material_parameter_id))
            non_material_parameters_raw.append(non_material_parameter_raw)
        non_material_parameters_raw = tuple(non_material_parameters_raw)
        formatted_non_material_parameters = self.formatter.format_parameters(non_material_parameters_raw, non_material_parameters_raw_template,non_material_parameter_sets_name_by_id )

        if check_col:
            with check_col:
                placeholder = st.empty()
        ac = 1
        i = 0

        toggle_names = parameter_id


        parameter_names =[]
        # Initialize session state values outside of the loop
        state_prefix = "state_"  # A prefix for state keys

        for non_material_parameter_id in formatted_non_material_parameters:
            non_material_parameter = formatted_non_material_parameters.get(non_material_parameter_id)
            non_material_parameter_name = non_material_parameter.name
            parameter_names.append(non_material_parameter_name)
            checkbox_key = "checkbox_{}_{}".format(category_id, non_material_parameter_name)
            input_key = "input_{}_{}".format(category_id, non_material_parameter_name)
            state_key = state_prefix + checkbox_key
            input_value = "input_value_{}_{}".format(category_id, non_material_parameter_name)
            empty_key = "empty_{}_{}".format(category_id, non_material_parameter_name)
            state_count= "state_count_" + str(category_id)
            states = "states_" + str(category_id)
            states_to_count = "counts_" + str(category_id)

            if state_count not in st.session_state:
                st.session_state[state_count] = 0

            if states not in st.session_state:
                st.session_state[states] = {"coating_thickness": True, "coating_porosity": True, "mass_loading": False}

            if states_to_count not in st.session_state:
                st.session_state[states_to_count] = {}

            if checkbox_key not in st.session_state:

                    if non_material_parameter_name == "mass_loading":
                        st.session_state[checkbox_key] = False
                    else:
                        st.session_state[checkbox_key] = True

            if input_value not in st.session_state:
                st.session_state[input_value] = None

            if state_key not in st.session_state:
                states = []
                state = {}
                for id in parameter_id:
                    state[id] = False
                st.session_state[state_key] = state

        for non_material_parameter_id in formatted_non_material_parameters:
            non_material_parameter = formatted_non_material_parameters.get(non_material_parameter_id)
            non_material_parameter_name = non_material_parameter.name
            if non_material_parameter.is_shown_to_user:
                selected_parameter_id = db_helper.get_parameter_id_from_template_parameter_and_parameter_set(
                    template_parameter_id=non_material_parameter.id,
                    parameter_set_id=non_material_parameter_set_id
                )
            input_key = "input_{}_{}".format(category_id, non_material_parameter_name)
            checkbox_key = "checkbox_{}_{}".format(category_id, non_material_parameter_name)
            state_key = state_prefix + checkbox_key
            input_value = "input_value_{}_{}".format(category_id, non_material_parameter_name)
            empty_key = "empty_{}_{}".format(category_id, non_material_parameter_name)
            states_to_count = "counts_" + str(category_id)

            st.session_state[states_to_count][checkbox_key] = st.session_state[checkbox_key]

            if check_col:
                with value_col:
                    if i == 0:
                        co_th_place = st.empty()
                    elif i == 1:
                        co_po_place = st.empty()
                    elif i == 2:
                        ml_place = st.empty()


                with check_col:
                    state = st.toggle(label = checkbox_key,
                                    key = checkbox_key,
                                    value= st.session_state[checkbox_key],
                                    on_change = self.checkbox_input_connect,
                                    args = (checkbox_key, tab, category_id, non_material_parameter.name),
                                    label_visibility="collapsed")
                    st.text(" ")

            property_col.write("[{}]({})".format(non_material_parameter.display_name, non_material_parameter.context_type_iri)+ " / " + "[{}]({})".format(non_material_parameter.unit, non_material_parameter.unit_iri))

            property_col.text(" ")

            if not st.session_state[input_value]:
                st.session_state[input_value] = non_material_parameter.default_value

            else:
                pass

            if not check_col:
                user_input = value_col.number_input(
                    label=non_material_parameter.name,
                    value=non_material_parameter.default_value,
                    min_value=non_material_parameter.min_value,
                    max_value=non_material_parameter.max_value,
                    key=input_key,
                    # format=non_material_parameter.format,
                    format = self.set_format(non_material_parameter.options.get(selected_parameter_id).value),
                    step=non_material_parameter.increment,
                    label_visibility="collapsed",
                    disabled = False
                    )

            if check_col:
                if i ==0:
                    place = co_th_place
                elif i == 1:
                    place = co_po_place
                elif i ==2:
                    place = ml_place


                user_input = place.number_input(
                        label=non_material_parameter.name,
                        value=st.session_state[input_value],
                        min_value=non_material_parameter.min_value,
                        max_value=non_material_parameter.max_value,
                        key=input_key,
                        format=non_material_parameter.format,
                        step=non_material_parameter.increment,
                        label_visibility="collapsed",
                        disabled = not st.session_state[checkbox_key]
                        )

            if non_material_parameter:
                non_material_parameter.set_selected_value(user_input)
                component_parameters_ = self.LD.setup_parameter_struct(non_material_parameter, component_parameters=component_parameters_)

                if non_material_parameter.name == "coating_thickness":
                    thickness = non_material_parameter.selected_value
                elif non_material_parameter.name == "coating_porosity":
                    porosity = non_material_parameter.selected_value
                elif non_material_parameter.name == "mass_loading":
                    mass_loading= non_material_parameter.selected_value
                    mass_loadings[category_name]=mass_loading
            i +=1
            ac += 1

        if mass_fraction_id_dict:
            self.validate_mass_fraction(mass_fraction_id_dict, category_display_name,tab)

            density_mix = self.calc_density_mix(mass_fraction_id_dict, density)
            density_eff = self.calc_density_eff(density_mix, porosity)

            try:
                with open(app_access.get_path_to_calculated_values(), 'r') as f:
                    parameters_dict = json.load(f)
            except json.JSONDecodeError as e:
                st.write(app_access.get_path_to_calculated_values())


            parameters_dict["calculatedParameters"]["effective_density"][category_name] = density_eff

            with open(app_access.get_path_to_calculated_values(),'w') as f:
                json.dump(parameters_dict,f, indent=3)

        if check_col:
            states = "states_" + str(category_id)


            if st.session_state[states]["coating_thickness"] and st.session_state[states]["coating_porosity"]:
                for non_material_parameter_id in formatted_non_material_parameters:
                    non_material_parameter = formatted_non_material_parameters.get(non_material_parameter_id)
                    non_material_parameter_name = non_material_parameter.name
                    if non_material_parameter_name == "mass_loading":
                        par_value_ml = self.calc_mass_loading(density_mix, thickness, porosity)
                        par_index = 2
                        mass_loadings[category_name]=par_value_ml

                        with open(app_access.get_path_to_calculated_values(),'r') as f:
                            parameters_dict = json.load(f)

                        parameters_dict["calculatedParameters"]["mass_loadings"] = mass_loadings

                        with open(app_access.get_path_to_calculated_values(),'w') as f:
                            json.dump(parameters_dict,f, indent=3)

                        input_key = "input_key_{}_{}".format(category_id, "mass_loading")
                        empty_key = "empty_{}_{}".format(category_id,"mass_loading")
                        input_value = "input_value_{}_{}".format(category_id, "mass_loading")
                        checkbox_key= "checkbox_{}_{}".format(category_id, "mass_loading")

                        st.session_state[input_value] = par_value_ml
                        tab.write("Mass loading is now equal to {}".format(round(par_value_ml,2)))

                        if st.session_state[input_value] > non_material_parameter.max_value:
                            tab.warning("{} outside range: the {} should have a value between {} and {}".format(st.session_state[input_value],non_material_parameter.display_name, non_material_parameter.min_value, non_material_parameter.max_value))
                            st.session_state[input_value] = non_material_parameter.default_value

                        elif st.session_state[input_value] < non_material_parameter.min_value:
                            tab.warning("{} outside range: the {} should have a value between {} and {}".format(st.session_state[input_value],non_material_parameter.display_name, non_material_parameter.min_value, non_material_parameter.max_value))
                            st.session_state[input_value] = non_material_parameter.default_value



                        user_input = ml_place.number_input(
                            label=non_material_parameter.name,
                            value=st.session_state[input_value],
                            min_value=non_material_parameter.min_value,
                            max_value=non_material_parameter.max_value,
                            key=input_value+str(np.random.rand(100)),
                            # format=non_material_parameter.format,
                            format = self.set_format(st.session_state[input_value]),
                            step=non_material_parameter.increment,
                            label_visibility="collapsed",
                            disabled = not st.session_state[checkbox_key]
                            )


            elif st.session_state[states]["coating_thickness"] and st.session_state[states]["mass_loading"]:
                for non_material_parameter_id in formatted_non_material_parameters:
                    non_material_parameter = formatted_non_material_parameters.get(non_material_parameter_id)
                    non_material_parameter_name = non_material_parameter.name
                    if non_material_parameter_name == "coating_porosity":
                        par_value_co = self.calc_porosity(density_mix, thickness, mass_loading)
                        par_index = 1

                        input_key = "input_key_{}_{}".format(category_id, "coating_porosity")
                        empty_key = "empty_{}_{}".format(category_id,"coating_porosity")
                        input_value = "input_value_{}_{}".format(category_id, "coating_porosity")
                        checkbox_key= "checkbox_{}_{}".format(category_id, "coating_porosity")

                        st.session_state[input_value] = par_value_co
                        if st.session_state[input_value] > non_material_parameter.max_value:
                            tab.warning("{} outside range: the {} should have a value between {} and {}".format(st.session_state[input_value],non_material_parameter.display_name, non_material_parameter.min_value, non_material_parameter.max_value))
                            st.session_state[input_value] = non_material_parameter.default_value

                        elif st.session_state[input_value] < non_material_parameter.min_value:
                            tab.warning("{} outside range: the {} should have a value between {} and {}".format(st.session_state[input_value],non_material_parameter.display_name, non_material_parameter.min_value, non_material_parameter.max_value))
                            st.session_state[input_value] = non_material_parameter.default_value

                        user_input = co_po_place.number_input(
                            label=non_material_parameter.name,
                            value=st.session_state[input_value],
                            min_value=non_material_parameter.min_value,
                            max_value=non_material_parameter.max_value,
                            key=input_value+str(np.random.rand(100)),
                            # format=non_material_parameter.format,
                            format = self.set_format(st.session_state[input_value]),
                            step=non_material_parameter.increment,
                            label_visibility="collapsed",
                            disabled = not st.session_state[checkbox_key]
                            )

                        tab.write("Coating porosity is now equal to {}".format(round(par_value_co,2)))



            elif st.session_state[states]["mass_loading"] and st.session_state[states]["coating_porosity"]:
                for non_material_parameter_id in formatted_non_material_parameters:
                    non_material_parameter = formatted_non_material_parameters.get(non_material_parameter_id)
                    non_material_parameter_name = non_material_parameter.name
                    if non_material_parameter_name == "coating_thickness":
                        par_value_th = self.calc_thickness(density_mix, mass_loading, porosity)

                        input_key = "input_key_{}_{}".format(category_id, "coating_thickness")
                        empty_key = "empty_{}_{}".format(category_id,"coating_thickness")
                        input_value = "input_value_{}_{}".format(category_id, "coating_thickness")
                        checkbox_key= "checkbox_{}_{}".format(category_id, "coating_thickness")

                        st.session_state[input_value] = par_value_th
                        if st.session_state[input_value] > non_material_parameter.max_value:
                            tab.warning("{} outside range: the {} should have a value between {} and {}".format(st.session_state[input_value],non_material_parameter.display_name, non_material_parameter.min_value, non_material_parameter.max_value))
                            st.session_state[input_value] = non_material_parameter.default_value

                        elif st.session_state[input_value] < non_material_parameter.min_value:
                            tab.warning("{} outside range: the {} should have a value between {} and {}".format(st.session_state[input_value],non_material_parameter.display_name, non_material_parameter.min_value, non_material_parameter.max_value))
                            st.session_state[input_value] = non_material_parameter.default_value

                        user_input = co_th_place.number_input(
                            label=non_material_parameter.name,
                            value=st.session_state[input_value],
                            min_value=non_material_parameter.min_value,
                            max_value=non_material_parameter.max_value,
                            key=input_value+str(np.random.rand(100)),
                            # format=non_material_parameter.format,
                            format = self.set_format(st.session_state[input_value]),
                            step=non_material_parameter.increment,
                            label_visibility="collapsed",
                            disabled = not st.session_state[checkbox_key]
                            )
                        par_index = 0
                        tab.write("Coating thickness is now equal to {}".format(round(par_value_th,2)))
            else:
                st.session_state["input_value_{}_{}".format(category_id, "coating_thickness")] = None
                st.session_state["input_value_{}_{}".format(category_id, "coating_porosity")] = None
                st.session_state["input_value_{}_{}".format(category_id, "mass_loading")] = None
                st.experimental_rerun


            if st.session_state[input_value]:
                if component_parameters_:

                    component_parameters_ = self.LD.change_numerical_value(component_parameters_,par_index,st.session_state[input_value])
                    st.experimental_rerun

        component_parameters_ = self.LD.fill_component_dict(component_parameters_,"new")
        component_parameters = self.LD.setup_sub_dict(dict=component_parameters,display_name=non_material_comp_display_name,context_type=non_material_comp_context_type)
        component_parameters = self.LD.fill_component_dict(component_parameters_,"existing", dict=component_parameters)

        component_relation = self.LD.get_relation(non_material_component_id, "component")

        category_parameters = self.LD.fill_component_dict(component_parameters,"existing",dict=category_parameters,relation=component_relation)


        return non_material_parameter,user_input, category_parameters, mass_loadings

    def checkbox_input_connect(self,checkbox_key, tab, category_id, parameter_name):
        """
        Function needed for the toggles and number_inputs to work properly together.
        """
        #st.session_state[checkbox_key] = new_value
        state_count ="state_count_" + str(category_id)
        states = "states_" + str(category_id)
        states_to_count = "counts_" + str(category_id)


        if st.session_state[checkbox_key]==True:

            st.session_state[states_to_count][checkbox_key] = True
            st.session_state[states][parameter_name] = True
            st.session_state[state_count] = sum(st.session_state[states_to_count].values())

        elif st.session_state[checkbox_key]== False:

            st.session_state[states_to_count][checkbox_key] = False
            st.session_state[states][parameter_name] = False
            st.session_state[state_count] = sum(st.session_state[states_to_count].values())


        if st.session_state[state_count] >2:
            st.session_state[states_to_count][checkbox_key] = False
            st.session_state[checkbox_key] = False
            st.session_state[state_count] = sum(st.session_state[states_to_count].values())
            st.session_state[states][parameter_name] = False
            tab.warning("Only two of three parameters can be defined. The third one is calculated.")

        elif st.session_state[state_count] < 2:
            tab.warning("Enable at least two of three parameters.")
        else:
            pass


    def fill_material_components(self,component_name,component_parameters,component_parameters_,material_comp_default_template_id,material_component_id,material_col,material_comp_display_name,material_comp_context_type_iri,material_component,category_parameters, density,tab, emmo_relation = None):

        material_parameter_sets = []


        materials = db_helper.get_material_from_component_id(self.model_name,material_component_id)

        for material in materials:

            material_id,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_ = material
            # get parameter sets corresponding to component, then parameters from each set
            material_parameter_sets.append(tuple(db_helper.get_material_by_material_id(material_id)[0]))

        material_parameter_sets_name_by_id = {}
        for id, name, _,_,_ in material_parameter_sets:
            material_parameter_sets_name_by_id[id] = name

        material_raw_parameters = []
        for material_parameter_set_id in material_parameter_sets_name_by_id:
            material_raw_parameters.append(db_helper.extract_parameters_by_parameter_set_id(material_parameter_set_id))


        material_raw_template_parameters_sub = []
        material_raw_template_parameters = []
        ind = 0

        for material_parameter_set_id in material_parameter_sets_name_by_id:
            for material_raw_parameter in material_raw_parameters[ind]:
                _, \
                _, \
                _, \
                template_parameter_id, \
                _ = material_raw_parameter


                # get corresponding template parameters from db
                material_raw_template_parameters_sub.append(db_helper.get_parameter_by_template_parameter_id(template_parameter_id))

            material_raw_template_parameters.append(material_raw_template_parameters_sub)
            ind +=1

        material_raw_template_parameters = material_raw_template_parameters[0]
        all_basis_material_raw_template_parameters = db_helper.get_all_basis_material_by_template_id(material_comp_default_template_id,self.model_name)
       # material_raw_parameters = tuple(material_raw_parameters)
        # format all those parameters: use template parameters for metadata, and parameters for values.
        # all information is packed in a single python object
        # formatted_parameters is a dict containing those python objects

        material_formatted_parameters, formatted_component, formatted_components = self.formatter.format_parameter_sets(material_component,materials,material_parameter_sets,material_parameter_sets_name_by_id, material_raw_template_parameters, material_raw_parameters,material_component_id)

        index = 0
        ### Use this perhaps when input file utility is implemented #############
        # if st.session_state.upload:
        #     uploaded_id = self.uploaded_input[component_name]
        #     index = list(formatted_component.options.keys()).index(uploaded_id)
        #########################################################################

        selected_value_id = material_col.selectbox(
            label="[{}]({})".format(formatted_component.name, formatted_component.context_type_iri),
            options=list(formatted_component.options.keys()),
            index=index,
            key="select_{}".format(material_component_id),
            label_visibility="collapsed",
            format_func=lambda x: formatted_component.options.get(x).display_name,
            # on_change=reset_func,
            # args=(material_component_id, material_parameter_set_id, formatted_component)
        )

        # db_helper.reset_material_template_parameters(material_comp_default_template_id)


        if formatted_component:

            material_choice = formatted_component.options.get(selected_value_id)
            material_parameter_set_id = material_choice.parameter_set_id
            material = material_choice.display_name

            parameter_ids = material_choice.parameter_ids
            parameters = material_choice.parameters

            template_parameter_ids = []
            excluded_template_parameter_ids = []
            for template_parameter in all_basis_material_raw_template_parameters:

                id,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_ = template_parameter

                for parameter_id in parameters:

                    parameter = parameters.get(parameter_id)
                    set_parameter = parameter.options.get(material_parameter_set_id)
                    template_parameter_id = parameter.id

                    if set_parameter:
                        parameter.set_selected_value(set_parameter.value)
                        component_parameters_ = self.LD.setup_parameter_struct(parameter, component_parameters=component_parameters_)

                        template_parameter_ids.append(template_parameter_id)
                
                    if parameter.name == "density" and density != None:
                        if set_parameter:
                            density[material_component_id] = set_parameter.value
                            
                if id not in template_parameter_ids:
                    excluded_template_parameter_ids.append(id)
                
                

                
            if excluded_template_parameter_ids:

                expander_missing_parameters = tab.expander(label="Define {} missing material parameters".format(material))
                
                with expander_missing_parameters:
                    
                    for i,ex_id in enumerate(excluded_template_parameter_ids):
                    
                        template_parameter = db_helper.get_parameter_by_template_parameter_id(ex_id)
                        id,par_name,_,_,_,_,context_type,context_type_iri,par_type,unit,_,unit_iri,max_value,min_value,_,_,par_display_name = template_parameter

                        raw_parameters = db_helper.get_parameter_from_template_parameter_id(ex_id)
                        material_display_names = []
                        material_values = []
                        for raw_parameter in raw_parameters:
                            id,name,material_parameter_set_id,_,value = raw_parameter
                            
                            # if par_type == "float":
                            #     value = float(value)
                            #     min_value = float(min_value)
                            #     max_value = float(max_value)

                            # elif par_type == "int":
                            #     value = int(value)
                            #     min_value = int(min_value)
                            #     max_value = int(max_value)

                            material_name = db_helper.get_parameter_set_name_from_id(material_parameter_set_id)
                            material_display_name  = db_helper.get_material_display_name_from_name(material_name[0])


                            

                            if material_display_name:
                                if material_display_name[0][0] == "User defined": 
                                    pass
                                else:  
                                    material_display_names.append(material_display_name[0][0])
                            else:
                                material_display_names.append("Default")

                            material_values.append(value)
                            

                        st.write("[{}]({})".format(par_name, context_type_iri) + " / " + "[{}]({})".format(unit,unit_iri))
                        select_col,value_col = st.columns(2)

                        key_select = "select_{}_{}".format(material_component_id, id)
                        key_input_number = "input_number_{}_{}".format(material_component_id, id)

                        if key_select not in st.session_state:
                            st.session_state[key_select] = material_display_names[-1]

                        if key_input_number not in st.session_state:
                            st.session_state[key_input_number] = None

                        selected_parameter_set = select_col.selectbox(
                            label=par_display_name,
                            options=material_display_names,
                            key=key_select,
                            on_change=set_select,
                            args=(raw_parameters, material_display_names, material_values, material_component_id, id),
                            label_visibility="collapsed"
                        )

                        index = material_display_names.index(selected_parameter_set)
                        material_value = material_values[index]

                        if st.session_state[key_input_number] is None:
                            st.session_state[key_input_number] = material_value

                        user_input = value_col.text_input(
                            label=par_display_name,
                            value=st.session_state[key_input_number],
                            # min_value=min_value,
                            # max_value=max_value,
                            key=key_input_number,
                            on_change=set_number_input,
                            args=(material_component_id, id),
                            label_visibility="collapsed"
                        )

                        if user_input != st.session_state[key_input_number]:
                            st.session_state[key_input_number] = user_input

                        if par_name == "density" and density != None:
                            st.write(user_input)
                            density[material_component_id] = float(user_input)

                        if par_type == "int":
                            user_input = int(user_input)
                        elif par_type == "float":
                            user_input = float(user_input)
                        else:
                            user_input = str(user_input)

                        component_parameters_ = self.LD.setup_parameter_struct(template_parameter, component_parameters=component_parameters_, value = user_input)
                



            # con, cur = app_access.get_sqlite_con_and_cur()
            # data=cur.execute('''SELECT * FROM template_parameter WHERE id = 52''')
            # # Fetch all rows from the result
            # data = cur.fetchall()

            # # Check if there are columns to describe
            # if cur.description:
            #     # Print the column information
            #     print("Column names:", [col[0] for col in cur.description])

            # else:
            #     print("No columns to describe (empty result set)")

            # # Print the retrieved data
            # for row in data:
            #     st.write(row)

            # # Don't forget to close the cursor and connection when done
            # cur.close()
            # con.close()

        #self.set_material_parameter_difficulty(material_parameter_sets,material_raw_parameters,material_comp_default_template_id)

        return material_formatted_parameters,formatted_component, selected_value_id, component_parameters_, emmo_relation, density



    def fill_advanced_expander(self, tab,category_name, category_display_name,category_parameters):
        advanced_input=tab.expander("Show '{}' advanced parameters".format(category_display_name))
        all_advanced_tabs = advanced_input.tabs(db_helper.get_advanced_tab_display_names(self.model_name, category_name))

        db_tab_ids_advanced = db_helper.get_advanced_db_tab_id(self.model_name,category_name)
        index_advanced = 0
        for tab_advanced in all_advanced_tabs:

            db_tab_id_advanced = db_tab_ids_advanced[index_advanced][0]
            tab_context_type= db_helper.get_context_type_and_iri_by_id(db_tab_id_advanced)
            # tab_parameters = {
            #     "label": db_helper.get_advanced_tabs_display_names(self.model_id)[index_advanced],
            #     "@type": tab_context_type_iri
            # }
            # get tab's categories
            categories_advanced = db_helper.get_advanced_categories_from_tab_id(db_tab_id_advanced)


            #if len(categories_advanced) > 1:  # create one sub tab per category

            all_category_display_names = [a[7] for a in categories_advanced]
            if len(categories_advanced) > 1:  # create one sub tab per category
                all_sub_tabs = tab_advanced.tabs(all_category_display_names)
            else:
                all_sub_tabs = None

            i = 0

            for category in categories_advanced:
                component_parameters_ = []
                component_parameters = {}

                category_id, category_name,_,_,category_context_type, category_context_type_iri, emmo_relation, category_display_name, _, default_template_id, _ = category

                if all_sub_tabs:
                    tab_advanced = all_sub_tabs[i]

                i += 1

                non_material_component = tuple(db_helper.get_advanced_components_from_category_id(category_id))


                non_material_component_id, non_material_component_name, _,_,_,_,non_material_comp_display_name,_,_,_,non_material_comp_default_template_id,non_material_comp_context_type,non_material_comp_context_type_iri,_ = non_material_component

                raw_template_parameters = db_helper.get_advanced_template_by_template_id(default_template_id,self.model_name)


                if raw_template_parameters:

                    non_material_parameters_sets = np.squeeze(db_helper.get_non_material_set_id_by_component_id(non_material_component_id))
                    non_material_parameter_set_id, non_material_parameters_set_name, _ ,_,_ = non_material_parameters_sets

                    non_material_parameters_raw = []
                    for non_material_parameter_raw_template in raw_template_parameters:

                        non_material_parameter_id,name,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_ = non_material_parameter_raw_template


                        non_material_parameter = db_helper.get_advanced_parameters_by_parameter_set_id(non_material_parameter_id, non_material_parameter_set_id)

                        non_material_parameters_raw.append(non_material_parameter)

                    formatted_parameters = self.formatter.format_parameters(non_material_parameters_raw, raw_template_parameters, non_material_parameters_set_name)

                    for parameter_id in formatted_parameters:

                        parameter = formatted_parameters.get(str(parameter_id))

                        if parameter.is_shown_to_user:
                            selected_parameter_id = db_helper.get_parameter_id_from_template_parameter_and_parameter_set(
                                template_parameter_id=parameter.id,
                                parameter_set_id=non_material_parameter_set_id
                            )
                            #st_space(tab_advanced)
                            name_col, input_col = tab_advanced.columns(2)

                            if isinstance(parameter, NumericalParameter):
                                name_col.write("[{}]({})".format(parameter.display_name, parameter.context_type_iri) + " / " + "[{}]({})".format(parameter.unit, parameter.unit_iri))

                                user_input = input_col.number_input(
                                    label=parameter.name,
                                    value=parameter.options.get(selected_parameter_id).value,
                                    min_value=parameter.min_value,
                                    max_value=parameter.max_value,
                                    key="input_{}_{}".format(non_material_component_name, parameter.name),
                                    # format=parameter.format,
                                    format = self.set_format(parameter.options.get(selected_parameter_id).value),
                                    step=parameter.increment,
                                    label_visibility="collapsed"
                                )
                            else:
                                name_col.write(parameter.display_name)
                                user_input = input_col.selectbox(
                                    label=parameter.display_name,
                                    options=[parameter.options.get(selected_parameter_id).value],
                                    key="input_{}_{}".format(non_material_component_id, parameter_id),
                                    label_visibility="collapsed",
                                )
                            parameter.set_selected_value(user_input)

                            component_parameters_ = self.LD.setup_parameter_struct(parameter,component_parameters=component_parameters_)
                    component_parameters = self.LD.setup_sub_dict(display_name=non_material_comp_display_name, context_type=non_material_comp_context_type,existence="new")
                    component_parameters = self.LD.fill_component_dict(component_parameters_,existence="new", dict=component_parameters)
                    non_material_comp_relation = self.LD.get_relation(non_material_component_id, "component")
                    category_parameters = self.LD.fill_component_dict(component_parameters,"existing",dict=category_parameters,relation=non_material_comp_relation )



            return category_parameters

    def fill_mass_fraction_column(self,mass_fraction_col,category_id,material_comp_default_template_id,material_component_id,component_parameters_,mass_fraction_id_dict,emmo_relation=None):

        volume_fraction_raw_template = db_helper.get_mf_template_by_template_id(material_comp_default_template_id)

        parameter_set_id, parameters_set_name = db_helper.get_mf_parameter_set_id_by_component_id(material_component_id)
        if parameter_set_id:
            parameter_set_id = int(parameter_set_id)
            parameters_set_name = str(parameters_set_name)

            raw_values = tuple(np.squeeze(db_helper.get_mf_raw_parameter_by_parameter_set_id(parameter_set_id)))


            formatted_parameters = self.formatter.format_parameters(raw_values, volume_fraction_raw_template,parameters_set_name )


            for parameter_id in formatted_parameters:
                parameter = formatted_parameters.get(parameter_id)
                if parameter.is_shown_to_user:
                    selected_parameter_id = db_helper.get_parameter_id_from_template_parameter_and_parameter_set(
                        template_parameter_id=parameter.id,
                        parameter_set_id=parameter_set_id
            )

                user_input = mass_fraction_col.number_input(
                    label=parameter.name,
                    value=parameter.default_value,
                    min_value=parameter.min_value,
                    max_value=parameter.max_value,
                    key="input_{}_{}".format(category_id, parameter.id),
                    # format=parameter.format,
                    format = self.set_format(parameter.default_value),
                    step=parameter.increment,
                    label_visibility="collapsed"
                    )

                if parameter:
                    parameter.set_selected_value(user_input)

                    component_parameters = self.LD.setup_parameter_struct(parameter, component_parameters=component_parameters_)

                    mass_fraction_id_dict[material_component_id] = parameter.selected_value

            return parameter, user_input, component_parameters, emmo_relation, mass_fraction_id_dict
        else:
            return None, None, None, None,None

class JsonViewer:
    """
    Used in Run Simulation to be able to visualize the json contents.
    Might not be necessary, mostly used for debugging; TBD if you keep using it
    """
    def __init__(self, json_data, label="Json"):
        self.json_data = json_data
        self.label = label

        self.set_json_viewer()

    def set_json_viewer(self):
        viewer = st.expander(self.label)
        viewer.json(self.json_data)


class RunSimulation:
    """
    Rendering of Rus simulation section in the Simulation page

    Can be improved, think about removing the 'UPDATE' button.
    """
    def __init__(self, gui_parameters):
        self.header = "Run simulation"
        self.json_file = app_access.get_path_to_battmo_formatted_input()
        #self.style = get_theme_style()
        self.gui_parameters = gui_parameters
        #self.gui_file_data = json.dumps(gui_parameters, indent=2)
        #self.gui_file_name = "gui_output_parameters.json"
        #self.file_mime_type = "application/json"
        self.success = st.session_state.success
        self.api_url = "http://genie:8000/run_simulation"
        self.json_input_folder = 'BattMoJulia'
        self.json_input_file = 'battmo_formatted_input.json'
        self.julia_module_folder = 'BattMoJulia'
        self.julia_module = 'runP2DBattery.jl'
        self.results_folder = "results"
        self.temporary_results_file = "battmo_result"
        self.response_start = None

        self.set_section()

    def set_section(self):

        save_run = st.container()

        self.set_header(save_run)
        file_name = self.set_naming(save_run)
        self.set_buttons(save_run, file_name)

    def set_header(self,save_run):

        save_run.markdown("### " + self.header)
        save_run.text(" ")

    def set_naming(self,save_run):

        if 'checkbox_value' not in st.session_state:
            st.session_state.checkbox_value = False     

        checkbox_value = save_run.checkbox("Give your results a name. (The results will be automatically deleted on refreshing or closing of the browser.)", value=st.session_state.checkbox_value)
        st.session_state.checkbox_value = checkbox_value
        if checkbox_value:
            file_name = save_run.text_input("Give your results a name.", value = st.session_state["simulation_results_file_name"])

            st.session_state["simulation_results_file_name"] = file_name
        

    def set_buttons(self,save_run,file_name):

        #empty,run,empty2 = save_run.columns((0.3,1,1))

        # update = update.button(
        #     label="UPDATE",
        #     on_click=self.update_on_click,
        #     args= (save_run, )
        #     #help = "Update the parameter values."
        # )
        col1,col2 = save_run.columns((1,1))
        runing = col1.button(
            label="RUN",
            on_click= self.execute_api_on_click,
            args = (save_run,file_name ),
            type = "primary",
            use_container_width = True
            #help = "Run the simulation (after updating the parameters)."

        )

        results_page = col2.button(label = "Results",
                                   type = "primary",
                                    use_container_width=True
                                    )

        if results_page:
            switch_page("Results")


    def update_on_click(self,file_name):
        self.update_json_LD()
        self.update_json_battmo_input()

        st.session_state.update_par = True

        #save_run.success("Your parameters are saved! Run the simulation to get your results.")


    def update_json_LD(self):

        path_to_battmo_input = app_access.get_path_to_linked_data_input()

        # save formatted parameters in json file
        with open(path_to_battmo_input, "w") as new_file:
            json.dump(
                self.gui_parameters,
                new_file,
                indent=3)

    def update_json_battmo_input(self):

        # Format parameters from json-LD to needed format
        path_to_battmo_formatted_input = app_access.get_path_to_battmo_formatted_input()

        # save formatted parameters in json file
        with open(path_to_battmo_formatted_input, "w") as new_file:
            json.dump(
                match_json_LD.get_batt_mo_dict_from_gui_dict(self.gui_parameters),
                new_file,
                indent=3
            )

    def execute_api_on_click(self, save_run,file_name):


        ##############################
        # Set page directory to base level to allow for module import from different folder

        sys.path.insert(0, app_access.get_path_to_streamlit_dir())

        ##############################

        self.update_on_click(file_name)

        #if st.session_state.update_par != True:
            # save_run.warning("""The parameters are not updated yet.
            #             Simulation not initiated. Click on the 'UPDATE' button first.""")

        # elif st.session_state.update_par == True:

        with open(app_access.get_path_to_battmo_formatted_input(), 'r') as j:
            json_data = json.loads(j.read())

        # Set the Content-Type header to application/json
        headers = {'Content-Type': 'application/json'}

        response_start = requests.post(self.api_url, json=json_data)

        if response_start.status_code == 200:

            st.session_state.reponse = True

            with open(app_access.get_path_to_battmo_results(), "wb") as f:
                    f.write(response_start.content)

            # file_like_object = io.BytesIO(response_start.content)
            # with h5py.File(file_like_object, 'r') as hdf5_file:

            #     st.write(hdf5_file["concentrations"]["electrolyte"]["elyte_c_state_1"][()])

            if st.session_state["checkbox_value"] == False:

                # random_file_name = str(uuid4())
                random_number = random.randint(1000, 9999)
                random_file_name = str(random_number)
                st.session_state["simulation_results_file_name"] = "data_" + random_file_name

            self.success = DivergenceCheck(save_run,response_start.content).success


        else:
                st.session_state.reponse = False
                # st.error("The data has not been retrieved succesfully, most probably due to an unsuccesful simulation")
                # st.session_state.success = False
                # self.success = False

                self.success = DivergenceCheck(save_run,False).success


        # with open("BattMo_results.pkl", "rb") as f:
        #     data = pickle.load(f)



        # with open(os.path.join(app_access.get_path_to_gui_dir(), self.results_folder, uuids), "rb") as pickle_result:
        #     result = pickle.load(pickle_result)

        # with open(os.path.join(app_access.get_path_to_python_dir(), self.temporary_results_file), "wb") as new_pickle_file:
        #             pickle.dump(result, new_pickle_file)


        # clear cache to get new data in hdf5 file (cf Plot_latest_results)
        st.cache_data.clear()


        st.session_state.update_par = False
        st.session_state.sim_finished = True


class DivergenceCheck:
    """
    Checks if the simulation is fully executed. If not it provides a warning to the user.
    If the simulation is fully executed, it shows the battmo logging if there is any.
    """
    def __init__(self,save_run,response= None):

        self.response = response
        self.save_run = save_run
        self.success = st.session_state.success
        self.check_for_divergence()


    def check_for_divergence(self):

       if self.response:

            results,_ = app_controller.get_results_data(None).get_results_data(None)

            N = self.get_timesteps_setting()
            number_of_states, log_messages = self.get_timesteps_execution(results)

            self.divergence_check_logging(N,number_of_states, log_messages,results)

    def get_timesteps_setting(self):

        # retrieve saved parameters from json file
        with open(app_access.get_path_to_battmo_formatted_input()) as json_gui_parameters:
            gui_parameters = json.load(json_gui_parameters)

        N = gui_parameters["TimeStepping"]["numberOfTimeSteps"]

        return N

    def get_timesteps_execution(self, results):

        [
            log_messages,
            number_of_states,
            cell_voltage,
            cell_current,
            time_values,
            negative_electrode_grid,
            negative_electrode_grid_bc,
            electrolyte_grid,
            electrolyte_grid_bc,
            positive_electrode_grid,
            positive_electrode_grid_bc,
            negative_electrode_concentration,
            electrolyte_concentration,
            positive_electrode_concentration,
            negative_electrode_potential,
            electrolyte_potential,
            positive_electrode_potential

        ] = results

        return number_of_states, log_messages
    
    def add_indicators_to_results(self, indicators, response):

        response = io.BytesIO(response)

        response.seek(0)

        print(indicators["NegativeElectrode"]["massLoading"]["unit"])
        with h5py.File(response, 'a') as hdf5_file:

            indocators_group = hdf5_file.create_group("indicators")
            cell = indocators_group.create_group("cell")
            negative_electrode = indocators_group.create_group("negative_electrode")
            negative_electrode_electrode = negative_electrode.create_group("electrode")
            negative_electrode_am = negative_electrode.create_group("active_material")
            positive_electrode = indocators_group.create_group("positive_electrode")
            positive_electrode_electrode = positive_electrode.create_group("electrode")
            positive_electrode_am = positive_electrode.create_group("active_material")

            

            NE_ml = negative_electrode_electrode.create_group("mass_loading")
            NE_ml.create_dataset("value", data = indicators["NegativeElectrode"]["massLoading"]["value"])
            NE_ml.create_dataset("unit", data = indicators["NegativeElectrode"]["massLoading"]["unit"].encode('utf-8'), dtype=h5py.string_dtype(encoding='utf-8'))

            NE_thi = negative_electrode_electrode.create_group("coating_thickness")
            NE_thi.create_dataset("value", data = indicators["NegativeElectrode"]["thickness"]["value"])
            NE_thi.create_dataset("unit", data = indicators["NegativeElectrode"]["thickness"]["unit"].encode('utf-8'), dtype=h5py.string_dtype(encoding='utf-8'))

            NE_po = negative_electrode_electrode.create_group("coating_porosity")
            NE_po.create_dataset("value", data = indicators["NegativeElectrode"]["porosity"]["value"])
            NE_po.create_dataset("unit", data = indicators["NegativeElectrode"]["porosity"]["unit"].encode('utf-8'), dtype=h5py.string_dtype(encoding='utf-8'))

            NE_cap = negative_electrode_electrode.create_group("capacity")
            NE_cap.create_dataset("value", data = indicators["NegativeElectrode"]["specificCapacity"]["value"])
            NE_cap.create_dataset("unit", data = indicators["NegativeElectrode"]["specificCapacity"]["unit"].encode('utf-8'), dtype=h5py.string_dtype(encoding='utf-8'))

            NE_am_cap = negative_electrode_am.create_group("specific_capacity")
            NE_am_cap.create_dataset("value", data = indicators["NegativeElectrode"]["ActiveMaterial"]["specificCapacity"]["value"])
            NE_am_cap.create_dataset("unit",data =  indicators["NegativeElectrode"]["ActiveMaterial"]["specificCapacity"]["unit"].encode('utf-8'), dtype=h5py.string_dtype(encoding='utf-8'))
        
            PE_ml = positive_electrode_electrode.create_group("mass_loading")
            PE_ml.create_dataset("value", data = indicators["PositiveElectrode"]["massLoading"]["value"])
            PE_ml.create_dataset("unit", data = indicators["PositiveElectrode"]["massLoading"]["unit"].encode('utf-8'), dtype=h5py.string_dtype(encoding='utf-8'))

            PE_thi = positive_electrode_electrode.create_group("coating_thickness")
            PE_thi.create_dataset("value", data = indicators["PositiveElectrode"]["thickness"]["value"])
            PE_thi.create_dataset("unit", data = indicators["PositiveElectrode"]["thickness"]["unit"].encode('utf-8'), dtype=h5py.string_dtype(encoding='utf-8'))

            PE_po = positive_electrode_electrode.create_group("coating_porosity")
            PE_po.create_dataset("value", data = indicators["PositiveElectrode"]["porosity"]["value"])
            PE_po.create_dataset("unit", data = indicators["PositiveElectrode"]["porosity"]["unit"].encode('utf-8'), dtype=h5py.string_dtype(encoding='utf-8'))

            PE_cap = positive_electrode_electrode.create_group("capacity")
            PE_cap.create_dataset("value", data = indicators["PositiveElectrode"]["specificCapacity"]["value"])
            PE_cap.create_dataset("unit", data = indicators["PositiveElectrode"]["specificCapacity"]["unit"].encode('utf-8'), dtype=h5py.string_dtype(encoding='utf-8'))

            PE_am_cap = positive_electrode_am.create_group("specific_capacity")
            PE_am_cap.create_dataset("value", data = indicators["PositiveElectrode"]["ActiveMaterial"]["specificCapacity"]["value"])
            PE_am_cap.create_dataset("unit", data = indicators["PositiveElectrode"]["ActiveMaterial"]["specificCapacity"]["unit"].encode('utf-8'), dtype=h5py.string_dtype(encoding='utf-8'))

            cell_mass = cell.create_group("cell_mass")
            cell_mass.create_dataset("value", data = indicators["Cell"]["cellMass"]["value"])
            cell_mass.create_dataset("unit", data = indicators["Cell"]["cellMass"]["unit"].encode('utf-8'), dtype=h5py.string_dtype(encoding='utf-8'))

            cell_cap = cell.create_group("nominal_cell_capacity")
            cell_cap.create_dataset("value", data = indicators["Cell"]["nominalCellCapacity"]["value"])
            cell_cap.create_dataset("unit", data = indicators["Cell"]["nominalCellCapacity"]["unit"].encode('utf-8'), dtype=h5py.string_dtype(encoding='utf-8'))

            cell_np = cell.create_group("n_to_p_ratio")
            cell_np.create_dataset("value", data = indicators["Cell"]["NPRatio"]["value"])
            cell_np.create_dataset("unit", data = indicators["Cell"]["NPRatio"]["unit"].encode('utf-8'), dtype=h5py.string_dtype(encoding='utf-8'))

            hdf5_file.flush()

            response.seek(0)
   
            return response.getvalue()

    def divergence_check_logging(self,N, number_of_states,log_messages,results):

        if self.response == False:
            self.save_run.error("The data has not been retrieved succesfully, most probably due to an unsuccesful simulation")
            st.session_state.success = False
            self.success = False

        elif self.response:
            if number_of_states == 0:
                self.success = False

                st.session_state.success = False

                if len(log_messages[()]) > 1:
                    c = self.save_run.container()
                    c.error("Simulation wasn't successful unfortunately. Some errors were produced, see the logging.")
                    c.markdown("***Logging:***")

                    log_message = ''' \n'''
                    for message in log_messages[()]:
                        log_message = log_message + message+ '''\n'''

                    c.code(log_message + ''' \n''')
                else:

                    self.save_run.error("Simulation wasn't successful unfortunately.")

            else:
                temp_file_name = st.session_state["simulation_results_file_name"]
                file_path = os.path.join(st.session_state['temp_dir'], temp_file_name +".hdf5")


                self.success = True
                self.save_run.success(f"""Simulation finished successfully! Check the results on the 'Results' page.""")# \n\n
                                 
                                # Your results are stored under the following name: {temp_file_name}""")
                st.session_state.success = True

                

                # if self.response:
                if not isinstance(self.response,bool):
                    with open(app_access.get_path_to_linked_data_input(), 'r') as f:
                        gui_parameters = json.load(f)

                    indicators = match_json_LD.get_indicators_from_gui_dict(gui_parameters)

                    with open(app_access.get_path_to_indicator_values(), 'w') as f:
                        json.dump(indicators, f, indent=3)

                    # with open(app_access.get_path_to_battmo_results(), "wb") as f:
                    #     f.write(results)

                    self.response = self.add_indicators_to_results(indicators, self.response)

                    with open(file_path, "wb") as f:
                        f.write(self.response)

                # except:
                #     pass
        else:

            pass








class DownloadParameters:
    """
    Rendering of Run Simulation tab
    """
    def __init__(self,gui_parameters):
        self.run_header = "Run Simulation"
        self.run_info = """ The BattMo toolbox used for running the simulations is Julia based. Julia is a compiled language and because of this, the first
                            simulation will be slow, but next simulations will be very quick."""


        self.gui_button_label = "Save GUI output parameters"
        self.battmo_button_label = "Save BattMo input parameters"
        self.gui_parameters = gui_parameters
        # retrieve saved parameters from json file
        # with open(app_access.get_path_to_linked_data_input()) as json_gui_parameters:
        #     self.gui_parameters = json.load(json_gui_parameters)

        self.download_header = "Download parameters"
        self.download_label = "JSON LD format"
        self.gui_file_data = json.dumps(self.gui_parameters, indent=2)
        self.gui_file_name = "JSON_ld_parameters.json"
        self.file_mime_type = "application/JSON"

        # retrieve saved formatted parameters from json file
        with open(app_access.get_path_to_battmo_formatted_input(),'r') as json_formatted_gui_parameters:
            self.formatted_gui_parameters = json.load(json_formatted_gui_parameters)

        self.download_label_formatted_parameters = "BattMo format"
        self.formatted_parameters_file_data = json.dumps(self.formatted_gui_parameters, indent=2)
        self.formatted_parameters_file_name = "battmo_formatted_parameters.json"


        self.set_submit_button()

    def update_on_click(self):

        self.update_json_LD()
        self.update_json_battmo_input()

        #st.session_state.update_par = True

        #save_run.success("Your parameters are saved! Run the simulation to get your results.")

    def update_json_LD(self):

        path_to_battmo_input = app_access.get_path_to_linked_data_input()

        # save formatted parameters in json file
        with open(path_to_battmo_input, "w") as new_file:
            json.dump(
                self.gui_parameters,
                new_file,
                indent=3)


    def update_json_battmo_input(self):

        # Format parameters from json-LD to needed format
        path_to_battmo_formatted_input = app_access.get_path_to_battmo_formatted_input()

        # save formatted parameters in json file
        with open(path_to_battmo_formatted_input, "w") as new_file:
            json.dump(
                match_json_LD.get_batt_mo_dict_from_gui_dict(self.gui_parameters),
                new_file,
                indent=3
            )

    def set_submit_button(self):

        with st.sidebar:
            # set Download header
            st.markdown("### " + self.download_header)

            # set download button
            st.download_button(
                label=self.download_label,
                on_click= self.update_on_click(),
                data=self.gui_file_data,
                file_name=self.gui_file_name,
                mime=self.file_mime_type
            )

            st.download_button(
                label=self.download_label_formatted_parameters,
                on_click= self.update_on_click(),
                data=self.formatted_parameters_file_data,
                file_name=self.formatted_parameters_file_name,
                mime=self.file_mime_type
            )


class LoadImages:
    """
    Get images as python objects
    - logo is used for page_icon and in "About" section
    - image_dict stores images used in Define_parameters
    """
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

        # images are resized for better rendering

        #l, w = 80, 80

        def image_open(file_name):
            image = Image.open(join_path(file_name))
            return image #.resize((l, w))

        """
        This dict has to be refactored, it needs at least:
        - images for every parameter category
        - proper naming
        - remove useless items
        """
        return {
            "4": image_open("cell_coin.png"),
            "9": image_open("cell_prismatic.png"),
            "3": image_open("separator_new_icon.png"),
            "1": image_open("plus_icon.png"),
            "0": image_open("minus_icon.png"),
            "2": image_open("electrolyte_icon.png"),
            "5": image_open("bc_icon.png"),
            "6": image_open("protocol_icon.png"),
            "7": image_open("current.png"),
            "8": image_open("cell_cylindrical.png")
        }


class SetModelDescription():
    """
    Used to render the 'Available models' section on the Materials and models page
    """
    def __init__(self):

        self.model = "P2D"
        self.hasNumericalData = "hasNumericalData"
        self.hasStringData = "hasStringData"
        self.set_model_description()

    def set_model_description(self):
        models_as_dict = db_helper.get_models_as_dict()
        P2D_model= db_helper.get_model_parameters_as_dict("P2D")
        P2D_model_description = db_helper.get_model_description(self.model)[0][0]

        st.title("The available models")

        model = st.expander(self.model)

        with model:

            st.markdown("""**Includes** """)
            st.markdown("- Thermal effects = <span style='color: blue;'>" + str(P2D_model[0]["value"][self.hasStringData]) + "</span>", unsafe_allow_html=True)
            st.markdown("- Current collector = <span style='color: blue;'>" + str(P2D_model[1]["value"][self.hasStringData]) + "</span>", unsafe_allow_html=True)
            st.markdown("- Solid Diffusion model = <span style='color: blue;'>" + str(P2D_model[2]["value"][self.hasStringData]) + "</span>", unsafe_allow_html=True)
            st.markdown("- Solid Diffusion model type = <span style='color: blue;'>" + str(P2D_model[3]["value"][self.hasStringData]) + "</span>", unsafe_allow_html=True)
            st.markdown(" ")
            st.markdown("**Description**")
            st.markdown(P2D_model_description)


class GetResultsData():
    """
    Used to retrieve and format the results of the simulation.
    """
    def __init__(self, file_names):
        self.results = None
        self.get_results_data(file_names)

    def get_results_data(self, file_names):

        results,indicators = self.retrieve_results(file_names)
        formatted_results, indicators = self.format_results(results,indicators,file_names)
        self.results = formatted_results
        # file_path = os.path.join(st.session_state['temp_dir'], uploaded_file[0].name)
        # with open(file_path, "wb") as f:
        #     f.write(uploaded_file[0].getbuffer())
        return self.results, indicators

    def retrieve_results(self,file_names):
        if isinstance(file_names,list):
            results = []
            indicators = []
            for file_name in file_names:
                file_path = os.path.join(st.session_state.temp_dir,file_name)
                result = h5py.File(file_path, "r")
                result,indicator = self.translate_results(result)

                results.append(result)
                indicators.append(indicator)
        elif isinstance(file_names, str):
      
            file_path = os.path.join(st.session_state.temp_dir,file_names)
            result = h5py.File(file_path, "r")
            results,indicators = self.translate_results(result)
            

        else:
            file_path = app_access.get_path_to_battmo_results()
            results = h5py.File(file_path, "r")
            indicators = None

        return results,indicators

        

    def translate_results(self,result):
        # Retrieve the attributes
        number_of_states = result["number_of_states"][()]

        # Retrieve datasets
        log_messages = result["log_messages"][:]
        time_values = result["time_values"][:]
        cell_voltage = result["cell_voltage"][:]
        cell_current = result["cell_current"][:]

        # Retrieve grid datasets
        negative_electrode_grid = np.squeeze(result["grids/negative_electrode_grid"][:])
        positive_electrode_grid = np.squeeze(result["grids/positive_electrode_grid"][:])
        electrolyte_grid = np.squeeze(result["grids/electrolyte_grid"][:])
        negative_electrode_grid_bc = result["grids/negative_electrode_grid_bc"][:]
        electrolyte_grid_bc = result["grids/electrolyte_grid_bc"][:]
        positive_electrode_grid_bc = result["grids/positive_electrode_grid_bc"][:]

        # Retrieve concentration datasets
        negative_electrode_concentration = [result["concentrations/negative_electrode/ne_c_state_{}".format(i+1)][:] for i in range(number_of_states)]
        positive_electrode_concentration = [result["concentrations/positive_electrode/pe_c_state_{}".format(i+1)][:] for i in range(number_of_states)]
        electrolyte_concentration = [result["concentrations/electrolyte/elyte_c_state_{}".format(i+1)][:] for i in range(number_of_states)]

        # Retrieve potential datasets
        negative_electrode_potential = [result["potentials/negative_electrode/ne_p_state_{}".format(i+1)][:] for i in range(number_of_states)]
        positive_electrode_potential = [result["potentials/positive_electrode/pe_p_state_{}".format(i+1)][:] for i in range(number_of_states)]
        electrolyte_potential = [result["potentials/electrolyte/elyte_p_state_{}".format(i+1)][:] for i in range(number_of_states)]

        try:
            ne_electrode_ml_value = result["indicators/negative_electrode/electrode/mass_loading/value"][()]
            ne_electrode_ml_unit = result["indicators/negative_electrode/electrode/mass_loading/unit"][()].decode('utf-8')
            ne_electrode_thi_value = result["indicators/negative_electrode/electrode/coating_thickness/value"][()]
            ne_electrode_thi_unit = result["indicators/negative_electrode/electrode/coating_thickness/unit"][()].decode('utf-8')
            ne_electrode_po_value = result["indicators/negative_electrode/electrode/coating_porosity/value"][()]
            ne_electrode_po_unit = result["indicators/negative_electrode/electrode/coating_porosity/unit"][()].decode('utf-8')
            ne_electrode_cap_value = result["indicators/negative_electrode/electrode/capacity/value"][()]
            ne_electrode_cap_unit = result["indicators/negative_electrode/electrode/capacity/unit"][()].decode('utf-8')
            ne_am_cap_value = result["indicators/negative_electrode/active_material/specific_capacity/value"][()]
            ne_am_cap_unit = result["indicators/negative_electrode/active_material/specific_capacity/unit"][()].decode('utf-8')

            pe_electrode_ml_value = result["indicators/positive_electrode/electrode/mass_loading/value"][()]
            pe_electrode_ml_unit = result["indicators/positive_electrode/electrode/mass_loading/unit"][()].decode('utf-8')
            pe_electrode_thi_value = result["indicators/positive_electrode/electrode/coating_thickness/value"][()]
            pe_electrode_thi_unit = result["indicators/positive_electrode/electrode/coating_thickness/unit"][()].decode('utf-8')
            pe_electrode_po_value = result["indicators/positive_electrode/electrode/coating_porosity/value"][()]
            pe_electrode_po_unit = result["indicators/positive_electrode/electrode/coating_porosity/unit"][()].decode('utf-8')
            pe_electrode_cap_value = result["indicators/positive_electrode/electrode/capacity/value"][()]
            pe_electrode_cap_unit = result["indicators/positive_electrode/electrode/capacity/unit"][()].decode('utf-8')
            pe_am_cap_value = result["indicators/positive_electrode/active_material/specific_capacity/value"][()]
            pe_am_cap_unit = result["indicators/positive_electrode/active_material/specific_capacity/unit"][()].decode('utf-8')

            cell_cap_value = result["indicators/cell/nominal_cell_capacity/value"][()]
            cell_cap_unit = result["indicators/cell/nominal_cell_capacity/unit"][()].decode('utf-8')
            cell_mass_value = result["indicators/cell/cell_mass/value"][()]
            cell_mass_unit = result["indicators/cell/cell_mass/unit"][()].decode('utf-8')
            cell_np_value = result["indicators/cell/n_to_p_ratio/value"][()]
            cell_np_unit = result["indicators/cell/n_to_p_ratio/unit"][()].decode('utf-8')

            indicators = [
                ne_electrode_ml_value,
                ne_electrode_ml_unit,
                ne_electrode_thi_value,
                ne_electrode_thi_unit,
                ne_electrode_po_value,
                ne_electrode_po_unit,
                ne_electrode_cap_value,
                ne_electrode_cap_unit,
                ne_am_cap_value,
                ne_am_cap_unit ,

                pe_electrode_ml_value,
                pe_electrode_ml_unit,
                pe_electrode_thi_value,
                pe_electrode_thi_unit,
                pe_electrode_po_value,
                pe_electrode_po_unit ,
                pe_electrode_cap_value ,
                pe_electrode_cap_unit,
                pe_am_cap_value ,
                pe_am_cap_unit,

                cell_cap_value ,
                cell_cap_unit,
                cell_mass_value,
                cell_mass_unit ,
                cell_np_value ,
                cell_np_unit,

                ]
        except Exception as e:

            indicators = None
        

        result = [
            log_messages,
            number_of_states,
            cell_voltage,
            cell_current,
            time_values,
            negative_electrode_grid,
            negative_electrode_grid_bc,
            electrolyte_grid,
            electrolyte_grid_bc,
            positive_electrode_grid,
            positive_electrode_grid_bc,
            negative_electrode_concentration,
            electrolyte_concentration,
            positive_electrode_concentration,
            negative_electrode_potential,
            electrolyte_potential,
            positive_electrode_potential

            ]
        

        
        
        return result, indicators



    def format_results(self,results,indicators,file_names):

        if file_names == None:
            file_names = [file_names]

        list = []
        for file_name in file_names:

            if file_name:
                results = results
                indicators = indicators
            else:
                result = results
                result,indicators = self.translate_results(result)
                results = result



            # length_1d_ne = len(negative_electrode_concentration_jl)
            # length_2d_ne = len(negative_electrode_concentration_jl[0])
            # length_1d_pe = len(positive_electrode_concentration_jl)
            # length_2d_pe = len(positive_electrode_concentration_jl[0])
            # length_1d_el = len(electrolyte_concentration_jl)
            # length_2d_el = len(electrolyte_concentration_jl[0])
            # negative_electrode_concentration = np.zeros((length_1d_ne,length_2d_ne))
            # positive_electrode_concentration = np.zeros((length_1d_pe,length_2d_pe))
            # negative_electrode_potential = np.zeros((length_1d_ne,length_2d_ne))
            # positive_electrode_potential = np.zeros((length_1d_pe,length_2d_pe))
            # electrolyte_concentration = np.zeros((length_1d_el,length_2d_el))
            # electrolyte_potential = np.zeros((length_1d_el,length_2d_el))

            # for i in range(length_1d_pe):
            #     for j in range(length_2d_pe):
            #         pe_c_sub = positive_electrode_concentration_jl[i]
            #         pe_p_sub = positive_electrode_potential_jl[i]
            #         positive_electrode_concentration[i,j] = pe_c_sub[j]
            #         positive_electrode_potential[i,j] = pe_p_sub[j]

            # for i in range(length_1d_el):
            #     for j in range(length_2d_el):
            #         el_c_sub = electrolyte_concentration_jl[i]
            #         el_p_sub = electrolyte_potential_jl[i]
            #         electrolyte_concentration[i,j] = el_c_sub[j]
            #         electrolyte_potential[i,j] = el_p_sub[j]

            # for i in range(length_1d_ne):
            #     for j in range(length_2d_ne):
            #         ne_c_sub = negative_electrode_concentration_jl[i]
            #         ne_p_sub = negative_electrode_potential_jl[i]
            #         negative_electrode_concentration[i,j] = ne_c_sub[j]
            #         negative_electrode_potential[i,j] = ne_p_sub[j]





        return results, indicators

class SetIndicators():
    """
    used to render the indicator parameters on the results page.
    """
    def __init__(self, page_name,results_simulation= None, file_names= None):

        self.page_name = page_name
        self.indicators = results_simulation
        self.file_names = file_names
        self.calc_round_trip_efficiency = calc.calc_round_trip_efficiency
        #self.style = get_theme_style()
        self.set_indicators()

    def set_indicators(self):

        if self.page_name == "Simulation":

            indicators= self.get_indicators_from_LD()

        else:
            indicators = self.indicators
            # st.write(self.results_simulation)
            # if self.results_simulation:
            #     calculated_indicaters = self.calculate_indicators()
            #     # calculated_indicaters = None

            # else:
            # calculated_indicaters = None

            # indicators= self.get_indicators_from_run()

            # if calculated_indicaters:
            #     indicators["Cell"]["roundTripEfficiency"]["value"] = calculated_indicaters["Cell"]["roundTripEfficiency"]


        self.render_indicators(indicators)

    def get_indicators_from_run(self):
        with open(app_access.get_path_to_indicator_values(), 'r') as f:
            indicators = json.load(f)
        return indicators

    def get_indicators_from_LD(self):

        with open(app_access.get_path_to_linked_data_input(), 'r') as f:
            gui_parameters = json.load(f)

        indicators = match_json_LD.get_indicators_from_gui_dict(gui_parameters)

        return indicators

    def calculate_indicators(self):

        [
            log_messages,
            number_of_states,
            cell_voltage,
            cell_current,
            time_values,
            negative_electrode_grid,
            negative_electrode_grid_bc,
            electrolyte_grid,
            electrolyte_grid_bc,
            positive_electrode_grid,
            positive_electrode_grid_bc,
            negative_electrode_concentration,
            electrolyte_concentration,
            positive_electrode_concentration,
            negative_electrode_potential,
            electrolyte_potential,
            positive_electrode_potential

            ] = self.results_simulation

        round_trip_eff = self.calc_round_trip_efficiency(time_values,cell_current,cell_voltage)

        indicators = {
            "Cell": {
                "roundTripEfficiency": round_trip_eff
            }
        }
        return indicators

    def render_indicators(self,indicators):

        if isinstance(indicators,dict):

            indicators = [indicators]
            file_names = self.file_names
            if file_names == None:
                file_names = ["Some indicators"]
            elif isinstance(file_names, str):
                file_names = [file_names]
            multi = None

        elif isinstance(indicators[0], float) :
            indicators = [indicators]
            file_names = self.file_names

            if file_names == None:
                file_names = ["Some indicators"]
            elif isinstance(file_names, str):
                file_names = [file_names]
            # else:
            #     file_names = [file_names]
            # multi = None


        else:
            file_names = self.file_names
            multi = len(indicators)

        tabs = st.tabs(file_names)

        for i,tab in enumerate(tabs):

            with tab:

                indicator = indicators[i]


                if isinstance(indicator,dict):

                    cell_mass = indicator["Cell"]["cellMass"]
                    # cell_energy = indicator["Cell"]["cellEnergy"]
                    cell_capacity = indicator["Cell"]["nominalCellCapacity"]
                    n_to_p_ratio = indicator["Cell"]["NPRatio"]
                    energy_efficiency = indicator["Cell"]["roundTripEfficiency"]

                    ne_mass_loading = indicator["NegativeElectrode"]["massLoading"]
                    ne_thickness = indicator["NegativeElectrode"]["thickness"]
                    ne_porosity = indicator["NegativeElectrode"]["porosity"]
                    ne_specific_capacity = indicator["NegativeElectrode"]["specificCapacity"]
                    ne_am_specific_capacity = indicator["NegativeElectrode"]["ActiveMaterial"]["specificCapacity"]
                    pe_mass_loading = indicator["PositiveElectrode"]["massLoading"]
                    pe_thickness = indicator["PositiveElectrode"]["thickness"]
                    pe_porosity = indicator["PositiveElectrode"]["porosity"]
                    pe_specific_capacity = indicator["PositiveElectrode"]["specificCapacity"]
                    pe_am_specific_capacity = indicator["PositiveElectrode"]["ActiveMaterial"]["specificCapacity"]

                elif isinstance(indicator, list):

                    [ne_electrode_ml_value,
                    ne_electrode_ml_unit,
                    ne_electrode_thi_value,
                    ne_electrode_thi_unit,
                    ne_electrode_po_value,
                    ne_electrode_po_unit,
                    ne_electrode_cap_value,
                    ne_electrode_cap_unit,
                    ne_am_cap_value,
                    ne_am_cap_unit ,
                    pe_electrode_ml_value,
                    pe_electrode_ml_unit,
                    pe_electrode_thi_value,
                    pe_electrode_thi_unit,
                    pe_electrode_po_value,
                    pe_electrode_po_unit ,
                    pe_electrode_cap_value ,
                    pe_electrode_cap_unit,
                    pe_am_cap_value ,
                    pe_am_cap_unit,
                    cell_cap_value ,
                    cell_cap_unit,
                    cell_mass_value,
                    cell_mass_unit ,
                    cell_np_value ,
                    cell_np_unit] = indicator
        
                    cell_mass = {
                        "value":cell_mass_value,
                        "unit": cell_mass_unit
                    }
                    # cell_energy = indicators["Cell"]["cellEnergy"]
                    cell_capacity = {
                        "value":cell_cap_value,
                        "unit": cell_cap_unit
                    }
                    n_to_p_ratio = {
                        "value":cell_np_value,
                        "unit": cell_np_unit
                    }

                    ne_mass_loading = {
                        "value":ne_electrode_ml_value,
                        "unit": ne_electrode_ml_unit
                    }
                    ne_thickness = {
                        "value":ne_electrode_thi_value,
                        "unit": ne_electrode_thi_unit
                    }
                    ne_porosity = {
                        "value":ne_electrode_po_value,
                        "unit": ne_electrode_po_unit
                    }
                    ne_specific_capacity = {
                        "value":ne_electrode_cap_value,
                        "unit": ne_electrode_cap_unit
                    }
                    ne_am_specific_capacity = {
                        "value":ne_am_cap_value,
                        "unit": ne_am_cap_unit
                    }
                    pe_mass_loading = {
                        "value":pe_electrode_ml_value,
                        "unit": pe_electrode_ml_unit
                    }
                    pe_thickness = {
                        "value":pe_electrode_thi_value,
                        "unit": pe_electrode_thi_unit
                    }
                    pe_porosity = {
                        "value":pe_electrode_po_value,
                        "unit": pe_electrode_po_unit
                    }
                    pe_specific_capacity = {
                        "value":pe_electrode_cap_value,
                        "unit": pe_electrode_ml_unit
                    }
                    pe_am_specific_capacity = {
                        "value":pe_electrode_cap_value,
                        "unit": pe_electrode_cap_unit
                    }

                


                if self.page_name == "Simulation":
                    col1, col2, col3, col4 = st.columns(4)
                    col2.metric(
                        label = "Cell Mass / {}".format(cell_mass["unit"]),
                        value = int(np.round(cell_mass["value"])),
                        label_visibility= "visible"
                    )

                    col3.metric(
                            label = "Cell Capacity / {}".format(cell_capacity["unit"]),
                            value = int(np.round(cell_capacity["value"])),
                            label_visibility= "visible"
                        )
                    col1.metric(
                            label = "N/P ratio / {}".format(n_to_p_ratio["unit"]),
                            value = np.round(n_to_p_ratio["value"],1),
                            label_visibility= "visible"
                        )


                elif self.page_name == "Results":

                    NE, PE,cell = st.tabs(["Negative Electrode", "Positive Electrode","Cell"])
                    Electrode_ne, AM_ne = NE.tabs(["Electrode", "Active material"])
                    Electrode_pe, AM_pe = PE.tabs(["Electrode", "Active material"])

                    col1, col2, col3, col4 = cell.columns(4)

                    col2.metric(
                        label = "Mass / {}".format(cell_mass["unit"]),
                        value = int(np.round(cell_mass["value"])),
                        label_visibility= "visible"
                    )
                    # if isinstance(energy_efficiency["value"], str):
                    #     col4.metric(
                    #         label = "Energy efficiency({})".format(energy_efficiency["unit"]),
                    #         value = energy_efficiency["value"],
                    #         label_visibility= "visible"
                    #     )
                    # elif isinstance(energy_efficiency["value"],  np.ndarray):
                    #     col4.metric(
                    #             label = "Energy efficiency({})".format(energy_efficiency["unit"]),
                    #             value = np.round(energy_efficiency["value"][0],2),
                    #             label_visibility= "visible"
                    #         )
                    # else:
                    #     col4.metric(
                    #             label = "Energy efficiency({})".format(energy_efficiency["unit"]),
                    #             value = np.round(energy_efficiency["value"],2),
                    #             label_visibility= "visible"
                    #         )
                    col3.metric(
                            label = "Capacity / {}".format(cell_capacity["unit"]),
                            value = int(np.round(cell_capacity["value"])),
                            label_visibility= "visible"
                        )
                    col1.metric(
                            label = "N/P ratio / {}".format(n_to_p_ratio["unit"]),
                            value = np.round(n_to_p_ratio["value"],1),
                            label_visibility= "visible"
                        )

                    mass_loading, thickness, porosity, capacity= Electrode_ne.columns(4)

                    mass_loading.metric(
                            label = "Mass Loading / {}".format(ne_mass_loading["unit"]),
                            value = int(np.round(ne_mass_loading["value"])),
                            label_visibility= "visible"
                        )

                    thickness.metric(
                            label = "Thickness / {}".format(ne_thickness["unit"]),
                            value = int(np.round(ne_thickness["value"])),
                            label_visibility= "visible"
                        )

                    porosity.metric(
                            label = "Porosity / {}".format(ne_porosity["unit"]),
                            value = np.round(ne_porosity["value"],2),
                            label_visibility= "visible"
                        )
                    capacity.metric(
                            label = "Capacity / {}".format(ne_specific_capacity["unit"]),
                            value = int(np.round(ne_specific_capacity["value"])),
                            label_visibility= "visible"
                        )

                    capacity, _, _ ,_= AM_ne.columns(4)
                    capacity.metric(
                            label = "Specific Capacity / {}".format(ne_am_specific_capacity["unit"]),
                            value = int(np.round(ne_am_specific_capacity["value"])),
                            label_visibility= "visible"
                        )

                    mass_loading, thickness, porosity, capacity= Electrode_pe.columns(4)

                    mass_loading.metric(
                            label = "Mass Loading / {}".format(pe_mass_loading["unit"]),
                            value = int(np.round(pe_mass_loading["value"])),
                            label_visibility= "visible"
                        )

                    thickness.metric(
                            label = "Thickness / {}".format(pe_thickness["unit"]),
                            value =int(np.round(pe_thickness["value"])),
                            label_visibility= "visible"
                        )

                    porosity.metric(
                            label = "Porosity / {}".format(pe_porosity["unit"]),
                            value = np.round(pe_porosity["value"],2),
                            label_visibility= "visible"
                        )
                    capacity.metric(
                            label = "Capacity / {}".format(pe_specific_capacity["unit"]),
                            value = int(np.round(pe_specific_capacity["value"])),
                            label_visibility= "visible"
                        )

                    capacity, _, _ ,_= AM_pe.columns(4)
                    capacity.metric(
                            label = "Specific Capacity / {}".format(pe_am_specific_capacity["unit"]),
                            value = int(np.round(pe_am_specific_capacity["value"])),
                            label_visibility= "visible"
                        )



                else:
                    print("ERROR: Page name '{}' to get indicators doesn't match.".format(self.page_name))


class SetGeometryVisualization():
    """
    Used to render the geometry in a Plotly 3D volume plot on the 'Simulation' page.
    """
    def __init__(self,gui_parameters):
        self.header = "Visualize geometry"
        self.info = """This geometry visualization is an approximation based on the input parameters specified above.
                        The particles are for example visualized using a random data generator."""
        self.gui_parameters = gui_parameters
        self.set_geometry_visualization()

    def set_geometry_visualization(self):
        with st.sidebar:
            self.set_header_info()
            geometry_data = self.get_data()
            self.create_graphs(geometry_data)

    def set_header_info(self):
        st.markdown("## " + self.header)

    def get_data(self):
        geometry_data = match_json_LD.get_geometry_data_from_gui_dict(self.gui_parameters)
        return geometry_data

    def generate_random_particles(self, width, thickness, num_particles, particle_radius):
        # Generate random particle coordinates within the specified dimensions
        pts = np.random.rand(2,num_particles)
        pts[0, :] *= thickness
        # pts[:, 1] *= length
        pts[1, :] *= width
        # Generate random particle radii
        radii = 2*np.ones(num_particles)*particle_radius #get diameter instead of radius
        return pts, radii

    def create_graphs(_self, geometry_data):

        toggle_box = st.toggle("Full 3D geometry",key="full", label_visibility="visible")

        if toggle_box:
            _self.create_3d_graph_box(geometry_data)

        toggle_box_scaled = st.toggle("Scaled 3D geometry",key="scaled", label_visibility="visible")

        if toggle_box_scaled:
            _self.create_3d_graph_box_scaled(geometry_data)

        # toggle_full = st.toggle("Full 3D geometry",key="full", label_visibility="visible")

        # if toggle_full:
        #     _self.create_3d_graph_full(geometry_data)

        # toggle_zoomed = st.toggle("3D volume plot",key="zoomed", label_visibility="visible")

        # if toggle_zoomed:
        #     _self.create_3d_graph_small(geometry_data)

        # toggle_2d = st.toggle("2D scatter plot",key="2D", label_visibility="visible")

        # if toggle_2d:
        #     _self.create_2d_graph(geometry_data)


    @st.cache_data
    def create_3d_graph_box_scaled(_self, geometry_data):

        thickness_ne = geometry_data["thickness_ne"]
        thickness_pe = geometry_data["thickness_pe"]
        thickness_sep = geometry_data["thickness_sep"]
        total_thickness = thickness_ne + thickness_pe + thickness_sep
        length = geometry_data["length"]*10**6
        width = geometry_data["width"]*10**6
        porosity_ne =geometry_data["porosity_ne"]
        porosity_pe =geometry_data["porosity_pe"]
        porosity_sep =geometry_data["porosity_sep"]

        # Define the dimensions and colors of the boxes
        dimensions = [(thickness_ne, total_thickness, total_thickness), (thickness_sep, total_thickness, total_thickness), (thickness_pe, total_thickness, total_thickness)]  # (length, width, height) for each box
        colors = ['#FF5733', '#3498DB', '#27AE60']  # Colors for negative electrode, separator, and positive electrode
        colorscales = ['greens', 'blues', 'reds']
        colorbarxs = [-0.3,-0.26,-0.22]
        showscales = [True,True,True]
        colorbar_titles = ['_____', '_____', '_____']
        thickmodes = ['array','array','auto']
        components = ['Negative electrode', 'Separator', 'Positive electrode']

        # Define the porosities for each component (between 0 and 1)
        porosities = [porosity_ne, porosity_sep, porosity_pe]  # Porosity for negative electrode, separator, and positive electrode

        fig = go.Figure()

        # Add boxes for each component
        start = 0
        for dim, colorscale, porosity, colorbarx, showscale, colorbar_title, thickmode, component in zip(dimensions, colorscales, porosities, colorbarxs, showscales, colorbar_titles, thickmodes, components):
            opacity = 1 - porosity  # Calculate opacity based on porosity
            intensity = np.full(10, porosity)
            x, y, z = dim
            end = start + x
            fig.add_trace(go.Mesh3d(
                x=[start, end, end, start, start, end, end, start],  # Define x-coordinates for the box
                y=[0, 0, y, y, 0, 0, y, y],  # Define y-coordinates for the box
                z=[0, 0, 0, 0, z, z, z, z],  # Define z-coordinates for the box
                intensity = intensity,
                # i, j and k give the vertices of triangles
                i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
                j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
                k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],

                #opacity=opacity,  # Set opacity based on porosity
                #color=color,
                reversescale=True,
                colorscale = colorscale,
                cmin = 0,
                cmax = 0.6,
                showscale=showscale,
                colorbar=dict(title=colorbar_title,x=colorbarx, tickmode=thickmode, tickvals=[]),
                name=f'{component}',
                showlegend=True,
                flatshading = True
            ))
            start = end

        # Define the custom colorbar title annotation
        title_annotation = dict(
            text="Porosity",
            font_size=20,
            font_family='arial',
            font_color='black',
            textangle=0,
            showarrow=False,
            # ^^ appearance
            xref="paper",
            yref="paper",
            x=-0.28,
            y=1,
            # ^^ position
        )

        fig.update_layout(
                legend=dict(
                    yanchor="top",
                    y=0.96,
                    xanchor="right",
                    x=1
                ),
                annotations=[title_annotation],
                scene_aspectmode='data',
                scene = dict(
                    xaxis = dict(autorange = "reversed", nticks=10),
                    xaxis_title='Thickness  /  \u03BCm',
                    yaxis_title='Scaled length  /  \u03BCm',
                    zaxis_title='Scaled width  /  \u03BCm'),
                xaxis=dict(range=[0, total_thickness]),
                width=700,
                margin=dict(r=20, b=10, l=10, t=10),
                # coloraxis_colorbar_x=colorbarx,#, colorbar_y=0.95, colorbar_yanchor='top', colorbar_ypad=0),
                # colorbar2=dict(coloraxis_colorbar_x=0.6),#, colorbar_y=0.95, colorbar_yanchor='top', colorbar_ypad=0),
                # colorbar3=dict(coloraxis_colorbar_x=0.75)#, colorbar_y=0.95, colorbar_yanchor='top', colorbar_ypad=0)
                )


        st.plotly_chart(fig,theme=None, use_container_width=True)

    @st.cache_data
    def create_3d_graph_box(_self, geometry_data):

        thickness_ne = geometry_data["thickness_ne"]
        thickness_pe = geometry_data["thickness_pe"]
        thickness_sep = geometry_data["thickness_sep"]
        total_thickness = thickness_ne + thickness_pe + thickness_sep
        length = geometry_data["length"]*10**6
        width = geometry_data["width"]*10**6
        porosity_ne =geometry_data["porosity_ne"]
        porosity_pe =geometry_data["porosity_pe"]
        porosity_sep =geometry_data["porosity_sep"]

        # Define the dimensions and colors of the boxes
        dimensions = [(thickness_ne, length, width), (thickness_sep, length, width), (thickness_pe, length, width)]  # (length, width, height) for each box
        colors = ['#FF5733', '#3498DB', '#27AE60']  # Colors for negative electrode, separator, and positive electrode
        colorscales = ['greens', 'blues', 'reds']
        colorbarxs = [-0.3,-0.26,-0.22]
        showscales = [True,True,True]
        colorbar_titles = ['_____', '_____', '_____']
        thickmodes = ['array','array','auto']
        components = ['Negative electrode', 'Separator', 'Positive electrode']

        # Define the porosities for each component (between 0 and 1)
        porosities = [porosity_ne, porosity_sep, porosity_pe]  # Porosity for negative electrode, separator, and positive electrode

        fig = go.Figure()

        # Add boxes for each component
        start = 0
        for dim, colorscale, porosity, colorbarx, showscale, colorbar_title, thickmode, component in zip(dimensions, colorscales, porosities, colorbarxs, showscales, colorbar_titles, thickmodes, components):
            opacity = 1 - porosity  # Calculate opacity based on porosity
            intensity = np.full(10, porosity)
            x, y, z = dim
            end = start + x
            fig.add_trace(go.Mesh3d(
                x=[start, end, end, start, start, end, end, start],  # Define x-coordinates for the box
                y=[0, 0, y, y, 0, 0, y, y],  # Define y-coordinates for the box
                z=[0, 0, 0, 0, z, z, z, z],  # Define z-coordinates for the box
                intensity = intensity,
                # i, j and k give the vertices of triangles
                i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
                j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
                k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],

                #opacity=opacity,  # Set opacity based on porosity
                #color=color,
                reversescale=True,
                colorscale = colorscale,
                cmin = 0,
                cmax = 0.6,
                showscale=showscale,
                colorbar=dict(title=colorbar_title,x=colorbarx, tickmode=thickmode, tickvals=[]),
                name=f'{component}',
                showlegend=True,
                flatshading = True
            ))
            start = end

        # Define the custom colorbar title annotation
        title_annotation = dict(
            text="Porosity",
            font_size=20,
            font_family='arial',
            font_color='black',
            textangle=0,
            showarrow=False,
            # ^^ appearance
            xref="paper",
            yref="paper",
            x=-0.28,
            y=1,
            # ^^ position
        )

        fig.update_layout(
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="right",
                    x=1
                ),
                annotations=[title_annotation],
                scene_aspectmode='data',
                scene = dict(
                    xaxis = dict(autorange = "reversed"),
                    xaxis_title='Thickness  /  \u03BCm',
                    yaxis_title='Length  /  \u03BCm',
                    zaxis_title='Width  /  \u03BCm'),
                xaxis=dict(range=[0, total_thickness]),
                width=700,
                margin=dict(r=20, b=10, l=10, t=10),
                # coloraxis_colorbar_x=colorbarx,#, colorbar_y=0.95, colorbar_yanchor='top', colorbar_ypad=0),
                # colorbar2=dict(coloraxis_colorbar_x=0.6),#, colorbar_y=0.95, colorbar_yanchor='top', colorbar_ypad=0),
                # colorbar3=dict(coloraxis_colorbar_x=0.75)#, colorbar_y=0.95, colorbar_yanchor='top', colorbar_ypad=0)
                )


        st.plotly_chart(fig,theme=None, use_container_width=True)

    @st.cache_data
    def create_3d_graph_full(_self, geometry_data):
        thickness_ne = geometry_data["thickness_ne"]
        thickness_pe = geometry_data["thickness_pe"]
        thickness_sep = geometry_data["thickness_sep"]
        total_thickness = thickness_ne + thickness_pe + thickness_sep
        length = geometry_data["length"]*10**6
        width = geometry_data["width"]*10**6
        particle_radius_ne = geometry_data["particle_radius_ne"]*10**6
        particle_radius_pe = geometry_data["particle_radius_pe"]*10**6
        porosity_ne =geometry_data["porosity_ne"]
        porosity_pe =geometry_data["porosity_pe"]
        porosity_sep =geometry_data["porosity_sep"]

        vf_ne = 1-porosity_ne
        vf_pe = 1-porosity_pe
        vf_sep = 1-porosity_sep
        volume_ne = length*width*thickness_ne
        volume_pe = length*width*thickness_pe
        mass_volume_ne = vf_ne*volume_ne
        mass_volume_pe = vf_pe*volume_pe
        particle_volume_ne = 4/3 *np.pi*particle_radius_ne**3
        particle_volume_pe = 4/3 *np.pi*particle_radius_pe**3
        number_of_particles_ne = int(round(mass_volume_ne/particle_volume_ne))
        number_of_particles_pe = int(round(mass_volume_pe/particle_volume_pe))

        np.random.seed(0)

        factor = int(round(thickness_sep))
        scaled_thickness_ne = thickness_ne/factor
        scaled_thickness_pe = thickness_pe/factor
        scaled_thickness_sep = thickness_sep/factor
        scaled_total_thickness  = total_thickness/factor
        scaled_length = length/factor
        scaled_width = width/factor
        scaled_volume_ne = scaled_thickness_ne*scaled_length*scaled_width
        scaled_volume_pe = scaled_thickness_pe*scaled_length*scaled_width
        scaled_volume_sep = scaled_thickness_sep*scaled_length*scaled_width
        scaled_real_volume_ne = scaled_volume_ne*vf_ne
        scaled_real_volume_pe = scaled_volume_ne*vf_pe
        scaled_real_volume_sep = scaled_volume_ne*vf_sep

        X_ne, Y, Z = np.mgrid[:int(round(scaled_thickness_ne)), :int(round(scaled_length)), :int(round(scaled_width))]
        # vol_ne = np.zeros((int(round(scaled_thickness_ne)), int(round(scaled_length)), int(round(scaled_width))))
        # # pts_ne_x = (scaled_thickness_ne * np.random.rand(1, 15)).astype(int)
        # # pts_ne_y = (scaled_total_thickness * np.random.rand(1, 15)).astype(int)
        # # pts_ne_z = (scaled_total_thickness * np.random.rand(1, 15)).astype(int)
        # #pts_ne = np.concatenate((pts_ne_x, pts_ne_y, pts_ne_z), axis=0)
        # pts_ne_x = np.transpose(np.random.randint(0, int(round(scaled_thickness_ne)), size=(int(round(scaled_real_volume_ne)), 1)))
        # pts_ne_y = np.transpose(np.random.randint(0, int(round(scaled_length)), size=(int(round(scaled_real_volume_ne)), 1)))
        # pts_ne_z = np.transpose(np.random.randint(0, int(round(scaled_width)), size=(int(round(scaled_real_volume_ne)), 1)))
        # pts_ne = np.concatenate((pts_ne_x, pts_ne_y, pts_ne_z), axis=0)

        X_pe, _, _ = np.mgrid[:int(round(scaled_thickness_pe)), :int(round(scaled_length)), :int(round(scaled_width))]
        #vol_pe = np.zeros((int(round(scaled_thickness_pe)), int(round(scaled_length)), int(round(scaled_width))))

        # pts_pe_x = (scaled_thickness_pe * np.random.rand(1, 15)).astype(int)#+ int(thickness_ne) + int(thickness_sep)
        # pts_pe_y = (scaled_total_thickness * np.random.rand(1, 15)).astype(int)
        # pts_pe_z = (scaled_total_thickness * np.random.rand(1, 15)).astype(int)
        # pts_pe = np.concatenate((pts_pe_x, pts_pe_y, pts_pe_z), axis=0)
        # pts_pe_x = np.transpose(np.random.randint(0, int(round(scaled_thickness_pe)), size=(int(round(scaled_real_volume_pe)), 1)))
        # pts_pe_y = np.transpose(np.random.randint(0, int(round(scaled_length)), size=(int(round(scaled_real_volume_pe)), 1)))
        # pts_pe_z = np.transpose(np.random.randint(0, int(round(scaled_width)), size=(int(round(scaled_real_volume_pe)), 1)))
        # pts_pe = np.concatenate((pts_pe_x, pts_pe_y, pts_pe_z), axis=0)

        X_sep, _, _ = np.mgrid[:int(round(scaled_thickness_sep)), :int(round(scaled_length)), :int(round(scaled_width))]
        #vol_sep = np.zeros((int(round(scaled_thickness_sep)), int(round(scaled_length)), int(round(scaled_width))))
        # pts_sep_x = (scaled_thickness_sep * np.random.rand(1, 15)).astype(int)# + int(thickness_ne)
        # pts_sep_y = (scaled_total_thickness * np.random.rand(1, 15)).astype(int)
        # pts_sep_z = (scaled_total_thickness * np.random.rand(1, 15)).astype(int)
        # pts_sep = np.concatenate((pts_sep_x, pts_sep_y, pts_sep_z), axis=0)
        # pts_sep_x = np.transpose(np.random.randint(0, int(round(scaled_thickness_sep)), size=(int(round(scaled_real_volume_sep)), 1)))
        # pts_sep_y = np.transpose(np.random.randint(0, int(round(scaled_length)), size=(int(round(scaled_real_volume_sep)), 1)))
        # pts_sep_z = np.transpose(np.random.randint(0, int(round(scaled_width)), size=(int(round(scaled_real_volume_sep)), 1)))
        # pts_sep = np.concatenate((pts_sep_x, pts_sep_y, pts_sep_z), axis=0)

        # vol_ne[tuple(indices for indices in pts_ne)] = 1
        # vol_pe[tuple(indices for indices in pts_pe)] = 1
        # vol_sep[tuple(indices for indices in pts_sep)] = 1
        from scipy import ndimage
        #vol_ne = ndimage.gaussian_filter(vol_ne, 0.5)
        vol_ne /= vol_ne.max()
        #vol_pe = ndimage.gaussian_filter(vol_pe, 0.5)
        vol_pe /= vol_pe.max()
        #vol_sep = ndimage.gaussian_filter(vol_sep, 0.5)
        vol_sep /= vol_sep.max()

        X_ne *= factor
        X_sep += int(scaled_thickness_ne)
        X_pe += int(scaled_thickness_ne +scaled_thickness_sep)
        X_sep *= factor
        X_pe *= factor
        Y *= factor
        Z *= factor

        fig = go.Figure(data=go.Volume(
            x=X_ne.flatten(), y=Y.flatten(), z=Z.flatten(),
            #value=vol_ne.flatten(),
            isomin=0.2,
            isomax=0.7,
            opacity=0.1,
            surface_count=25,
            name='Negative Electrode',
            colorscale='Blues',
            showscale=False
            ))

        # fig.add_trace(go.Volume(
        #     x=X_pe.flatten(), y=Y.flatten(), z=Z.flatten(),
        #     value=vol_pe.flatten(),
        #     isomin=0.2,
        #     isomax=0.7,
        #     opacity=0.1,
        #     surface_count=25,
        #     name='Positive Electrode',
        #     colorscale='Reds',
        #     showscale=False
        # ))

        # fig.add_trace(go.Volume(
        #     x=X_sep.flatten(), y=Y.flatten(), z=Z.flatten(),
        #     value=vol_sep.flatten(),
        #     isomin=0.2,
        #     isomax=0.7,
        #     opacity=0.1,
        #     surface_count=25,
        #     name='Separator',
        #     colorscale='Greens',
        #     showscale=False
        # ))
        fig.update_layout(
                # legend=dict(
                #     yanchor="top",
                #     y=0.99,
                #     xanchor="left",
                #     x=0.01
                # ),

                scene_aspectmode='data',
                scene = dict(
                    xaxis = dict(autorange = "reversed"),
                    xaxis_title='Thickness  /  \u03BCm',
                    yaxis_title='Length  /  \u03BCm',
                    zaxis_title='Width  /  \u03BCm'),
                    xaxis=dict(range=[0, total_thickness]),
                    width=700,
                    margin=dict(r=20, b=10, l=10, t=10),

                )
        st.plotly_chart(fig,theme=None, use_container_width=True)

    @st.cache_data
    def create_3d_graph_small(_self, geometry_data):
        thickness_ne = geometry_data["thickness_ne"]
        thickness_pe = geometry_data["thickness_pe"]
        thickness_sep = geometry_data["thickness_sep"]
        total_thickness = thickness_ne + thickness_pe + thickness_sep
        length = total_thickness
        width = total_thickness
        particle_radius_ne = geometry_data["particle_radius_ne"]*10**6
        particle_radius_pe = geometry_data["particle_radius_pe"]*10**6
        porosity_ne =geometry_data["porosity_ne"]
        porosity_pe =geometry_data["porosity_pe"]
        porosity_sep =geometry_data["porosity_sep"]

        vf_ne = 1-porosity_ne
        vf_pe = 1-porosity_pe
        vf_sep = 1-porosity_sep
        volume_ne = length*width*thickness_ne
        volume_pe = length*width*thickness_pe
        mass_volume_ne = vf_ne*volume_ne
        mass_volume_pe = vf_pe*volume_pe
        particle_volume_ne = 4/3 *np.pi*particle_radius_ne**3
        particle_volume_pe = 4/3 *np.pi*particle_radius_pe**3
        number_of_particles_ne = int(round(mass_volume_ne/particle_volume_ne))
        number_of_particles_pe = int(round(mass_volume_pe/particle_volume_pe))

        np.random.seed(0)

        factor = int(round(thickness_sep/2))

        scaled_thickness_ne = thickness_ne/factor
        scaled_thickness_pe = thickness_pe/factor
        scaled_thickness_sep = thickness_sep/factor
        scaled_total_thickness  = total_thickness/factor
        scaled_volume_ne = scaled_thickness_ne*scaled_total_thickness*scaled_total_thickness
        scaled_volume_pe = scaled_thickness_pe*scaled_total_thickness*scaled_total_thickness
        scaled_volume_sep = scaled_thickness_sep*scaled_total_thickness*scaled_total_thickness
        scaled_real_volume_ne = scaled_volume_ne*vf_ne
        scaled_real_volume_pe = scaled_volume_ne*vf_pe
        scaled_real_volume_sep = scaled_volume_ne*vf_sep

        X_ne, Y, Z = np.mgrid[:int(round(scaled_thickness_ne)), :int(round(scaled_total_thickness)), :int(round(scaled_total_thickness))]
        vol_ne = np.zeros((int(round(scaled_thickness_ne)), int(round(scaled_total_thickness)), int(round(scaled_total_thickness))))
        # pts_ne_x = (scaled_thickness_ne * np.random.rand(1, 15)).astype(int)
        # pts_ne_y = (scaled_total_thickness * np.random.rand(1, 15)).astype(int)
        # pts_ne_z = (scaled_total_thickness * np.random.rand(1, 15)).astype(int)
        #pts_ne = np.concatenate((pts_ne_x, pts_ne_y, pts_ne_z), axis=0)
        pts_ne_x = np.transpose(np.random.randint(0, int(round(scaled_thickness_ne)), size=(int(round(scaled_real_volume_ne)), 1)))
        pts_ne_y = np.transpose(np.random.randint(0, int(round(scaled_total_thickness)), size=(int(round(scaled_real_volume_ne)), 1)))
        pts_ne_z = np.transpose(np.random.randint(0, int(round(scaled_total_thickness)), size=(int(round(scaled_real_volume_ne)), 1)))
        pts_ne = np.concatenate((pts_ne_x, pts_ne_y, pts_ne_z), axis=0)

        X_pe, _, _ = np.mgrid[:int(round(scaled_thickness_pe)), :int(round(scaled_total_thickness)), :int(round(scaled_total_thickness))]
        vol_pe = np.zeros((int(round(scaled_thickness_pe)), int(round(scaled_total_thickness)), int(round(scaled_total_thickness))))

        # pts_pe_x = (scaled_thickness_pe * np.random.rand(1, 15)).astype(int)#+ int(thickness_ne) + int(thickness_sep)
        # pts_pe_y = (scaled_total_thickness * np.random.rand(1, 15)).astype(int)
        # pts_pe_z = (scaled_total_thickness * np.random.rand(1, 15)).astype(int)
        # pts_pe = np.concatenate((pts_pe_x, pts_pe_y, pts_pe_z), axis=0)
        pts_pe_x = np.transpose(np.random.randint(0, int(round(scaled_thickness_pe)), size=(int(round(scaled_real_volume_pe)), 1)))
        pts_pe_y = np.transpose(np.random.randint(0, int(round(scaled_total_thickness)), size=(int(round(scaled_real_volume_pe)), 1)))
        pts_pe_z = np.transpose(np.random.randint(0, int(round(scaled_total_thickness)), size=(int(round(scaled_real_volume_pe)), 1)))
        pts_pe = np.concatenate((pts_pe_x, pts_pe_y, pts_pe_z), axis=0)

        X_sep, _, _ = np.mgrid[:int(round(scaled_thickness_sep)), :int(round(scaled_total_thickness)), :int(round(scaled_total_thickness))]
        vol_sep = np.zeros((int(round(scaled_thickness_sep)), int(round(scaled_total_thickness)), int(round(scaled_total_thickness))))
        # pts_sep_x = (scaled_thickness_sep * np.random.rand(1, 15)).astype(int)# + int(thickness_ne)
        # pts_sep_y = (scaled_total_thickness * np.random.rand(1, 15)).astype(int)
        # pts_sep_z = (scaled_total_thickness * np.random.rand(1, 15)).astype(int)
        # pts_sep = np.concatenate((pts_sep_x, pts_sep_y, pts_sep_z), axis=0)
        pts_sep_x = np.transpose(np.random.randint(0, int(round(scaled_thickness_sep)), size=(int(round(scaled_real_volume_sep)), 1)))
        pts_sep_y = np.transpose(np.random.randint(0, int(round(scaled_total_thickness)), size=(int(round(scaled_real_volume_sep)), 1)))
        pts_sep_z = np.transpose(np.random.randint(0, int(round(scaled_total_thickness)), size=(int(round(scaled_real_volume_sep)), 1)))
        pts_sep = np.concatenate((pts_sep_x, pts_sep_y, pts_sep_z), axis=0)

        vol_ne[tuple(indices for indices in pts_ne)] = 1
        vol_pe[tuple(indices for indices in pts_pe)] = 1
        vol_sep[tuple(indices for indices in pts_sep)] = 1
        from scipy import ndimage
        vol_ne = ndimage.gaussian_filter(vol_ne, 0.5)
        vol_ne /= vol_ne.max()
        vol_pe = ndimage.gaussian_filter(vol_pe, 0.5)
        vol_pe /= vol_pe.max()
        vol_sep = ndimage.gaussian_filter(vol_sep, 0.5)
        vol_sep /= vol_sep.max()

        X_ne *= factor
        X_sep += int(scaled_thickness_ne)
        X_pe += int(scaled_thickness_ne +scaled_thickness_sep)
        X_sep *= factor
        X_pe *= factor
        Y *= factor
        Z *= factor

        fig = go.Figure(data=go.Volume(
            x=X_ne.flatten(), y=Y.flatten(), z=Z.flatten(),
            value=vol_ne.flatten(),
            isomin=0.2,
            isomax=0.7,
            opacity=0.1,
            surface_count=25,
            name='Negative Electrode',
            colorscale='Blues',
            showscale=False
            ))

        fig.add_trace(go.Volume(
            x=X_pe.flatten(), y=Y.flatten(), z=Z.flatten(),
            value=vol_pe.flatten(),
            isomin=0.2,
            isomax=0.7,
            opacity=0.1,
            surface_count=25,
            name='Positive Electrode',
            colorscale='Reds',
            showscale=False
        ))

        fig.add_trace(go.Volume(
            x=X_sep.flatten(), y=Y.flatten(), z=Z.flatten(),
            value=vol_sep.flatten(),
            isomin=0.2,
            isomax=0.7,
            opacity=0.1,
            surface_count=25,
            name='Separator',
            colorscale='Greens',
            showscale=False
        ))
        fig.update_layout(
                # legend=dict(
                #     yanchor="top",
                #     y=0.99,
                #     xanchor="left",
                #     x=0.01
                # ),

                scene_aspectmode='data',
                scene = dict(
                    xaxis = dict(autorange = "reversed"),
                    xaxis_title='Thickness  /  \u03BCm',
                    yaxis_title='Length  /  \u03BCm',
                    zaxis_title='Width  /  \u03BCm'),
                    xaxis=dict(range=[0, total_thickness]),
                    width=700,
                    margin=dict(r=20, b=10, l=10, t=10),
                )
        st.plotly_chart(fig,theme=None, use_container_width=True)

    @st.cache_data
    def create_2d_graph(_self, geometry_data):
        length = geometry_data["length"]*10**4
        width = geometry_data["width"]*10**4
        thickness_ne = geometry_data["thickness_ne"]
        thickness_pe = geometry_data["thickness_pe"]
        thickness_sep = geometry_data["thickness_sep"]
        total_thickness = thickness_ne + thickness_pe + thickness_sep
        width = total_thickness
        particle_radius_ne = geometry_data["particle_radius_ne"]*10**6*10
        particle_radius_pe = geometry_data["particle_radius_pe"]*10**6*10
        porosity_ne =geometry_data["porosity_ne"]
        porosity_pe =geometry_data["porosity_pe"]

        vf_ne = 1-porosity_ne
        vf_pe = 1-porosity_pe
        area_ne = width*thickness_ne
        area_pe = width*thickness_pe
        mass_area_ne = vf_ne*area_ne
        mass_area_pe = vf_pe*area_pe
        particle_area_ne = (2*particle_radius_ne)**2 #np.pi*particle_radius_ne**2
        particle_area_pe = (2*particle_radius_pe)**2 #np.pi*particle_radius_pe**2
        number_of_particles_ne = int(round(mass_area_ne/particle_area_ne))
        number_of_particles_pe = int(round(mass_area_pe/particle_area_pe))

        ne_pts_full = np.full((2, int(round(total_thickness))), np.nan)

        # Generate negative electrode particles
        ne_pts, ne_radii = _self.generate_random_particles(width, thickness_ne, number_of_particles_ne, particle_radius_ne)

        # Generate positive electrode particles
        pe_pts, pe_radii = _self.generate_random_particles(width, thickness_pe, number_of_particles_pe, particle_radius_pe)
        pe_pts[0,:] += thickness_ne +thickness_sep
        # Generate separator particles
        sep_pts, sep_radii = _self.generate_random_particles( width, thickness_sep, 10,5)
        sep_pts[0,:] += thickness_ne
        elements = max(number_of_particles_ne, number_of_particles_pe)

        import pandas as pd
        # Create DataFrame for each particle type
        ne_df = pd.DataFrame({'x': ne_pts[0,:], 'y': ne_pts[1,:], 'radius': ne_radii, 'component': 'Negative Electrode'})
        pe_df = pd.DataFrame({'x': pe_pts[0,:], 'y': pe_pts[1,:], 'radius': pe_radii, 'component': 'Positive Electrode'})
        sep_df = pd.DataFrame({'x': sep_pts[0,:], 'y': sep_pts[1,:], 'radius': sep_radii, 'component': 'Separator'})

        # Concatenate DataFrames
        combined_df = pd.concat([ne_df, sep_df,pe_df], ignore_index=True)

        one = np.ones(len(ne_pts[0,:]))
        two = np.ones(len(sep_pts[0,:]))*2
        three = np.ones(len(pe_pts[0,:]))*3
        a = ['a' for i in range(len(ne_pts[0,:]))]
        b = ['b' for i in range(len(sep_pts[0,:]))]
        c = ['c' for i in range(len(pe_pts[0,:]))]

        sub = np.append(one, two)

        combined_df['Marker'] = np.append(sub,three)
        combined_df['Color'] = a + b + c

        # Plot scatter plot
        fig = px.scatter(combined_df, x='x', y='y', size='radius',
                        color = 'Color', hover_data = ["Color", "Marker"],
                        symbol = combined_df['Marker'],
                        symbol_sequence= ['diamond-dot', 'square', 'circle'],
                        color_discrete_sequence = ['blue','green', 'red']
                        )

        ratio = 8
        plot_width = 400


        # Update layout
        fig.update_layout(
            xaxis_title='Thickness  /  \u03BCm',
            yaxis_title='Width  /  \u03BCm',
            width=plot_width,
            height = plot_width,
            margin=dict(r=20, b=10, l=10, t=10),
            xaxis=dict(
                        dtick= int(round(max(combined_df['x'])/ratio/10))*10,  # Set the step for x-axis tick marks
                    ),
            yaxis=dict(
                        dtick=int(round(max(combined_df['y'])/ratio/10))*10,  # Set the step for y-axis tick marks
                    ))
        st.plotly_chart(fig, use_container_width=False, width=1400,height=1400)
        # fig.show()







class SetHDF5Download():
    """
    Used to render the hdf5 output file on the Results page.
    """
    def __init__(self,results,selected_data_sets):

        self.header = "Download results"
        self.results = results
        self.selected_data_sets = selected_data_sets
        self.set_download_hdf5_button()

    def set_download_hdf5_button(self):

        with st.sidebar:
            # set Download header
            st.markdown("## " + self.header)

            if len(self.selected_data_sets) > 1:
                st.error("Select only one file to download.")
            else:

                st.download_button(
                    label="HDF5 Results",
                    file_name=self.selected_data_sets[0],
                    data=self.prepare_h5_file(),
                    mime="application/x-hdf",
                    help="Download your results."
                )

    # Create hdf5 from numpy arrays, result cached to optimize software.
    # Cache cleared after generating new results (cf RunSimulation)

    def prepare_h5_file(_self):

        
        file_path = os.path.join(st.session_state.temp_dir,_self.selected_data_sets[0])

        results,indicators = app_controller.get_results_data(file_path).get_results_data(file_path)


        [
            log_messages,
            number_of_states,
            cell_voltage,
            cell_current,
            time_values,
            negative_electrode_grid,
            negative_electrode_grid_bc,
            electrolyte_grid,
            electrolyte_grid_bc,
            positive_electrode_grid,
            positive_electrode_grid_bc,
            negative_electrode_concentration,
            electrolyte_concentration,
            positive_electrode_concentration,
            negative_electrode_potential,
            electrolyte_potential,
            positive_electrode_potential

            ] = results
        
        [
            ne_electrode_ml_value,
            ne_electrode_ml_unit,
            ne_electrode_thi_value,
            ne_electrode_thi_unit,
            ne_electrode_po_value,
            ne_electrode_po_unit,
            ne_electrode_cap_value,
            ne_electrode_cap_unit,
            ne_am_cap_value,
            ne_am_cap_unit ,

            pe_electrode_ml_value,
            pe_electrode_ml_unit,
            pe_electrode_thi_value,
            pe_electrode_thi_unit,
            pe_electrode_po_value,
            pe_electrode_po_unit ,
            pe_electrode_cap_value ,
            pe_electrode_cap_unit,
            pe_am_cap_value ,
            pe_am_cap_unit,

            cell_cap_value ,
            cell_cap_unit,
            cell_mass_value,
            cell_mass_unit ,
            cell_np_value ,
            cell_np_unit,

            ] = indicators


        bio = io.BytesIO()
        # cf https://stackoverflow.com/questions/73157377/how-to-download-various-data-from-streamlit-to-hdf5-file-with-st-download-butto

        with h5py.File(bio, "w") as f:
            f['number_of_states'] = number_of_states
            f['log_messages'] = log_messages
            f.create_dataset("time_values", data=time_values)
            f.create_dataset("cell_voltage", data=cell_voltage)
            f.create_dataset("cell_current", data=cell_current)

            grids = f.create_group("grids")
            grids.create_dataset("negative_electrode_grid", data=negative_electrode_grid)
            grids.create_dataset("negative_electrode_grid_bc", data=negative_electrode_grid_bc)
            grids.create_dataset("positive_electrode_grid", data=positive_electrode_grid)
            grids.create_dataset("positive_electrode_grid_bc", data=positive_electrode_grid_bc)
            grids.create_dataset("electrolyte_grid", data=electrolyte_grid)
            grids.create_dataset("electrolyte_grid_bc", data=electrolyte_grid_bc)

            concentrations = f.create_group("concentrations")

            negative_electrode_concentrations = concentrations.create_group("negative_electrode")
            electrolyte_concentrations = concentrations.create_group("electrolyte")
            positive_electrode_concentrations = concentrations.create_group("positive_electrode")

            potentials = f.create_group("potentials")

            negative_electrode_potentials = potentials.create_group("negative_electrode")
            electrolyte_potentials = potentials.create_group("electrolyte")
            positive_electrode_potentials = potentials.create_group("positive_electrode")

            for i in range(number_of_states):
                negative_electrode_concentrations.create_dataset(
                    "ne_c_state_{}".format(i+1),
                    data=np.array(negative_electrode_concentration[i], dtype=float)
                )
                positive_electrode_concentrations.create_dataset(
                    "pe_c_state_{}".format(i+1),
                    data=np.array(positive_electrode_concentration[i], dtype=float)
                )
                electrolyte_concentrations.create_dataset(
                    "elyte_c_state_{}".format(i+1),
                    data=np.array(electrolyte_concentration[i], dtype=float)
                )

                negative_electrode_potentials.create_dataset(
                    "ne_p_state_{}".format(i+1),
                    data=np.array(negative_electrode_potential[i], dtype=float)
                )
                positive_electrode_potentials.create_dataset(
                    "pe_p_state_{}".format(i+1),
                    data=np.array(positive_electrode_potential[i], dtype=float)
                )
                electrolyte_potentials.create_dataset(
                    "elyte_p_state_{}".format(i+1),
                    data=np.array(electrolyte_potential[i], dtype=float)
                )


            indocators_group = f.create_group("indicators")
            cell = indocators_group.create_group("cell")
            negative_electrode = indocators_group.create_group("negative_electrode")
            negative_electrode_electrode = negative_electrode.create_group("electrode")
            negative_electrode_am = negative_electrode.create_group("active_material")
            positive_electrode = indocators_group.create_group("positive_electrode")
            positive_electrode_electrode = positive_electrode.create_group("electrode")
            positive_electrode_am = positive_electrode.create_group("active_material")

            NE_ml = negative_electrode_electrode.create_group("mass_loading")
            NE_ml.create_dataset("value", data = ne_electrode_ml_value)
            NE_ml.create_dataset("unit", data = ne_electrode_ml_unit)

            NE_thi = negative_electrode_electrode.create_group("coating_thickness")
            NE_thi.create_dataset("value", data = ne_electrode_thi_value)
            NE_thi.create_dataset("unit", data = ne_electrode_thi_unit)

            NE_po = negative_electrode_electrode.create_group("coating_porosity")
            NE_po.create_dataset("value", data = ne_electrode_po_value)
            NE_po.create_dataset("unit", data = ne_electrode_po_unit)

            NE_cap = negative_electrode_electrode.create_group("capacity")
            NE_cap.create_dataset("value", data = ne_electrode_cap_value)
            NE_cap.create_dataset("unit", data = ne_electrode_cap_unit)

            NE_am_cap = negative_electrode_am.create_group("specific_capacity")
            NE_am_cap.create_dataset("value", data = ne_am_cap_value)
            NE_am_cap.create_dataset("unit",data =  ne_am_cap_unit)
        
            PE_ml = positive_electrode_electrode.create_group("mass_loading")
            PE_ml.create_dataset("value", data = pe_electrode_ml_value)
            PE_ml.create_dataset("unit", data = pe_electrode_ml_unit)

            PE_thi = positive_electrode_electrode.create_group("coating_thickness")
            PE_thi.create_dataset("value", data = pe_electrode_thi_value)
            PE_thi.create_dataset("unit", data = pe_electrode_thi_unit)

            PE_po = positive_electrode_electrode.create_group("coating_porosity")
            PE_po.create_dataset("value", data = pe_electrode_po_value)
            PE_po.create_dataset("unit", data = pe_electrode_po_unit)

            PE_cap = positive_electrode_electrode.create_group("capacity")
            PE_cap.create_dataset("value", data = pe_electrode_cap_value)
            PE_cap.create_dataset("unit", data = pe_electrode_cap_unit)

            PE_am_cap = positive_electrode_am.create_group("specific_capacity")
            PE_am_cap.create_dataset("value", data = pe_am_cap_value)
            PE_am_cap.create_dataset("unit", data = pe_am_cap_unit)

            cell_mass = cell.create_group("cell_mass")
            cell_mass.create_dataset("value", data = cell_mass_value)
            cell_mass.create_dataset("unit", data = cell_mass_unit)

            cell_cap = cell.create_group("nominal_cell_capacity")
            cell_cap.create_dataset("value", data = cell_cap_value)
            cell_cap.create_dataset("unit", data = cell_cap_unit)

            cell_np = cell.create_group("n_to_p_ratio")
            cell_np.create_dataset("value", data = cell_np_value)
            cell_np.create_dataset("unit", data = cell_np_unit)

        return bio

class SetHDF5Upload():
    def __init__(self):
        self.header = "Upload your data file"
        self.upload_folder_path = app_access.get_path_to_uploaded_hdf5_files_dir()

    def set_results_uploader(self):

        with st.sidebar:
            st.markdown("## " + self.header)
            uploaded_file = st.file_uploader("Upload your HDF5 results file.",type='hdf5', label_visibility="collapsed",accept_multiple_files = True)

        if uploaded_file:
            if isinstance(uploaded_file, list) and len(uploaded_file) > 1:
                names = []
                for i, data in enumerate(uploaded_file):
                    file_path = os.path.join(st.session_state['temp_dir'], data.name)
                    with open(file_path, "wb") as f:
                        f.write(data.getbuffer())
                    names.append(data.name)
                    
                st.success(f"""Files are saved with names {names}. \n\n

                                All results are stored temporarily and will be deleted on refreshing or closing the browser.
                """)
            
            else:
                file_path = os.path.join(st.session_state['temp_dir'], uploaded_file[0].name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file[0].getbuffer())
                
                st.success(f"""File is saved with name {uploaded_file[0].name}.
                           
                           All results are stored temporarily and will be deleted on refreshing or closing the browser.
                           
                           """)
            
            st.session_state.hdf5_upload = True

        

    def retrieve_h5_data(self, uploaded_file):
        results = []

        with h5py.File(uploaded_file, "r") as f:

            number_of_states = int(f['number_of_states'][()])

            time_values = np.array(f['time_values'][:])
            cell_voltage = np.array(f['cell_voltage'][:])
            cell_current = np.array(f['cell_current'][:])

            negative_electrode_grid = np.array(f['grids/negative_electrode_grid'][:])
            negative_electrode_grid_bc = np.array(f['grids/negative_electrode_grid_bc'][()])
            positive_electrode_grid = np.array(f['grids/positive_electrode_grid'][:])
            positive_electrode_grid_bc = np.array(f['grids/positive_electrode_grid_bc'][()])
            electrolyte_grid = np.array(f['grids/electrolyte_grid'][:])
            electrolyte_grid_bc = np.array(f['grids/electrolyte_grid_bc'][()])

            negative_electrode_concentration = []
            positive_electrode_concentration = []
            electrolyte_concentration = []

            negative_electrode_potential = []
            positive_electrode_potential = []
            electrolyte_potential = []

            for i in range(number_of_states):
                ne_conc = np.array(f[f'concentrations/negative_electrode/ne_c_state_{i+1}'][()])
                pe_conc = np.array(f[f'concentrations/positive_electrode/pe_c_state_{i+1}'][()])
                elyte_conc = np.array(f[f'concentrations/electrolyte/elyte_c_state_{i+1}'][()])

                ne_pot = np.array(f[f'potentials/negative_electrode/ne_p_state_{i+1}'][()])
                pe_pot = np.array(f[f'potentials/positive_electrode/pe_p_state_{i+1}'][()])
                elyte_pot = np.array(f[f'potentials/electrolyte/elyte_p_state_{i+1}'][()])

                negative_electrode_concentration.append(ne_conc)
                positive_electrode_concentration.append(pe_conc)
                electrolyte_concentration.append(elyte_conc)

                negative_electrode_potential.append(ne_pot)
                positive_electrode_potential.append(pe_pot)
                electrolyte_potential.append(elyte_pot)

            
            ne_electrode_ml_value = f["indicators/negative_electrode/electrode/mass_loading/value"][()]
            ne_electrode_ml_unit = f["indicators/negative_electrode/electrode/mass_loading/unit"][()]
            ne_electrode_thi_value = f["indicators/negative_electrode/electrode/coating_thickness/value"][()]
            ne_electrode_thi_unit = f["indicators/negative_electrode/electrode/coating_thickness/unit"][()]
            ne_electrode_po_value = f["indicators/negative_electrode/electrode/coating_porosity/value"][()]
            ne_electrode_po_unit = f["indicators/negative_electrode/electrode/coating_porosity/unit"][()]
            ne_electrode_cap_value = f["indicators/negative_electrode/electrode/capacity/value"][()]
            ne_electrode_cap_unit = f["indicators/negative_electrode/electrode/capacity/unit"][()]
            ne_am_cap_value = f["indicators/negative_electrode/active_material/specific_capacity/value"][()]
            ne_am_cap_unit = f["indicators/negative_electrode/active_material/specific_capacity/unit"][()]

            pe_electrode_ml_value = f["indicators/positive_electrode/electrode/mass_loading/value"][()]
            pe_electrode_ml_unit = f["indicators/positive_electrode/electrode/mass_loading/unit"][()]
            pe_electrode_thi_value = f["indicators/positive_electrode/electrode/coating_thickness/value"][()]
            pe_electrode_thi_unit = f["indicators/positive_electrode/electrode/coating_thickness/unit"][()]
            pe_electrode_po_value = f["indicators/positive_electrode/electrode/coating_porosity/value"][()]
            pe_electrode_po_unit = f["indicators/positive_electrode/electrode/coating_porosity/unit"][()]
            pe_electrode_cap_value = f["indicators/positive_electrode/electrode/capacity/value"][()]
            pe_electrode_cap_unit = f["indicators/positive_electrode/electrode/capacity/unit"][()]
            pe_am_cap_value = f["indicators/positive_electrode/active_material/specific_capacity/value"][()]
            pe_am_cap_unit = f["indicators/positive_electrode/active_material/specific_capacity/unit"][()]

            cell_cap_value = f["indicators/cell/capacity/value"][()]
            cell_cap_unit = f["indicators/cell/capacity/unit"][()]
            cell_mass_value = f["indicators/cell/cell_mass/value"][()]
            cell_mass_unit = f["indicators/cell/cell_mass/unit"][()]
            cell_np_value = f["indicators/cell/n_to_p_ratio/value"][()]
            cell_np_unit = f["indicators/cell/n_to_p_ratio/unit"][()]

            results = [
                f['log_messages'][:].tolist() if 'log_messages' in f else [],
                number_of_states,
                cell_voltage,
                cell_current,
                time_values,
                negative_electrode_grid,
                negative_electrode_grid_bc,
                electrolyte_grid,
                electrolyte_grid_bc,
                positive_electrode_grid,
                positive_electrode_grid_bc,
                negative_electrode_concentration,
                electrolyte_concentration,
                positive_electrode_concentration,
                negative_electrode_potential,
                electrolyte_potential,
                positive_electrode_potential
            ]

            indicators = [
                ne_electrode_ml_value,
                ne_electrode_ml_unit,
                ne_electrode_thi_value,
                ne_electrode_thi_unit,
                ne_electrode_po_value,
                ne_electrode_po_unit,
                ne_electrode_cap_value,
                ne_electrode_cap_unit,
                ne_am_cap_value,
                ne_am_cap_unit ,

                pe_electrode_ml_value,
                pe_electrode_ml_unit,
                pe_electrode_thi_value,
                pe_electrode_thi_unit,
                pe_electrode_po_value,
                pe_electrode_po_unit ,
                pe_electrode_cap_value ,
                pe_electrode_cap_unit,
                pe_am_cap_value ,
                pe_am_cap_unit,

                cell_cap_value ,
                cell_cap_unit,
                cell_mass_value,
                cell_mass_unit ,
                cell_np_value ,
                cell_np_unit

            ]

        return results, indicators

class SetDataSetSelector():
    def __init__(self):
        self.header = "Select data to visualize/compare"
        self.session_temp_folder = st.session_state["temp_dir"]

    def set_selector(self):


        with st.sidebar:

            # Remember user changed values when switching between pages
            for k, v in st.session_state.items():
                st.session_state[k] = v


            st.markdown("## " + self.header)

            file_names = [f for f in os.listdir(self.session_temp_folder) if os.path.isfile(os.path.join(self.session_temp_folder, f))]
            selected = st.multiselect(label="Select data",options= list(file_names), label_visibility="collapsed",default = st.session_state["selected_data"])
            st.session_state["selected_data"] = selected
        return  selected

class SetGraphs():
    """
    Used to render the graphs on the Results page.
    """
    def __init__(_self,results,selected_data_sets):

        _self.header = "Visualize results"
        _self.dashboard_header = "Dynamic dashboard"
        _self.selected_data_sets = selected_data_sets
        _self.results = results


        _self.set_graphs()

    def set_graphs(_self):


        #dynamic, colormaps = _self.set_graph_toggles()

        #if dynamic:

        st.markdown("# " + _self.dashboard_header)

        st_space(space_number=1, space_width= 3 )

        _self.structure_results()

        _self.set_dynamic_dashboard()

        #if colormaps:
        # _self.set_colormaps()

    def structure_results(_self):

        if isinstance(_self.selected_data_sets,list) and len(_self.selected_data_sets) >1:
            _self.log_messages = []
            _self.number_of_states = []
            _self.cell_voltage = []
            _self.cell_current = []
            _self.time_values = []
            _self.negative_electrode_grid = []
            _self.negative_electrode_grid_bc = []
            _self.electrolyte_grid = []
            _self.electrolyte_grid_bc = []
            _self.positive_electrode_grid = []
            _self.positive_electrode_grid_bc = []
            _self.negative_electrode_concentration = []
            _self.electrolyte_concentration = []
            _self.positive_electrode_concentration = []
            _self.negative_electrode_potential = []
            _self.electrolyte_potential = []
            _self.positive_electrode_potential = []

            for i,result in enumerate(_self.results):


                [
                log_messages,
                number_of_states,
                cell_voltage,
                cell_current,
                time_values,
                negative_electrode_grid,
                negative_electrode_grid_bc,
                electrolyte_grid,
                electrolyte_grid_bc,
                positive_electrode_grid,
                positive_electrode_grid_bc,
                negative_electrode_concentration,
                electrolyte_concentration,
                positive_electrode_concentration,
                negative_electrode_potential,
                electrolyte_potential,
                positive_electrode_potential
                ] = result

                def array_and_transpose(data):
                    data = np.array(data)
                    if data.ndim > 1:
                        if len(data[0]) > len(data[:,0]):
                            data = np.transpose(data)

                    return data

                _self.log_messages.append(log_messages)
                _self.number_of_states.append(array_and_transpose(number_of_states))
                _self.cell_voltage.append(array_and_transpose(cell_voltage))
                _self.cell_current.append(array_and_transpose(cell_current))
                _self.time_values.append(array_and_transpose(time_values))
                _self.negative_electrode_grid.append(array_and_transpose(negative_electrode_grid))
                _self.negative_electrode_grid_bc.append(array_and_transpose(negative_electrode_grid_bc))
                _self.electrolyte_grid.append(array_and_transpose(electrolyte_grid))
                _self.electrolyte_grid_bc.append(array_and_transpose(electrolyte_grid_bc))
                _self.positive_electrode_grid.append(array_and_transpose(positive_electrode_grid))
                _self.positive_electrode_grid_bc.append(array_and_transpose(positive_electrode_grid_bc))
                _self.negative_electrode_concentration.append(array_and_transpose(negative_electrode_concentration))
                _self.electrolyte_concentration.append(array_and_transpose(electrolyte_concentration))
                _self.positive_electrode_concentration.append(array_and_transpose(positive_electrode_concentration))
                _self.negative_electrode_potential.append(array_and_transpose(negative_electrode_potential))
                _self.electrolyte_potential.append(array_and_transpose(electrolyte_potential))
                _self.positive_electrode_potential.append(array_and_transpose(positive_electrode_potential))

        else:
    
            [
            _self.log_messages,
            _self.number_of_states,
            _self.cell_voltage,
            _self.cell_current,
            _self.time_values,
            _self.negative_electrode_grid,
            _self.negative_electrode_grid_bc,
            _self.electrolyte_grid,
            _self.electrolyte_grid_bc,
            _self.positive_electrode_grid,
            _self.positive_electrode_grid_bc,
            _self.negative_electrode_concentration,
            _self.electrolyte_concentration,
            _self.positive_electrode_concentration,
            _self.negative_electrode_potential,
            _self.electrolyte_potential,
            _self.positive_electrode_potential
            ] = _self.results


    def set_graph_toggles(_self):

        #dash, color = st.columns((2,5))
        with st.sidebar:


            display_dynamic_dashboard = st.toggle(
                label="Dynamic dashboard",
                value=True
            )


            display_colormaps = st.toggle(
                label="Colormaps",
                value=False
            )



        #st.divider()
        return display_dynamic_dashboard, display_colormaps

    def set_dynamic_dashboard(_self):

        if isinstance(_self.selected_data_sets,list) and len(_self.selected_data_sets) > 1:
            time_values = _self.find_max_length_array_x_axis(_self.time_values)
            
        else:
            time_values = _self.time_values

        
        max_time_value = max(time_values)
        init_time_value = 0.0
        step_size = _self.get_min_difference(time_values)
        selected_time = st.slider(
            key = "DynamicDashboard",
            label="Select a time (hours)",
            min_value=init_time_value,
            max_value= max_time_value,
            step=step_size
            )


        state = 0
        time = time_values[state]
        while time < selected_time:
            state += 1
            time = time_values[state]

        _self.view_plots_static(state)

    # def set_colormaps(_self):
        # Colormaps


        # with st.sidebar:
        #     select = st.multiselect(label= "Select contour plots.",
        #                             options=["Negative electrode concentration", "Positive electrode concentration",
        #                                      "Negative electrode potential", "Positive electrode potential",
        #                                      "Electrolyte concentration", "Electrolyte potential" ],
        #                                      key = "multi_contour_plots"
        #                                      )

        # #col1, col2= st.columns(2)
        # for choice in select:
        #     if choice == "Negative electrode concentration":
        #         st.plotly_chart(_self.get_ne_c_color())
        #     if choice == "Positive electrode concentration":
        #         st.plotly_chart(_self.get_pe_c_color())
        #     if choice == "Negative electrode potential":
        #         st.plotly_chart(_self.get_ne_p_color())
        #     if choice == "Positive electrode potential":
        #         st.plotly_chart(_self.get_pe_p_color())
        #     if choice == "Electrolyte concentration":
        #         st.plotly_chart(_self.get_elyte_c_color())
        #     if choice == "Electrolyte potential":
        #         st.plotly_chart(_self.get_elyte_p_color())


    @st.cache_data
    def get_elyte_p_color(_self,state):
        return _self.create_colormap(
            x_data=_self.electrolyte_grid,
            y_data=_self.time_values,
            z_data=_self.electrolyte_potential,
            title="Electrolyte - Potential",
            x_label="Position  /  \u00B5m",
            y_label="Time  /  h",
            cbar_label="Potential  /  V",
            horizontal_line=_self.time_values[state]
        )

    @st.cache_data
    def get_elyte_c_color(_self,state):
        return _self.create_colormap(
            x_data=_self.electrolyte_grid,
            y_data=_self.time_values,
            z_data=_self.electrolyte_concentration,
            title="Electrolyte - Liquid phase lithium concentration",
            x_label="Position  /  \u00B5m",
            y_label="Time  /  h",
            cbar_label="Concentration  /  mol . L-1",
            horizontal_line=_self.time_values[state]
        )

    @st.cache_data
    def get_pe_p_color(_self,state):
        return _self.create_colormap(
            x_data=_self.positive_electrode_grid,
            y_data=_self.time_values,
            z_data=_self.positive_electrode_potential,
            title="Positive Electrode - Potential",
            x_label="Position  /  \u00B5m",
            y_label="Time  /  h",
            cbar_label="Potential  /  V",
            horizontal_line=_self.time_values[state]
        )

    @st.cache_data
    def get_pe_c_color(_self,state):
        return _self.create_colormap(
            x_data=_self.positive_electrode_grid,
            y_data=_self.time_values,
            z_data=np.array(_self.positive_electrode_concentration),
            title="Positive Electrode - Solid phase lithium concentration",
            x_label="Position  /  \u00B5m",
            y_label="Time  /  h",
            cbar_label="Concentration  /  mol . L-1",
            horizontal_line=_self.time_values[state]
        )

    @st.cache_data
    def get_ne_c_color(_self,state):
        return _self.create_colormap(
            x_data=_self.negative_electrode_grid,
            y_data=_self.time_values,
            z_data=_self.negative_electrode_concentration,
            title="Negative Electrode - Solid phase lithium concentration",
            x_label="Position  / \u00B5m",
            y_label="Time  /  h",
            cbar_label="Concentration  /  mol . L-1",
            horizontal_line=_self.time_values[state]
        )


    @st.cache_data
    def get_ne_p_color(_self,state):
        return _self.create_colormap(
            x_data=_self.negative_electrode_grid,
            y_data=_self.time_values,
            z_data=_self.negative_electrode_potential,
            title="Negative Electrode - Potential",
            x_label="Position  /  \u00B5m",
            y_label="Time  /  h",
            cbar_label="Potential  /  V",
            horizontal_line=_self.time_values[state]
        )

    def create_colormap(_self,x_data, y_data, z_data, title, x_label, y_label, cbar_label, horizontal_line = None):


        x_data = np.squeeze(np.array(x_data))
        y_data = np.array(y_data)

        x_color, y_color = np.meshgrid(x_data, y_data)

        fig = go.Figure(data = go.Contour(
                                    z=z_data,
                                    y=y_data,
                                    x = x_data,
                                    colorbar=dict(title=cbar_label),
                                    ))
        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label
        )

        if horizontal_line:
            fig.add_shape(
                type="line",
                x0=0,  # x-coordinate of the start of the line
                x1=1,  # x-coordinate of the end of the line (1 corresponds to 100% of the x-axis range)
                y0=horizontal_line,  # y-coordinate of the line
                y1=horizontal_line,  # y-coordinate of the line
                xref='paper',  # x-reference to the plotting area (paper coordinates)
                yref='y',  # y-reference to the y-axis
                line=dict(
                    color="grey",
                    width=3,
                    dash = "dash"
                )
            )
        # fig.update_yaxes(
        #     range=[0,1/crate[0]],  # sets the range of xaxis
        #     constrain="domain",  # meanwhile compresses the xaxis by decreasing its "domain"
        # )

        # x_color, y_color = np.meshgrid(x_data, y_data)
        # fig, ax = plt.subplots()

        # # Precision is set to 100 (change to 10 for lower precision, to 1000 for higher precision)
        # # The lower the precision, the faster it runs
        # color_map = ax.contourf(x_color, y_color, z_data, 100)
        # cbar = fig.colorbar(color_map)
        # cbar.ax.set_ylabel(cbar_label)

        # ax.set_title(title)
        # ax.set_xlabel(x_label)
        # ax.set_ylabel(y_label)

        return fig


    @st.cache_data
    def get_min_difference(_self, time_values):
        diff = []
        n = len(time_values)
        for i in range(1, n):
            diff.append(round(time_values[i] - time_values[i - 1], 5))
        return float(min(diff))
    
    def find_max_length_array_x_axis(self,arrays):

        max_length = 0
        max_array = None

        # Find the maximum length
        for index, array in enumerate(arrays):
            if isinstance(array, np.ndarray):
                current_length = array.shape[0] if len(array.shape) == 2 else len(array)
            else:  # Handle lists
                current_length = len(array) if isinstance(array, list) else 0

            if current_length > max_length:
                max_length = current_length
                max_array = array

        return max_array


    
    def find_max_length_array_y_axis(self,arrays):
        if not arrays:  # Check if the list is empty
            return None, 0, -1

        max_length_1 = 0
        max_length_2 = 0
        max_array = None
        max_index = -1

        # Find the maximum length
        for index, array in enumerate(arrays):
            if len(array.shape) == 1:
                current_length_1 = len(array)
                if current_length_1 > max_length_1:
                    max_length_1 = current_length_1
                    max_array = array
                    max_index = index
            else:
                current_length_1 = len(array[:,0])
                current_length_2 = len(array[0])

                if current_length_1 > max_length_1:
                    max_length_1 = current_length_1
                    max_array = array
                    max_index = index

                if current_length_2 > max_length_2:
                    max_length_2 = current_length_2
                    max_array = array
                    max_index = index
                
                
    
        # Extend smaller arrays with np.nan
        for index, array in enumerate(arrays):
            if len(array.shape) == 1:
                if len(array) < max_length_1:
                    arrays[index] = np.append(array, [np.nan] * (max_length_1 - len(array)))
            elif len(array.shape) == 2:
                if len(array[:,0]) < max_length_1:
                    diff = max_length_1 - len(array[:,0])
                    nan_array = np.full((diff, len(array[0])), np.nan)
                    arrays[index] = np.vstack((array, nan_array))
                if len(array[0]) < max_length_2:
                    diff = max_length_2 - len(array[0])
                    nan_array = np.full((len(array[:,0]), diff), np.nan)
                    arrays[index] = np.hstack((arrays[index], nan_array))
                    

        return arrays


    def view_plots_static(_self,state):

        initial_graph_limits = _self.get_graph_initial_limits()
        xmin = initial_graph_limits[0]
        xmax = initial_graph_limits[1]
        [
            cmax_elyte_sub,
            cmin_elyte_sub,
            cmax_ne_sub,
            cmin_ne_sub,
            cmax_pe_sub,
            cmin_pe_sub,
            phimax_elyte_sub,
            phimin_elyte_sub,
            phimax_ne_sub,
            phimin_ne_sub,
            phimax_pe_sub,
            phimin_pe_sub,
            cmin_elyte,
            cmax_elyte,
            cmin_ne,
            cmax_ne,
            cmin_pe,
            cmax_pe,
            phimax_elyte,
            phimin_elyte,
            phimax_ne,
            phimin_ne,
            phimax_pe,
            phimin_pe
        ] = _self.get_graph_limits_from_state(state)

        # Negative Electrode Concentration
        if isinstance(_self.electrolyte_grid[0],float):
            length_grid_elyte = len(_self.electrolyte_grid)
            length_grid_NE = len(_self.negative_electrode_grid)
            number_of_datasets = None
            negative_electrode_concentration_ext_list = np.full(length_grid_elyte, np.nan)
            negative_electrode_concentration_ext_list[0:length_grid_NE] = np.squeeze(_self.negative_electrode_concentration)[state]
            electrolyte_grid = _self.electrolyte_grid
        else:
            
            length_grid_elyte = len(_self.find_max_length_array_x_axis(_self.electrolyte_grid))
            number_of_datasets = len(_self.electrolyte_grid)
            negative_electrode_concentration_ext_list = []
            electrolyte_grid = _self.find_max_length_array_y_axis(_self.electrolyte_grid)
            

            _self.negative_electrode_concentration = _self.find_max_length_array_y_axis(_self.negative_electrode_concentration)
            
            
            for i,dataset in enumerate(_self.negative_electrode_concentration):
                length_grid_NE = len(dataset[0])
                negative_electrode_concentration_ext = np.full(length_grid_elyte, np.nan)
                
                negative_electrode_concentration_ext[0:length_grid_NE] = dataset[state]
                negative_electrode_concentration_ext_list.append(negative_electrode_concentration_ext)


        ne_concentration = _self.create_subplot(
            x_data=electrolyte_grid,
            y_data=negative_electrode_concentration_ext_list,
            title="Negative Electrode - Solid phase lithium concentration  /  mol . L-1",
            x_label="Position  /  \u00B5m",
            y_label="Concentration  /  mol . L-1",
            x_min=xmin,
            x_max=xmax,
            y_min=cmin_ne,
            y_max=cmax_ne,
            y_min_sub = cmin_ne_sub,
            y_max_sub = cmax_ne_sub
        )

        # Electrolyte Concentration
        if isinstance(_self.electrolyte_grid[0],float):
            elyte_concentration_ext_list = _self.electrolyte_concentration[state]
            electrolyte_grid = _self.electrolyte_grid
            number_of_datasets = None

        else:

            elyte_concentration_ext_list = []
            electrolyte_grid = _self.find_max_length_array_y_axis(_self.electrolyte_grid)

            _self.electrolyte_concentration = _self.find_max_length_array_y_axis(_self.electrolyte_concentration)


            for i,dataset in enumerate(_self.electrolyte_concentration):
                elyte_concentration_ext_list.append(dataset[state])
        elyte_concentration = _self.create_subplot(
            x_data=electrolyte_grid,
            y_data=elyte_concentration_ext_list,
            title="Electrolyte - Liquid phase lithium concentration  /  mol . L-1",
            x_label="Position  /  \u00B5m",
            y_label="Concentration  /  mol . L-1",
            x_min=xmin,
            x_max=xmax,
            y_min=cmin_elyte,
            y_max=cmax_elyte,
            y_min_sub = cmin_elyte_sub,
            y_max_sub = cmax_elyte_sub
        )

        # Positive Electrode Concentration
        if isinstance(_self.electrolyte_grid[0],float):
            length_grid_elyte = len(_self.electrolyte_grid)
            length_grid_PE = len(_self.positive_electrode_grid)
            number_of_datasets = None
            positive_electrode_concentration_ext_list = np.full(length_grid_elyte, np.nan)
            positive_electrode_concentration_ext_list[-length_grid_PE:] = np.squeeze(_self.positive_electrode_concentration)[state]
            electrolyte_grid = _self.electrolyte_grid
        else:

            length_grid_elyte = len(_self.find_max_length_array_x_axis(_self.electrolyte_grid))
            electrolyte_grid = _self.find_max_length_array_y_axis(_self.electrolyte_grid)
            _self.positive_electrode_concentration = _self.find_max_length_array_y_axis(_self.positive_electrode_concentration)


            positive_electrode_concentration_ext_list = []

            for i,dataset in enumerate(_self.positive_electrode_concentration):
                length_grid_PE = len(dataset[0])
                positive_electrode_concentration_ext = np.full(length_grid_elyte, np.nan)
                positive_electrode_concentration_ext[-length_grid_PE:]  = dataset[state]
                positive_electrode_concentration_ext_list.append(positive_electrode_concentration_ext)

        pe_concentration = _self.create_subplot(
            x_data=electrolyte_grid,
            y_data=positive_electrode_concentration_ext_list,
            title="Positive Electrode - Solid phase lithium concentration  /  mol . L-1",
            x_label="Position  /  \u00B5m",
            y_label="Concentration  /  mol . L-1",
            x_min=xmin,
            x_max=xmax,
            y_min=cmin_pe,
            y_max=cmax_pe,
            y_min_sub = cmin_pe_sub,
            y_max_sub = cmax_pe_sub
        )

        # Cell Current
        if isinstance(_self.electrolyte_grid[0],float):
            time_values_list = _self.time_values
            vertical_line = _self.time_values[state]

        else:
            _self.cell_current = _self.find_max_length_array_y_axis(_self.cell_current)
            time_values_list = _self.find_max_length_array_y_axis(_self.time_values)
            vertical_line = _self.find_max_length_array_x_axis(_self.time_values)[state]


        cell_current_fig = _self.create_subplot(
            x_data=time_values_list,
            y_data=_self.cell_current,
            title="Cell Current  /  A",
            x_label="Time  /  h",
            y_label="Cell Current  /  A",
            vertical_line= vertical_line
        )

        # Negative Electrode Potential

        if isinstance(_self.electrolyte_grid[0],float):
            length_grid_elyte = len(_self.electrolyte_grid)
            length_grid_NE = len(_self.negative_electrode_grid)
            number_of_datasets = None
            negative_electrode_potential_ext_list = np.full(length_grid_elyte, np.nan)
            negative_electrode_potential_ext_list[0:length_grid_NE] = np.squeeze(_self.negative_electrode_potential)[state]
            electrolyte_grid = _self.electrolyte_grid
        else:
            length_grid_elyte = len(_self.find_max_length_array_x_axis(_self.electrolyte_grid))
            electrolyte_grid = _self.find_max_length_array_y_axis(_self.electrolyte_grid)
            _self.negative_electrode_potential = _self.find_max_length_array_y_axis(_self.negative_electrode_potential)

            negative_electrode_potential_ext_list = []

            for i,dataset in enumerate(_self.negative_electrode_potential):
                length_grid_NE = len(dataset[0])
                negative_electrode_potential_ext = np.full(length_grid_elyte, np.nan)
                negative_electrode_potential_ext[0:length_grid_NE] = dataset[state]
                negative_electrode_potential_ext_list.append(negative_electrode_potential_ext)

        ne_potential = _self.create_subplot(
            x_data=electrolyte_grid,
            y_data=negative_electrode_potential_ext_list,
            title="Negative Electrode - Potential  /  V",
            x_label="Position  /  \u00B5m",
            y_label="Potential  /  V",
            x_min=xmin,
            x_max=xmax,
            y_min=phimin_ne,
            y_max=phimax_ne,
            y_min_sub = phimin_ne_sub,
            y_max_sub = phimax_ne_sub
        )

        # Electrolyte Potential
        if isinstance(_self.electrolyte_grid[0],float):
            elyte_potential_ext_list = _self.electrolyte_potential[state]
            electrolyte_grid = _self.electrolyte_grid
            number_of_datasets = None

        else:
            elyte_potential_ext_list = []
            electrolyte_grid = _self.find_max_length_array_y_axis(_self.electrolyte_grid)
            _self.electrolyte_potential = _self.find_max_length_array_y_axis(_self.electrolyte_potential)


            for i,dataset in enumerate(_self.electrolyte_potential):
                elyte_potential_ext_list.append(dataset[state])

        elyte_potential = _self.create_subplot(
            x_data=electrolyte_grid,
            y_data=elyte_potential_ext_list,
            title="Electrolyte - Potential  /  V",
            x_label="Position  /  \u00B5m",
            y_label="Potential  /  V",
            x_min=xmin,
            x_max=xmax,
            y_min=phimin_elyte,
            y_max=phimax_elyte,
            y_min_sub = phimin_elyte_sub,
            y_max_sub = phimax_elyte_sub
        )

        # Positive Electrode Potential
        if isinstance(_self.electrolyte_grid[0],float):
            length_grid_elyte = len(_self.electrolyte_grid)
            length_grid_PE = len(_self.positive_electrode_grid)
            number_of_datasets = None
            positive_electrode_potential_ext_list = np.full(length_grid_elyte, np.nan)
            positive_electrode_potential_ext_list[-length_grid_PE:] = np.squeeze(_self.positive_electrode_potential)[state]
            electrolyte_grid = _self.electrolyte_grid
        else:
            length_grid_elyte = len(_self.find_max_length_array_x_axis(_self.electrolyte_grid))
            electrolyte_grid = _self.find_max_length_array_y_axis(_self.electrolyte_grid)
            _self.positive_electrode_potential = _self.find_max_length_array_y_axis(_self.positive_electrode_potential)


            positive_electrode_potential_ext_list = []

            for i,dataset in enumerate(_self.positive_electrode_potential):
                length_grid_PE = len(dataset[0])
                positive_electrode_potential_ext = np.full(length_grid_elyte, np.nan)
                positive_electrode_potential_ext[-length_grid_PE:]  = dataset[state]
                positive_electrode_potential_ext_list.append(positive_electrode_potential_ext)

        pe_potential = _self.create_subplot(
            x_data=electrolyte_grid,
            y_data=positive_electrode_potential_ext_list,
            title="Positive Electrode - Potential  /  V",
            x_label="Position  /  \u00B5m",
            y_label="Potential  /  V",
            x_min=xmin,
            x_max=xmax,
            y_min=phimin_pe,
            y_max=phimax_pe,
            y_min_sub = phimin_pe_sub,
            y_max_sub = phimax_pe_sub

        )

        # Cell Voltage
        if isinstance(_self.electrolyte_grid[0],float):
            time_values_list = _self.time_values
            vertical_line = _self.time_values[state]

        else:

            time_values_list = _self.find_max_length_array_y_axis(_self.time_values)
            _self.cell_voltage = _self.find_max_length_array_y_axis(_self.cell_voltage)
            vertical_line = _self.find_max_length_array_x_axis(_self.time_values)[state]


        cell_voltage_fig = _self.create_subplot(
            x_data=time_values_list,
            y_data=_self.cell_voltage,
            title="Cell Voltage  /  V",
            x_label="Time  /  h",
            y_label = "Cell Voltage  /  V",
            vertical_line=vertical_line
        )

        ######################
        # Set streamlit plot
        ######################


        # import streamlit.components.v1 as components

        # # Plotly imports
        # import plotly.graph_objects as go

        # Create a Plotly graph
        # fig = go.Figure()
        # fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 1, 2], mode='lines'))

        # # Convert the Plotly graph to HTML
        # plotly_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

        # # Define the layout for the dashboard items
        # layout = [
        #     el.dashboard.Item("plotly_chart", 0, 0, 2, 2)  # Adjust position and size as needed
        # ]

        # # Create the dashboard layout
        # with el.elements("nested_children"):
        #     with el.dashboard.Grid(layout):
        #         # Embed the Plotly chart within the Paper component
        #         with el.mui.Paper(key="plotly_chart"):
        #             components.html(plotly_html, width=600, height=400)


        # with st.sidebar:
        #     st.markdown("## " + _self.header)
        #     select = st.multiselect(label= "Select line plots.",
        #                             options=["Cell current","Cell voltage", "Negative electrode concentration",
        #                                      "Positive electrode concentration", "Negative electrode potential",
        #                                      "Positive electrode potential", "Electrolyte concentration", "Electrolyte potential" ],
        #                                      default= "Cell voltage",
        #                                      key = "multi_line_plots"
        #                                      )

        # #col1, col2= st.columns(2)
        # for choice in select:
        #     if choice == "Cell current":
        #         st.plotly_chart(cell_current_fig, clear_figure=True)
        #     if choice == "Cell voltage":
        #         st.plotly_chart(cell_voltage_fig, clear_figure=True)
        #     if choice == "Negative electrode concentration":
        #         st.plotly_chart(ne_concentration, clear_figure=True)
        #     if choice == "Positive electrode concentration":
        #         st.plotly_chart(pe_concentration, clear_figure=True)
        #     if choice == "Negative electrode potential":
        #         st.plotly_chart(ne_potential, clear_figure=True)
        #     if choice == "Positive electrode potential":
        #         st.plotly_chart(pe_potential, clear_figure=True)
        #     if choice == "Electrolyte concentration":
        #         st.plotly_chart(elyte_concentration, clear_figure=True)
        #     if choice == "Electrolyte potential":
        #         st.plotly_chart(elyte_potential, clear_figure=True)

        voltage,current = st.columns(2)

        voltage.plotly_chart(cell_voltage_fig, clear_figure=True, use_container_width = True)
        current.plotly_chart(cell_current_fig, clear_figure=True, use_container_width = True)

        if number_of_datasets:

            use_container_width = False
            use_color_plots = None

        else:
            use_container_width = True
            use_color_plots = True

        with st.expander("Electrolyte"):

            conc1,pot1 = st.tabs(["Concentration", "Potential"])

            with conc1:
                line1,color1 = st.columns(2)

                line1.plotly_chart(elyte_concentration, clear_figure=True,use_container_width = use_container_width)
                if use_color_plots:
                    color1.plotly_chart(_self.get_elyte_c_color(state),use_container_width = use_container_width)

            with pot1:
                line2,color2 = st.columns(2)

                line2.plotly_chart(elyte_potential, clear_figure=True,use_container_width = use_container_width)
                if use_color_plots:
                    color2.plotly_chart(_self.get_elyte_p_color(state),use_container_width = use_container_width)


        with st.expander("Negative electrode"):

            conc2,pot2 = st.tabs(["Concentration", "Potential"])
            with conc2:
                line3, color3 = st.columns(2)

                line3.plotly_chart(ne_concentration, clear_figure=True,use_container_width = use_container_width)
                if use_color_plots:
                    color3.plotly_chart(_self.get_ne_c_color(state),use_container_width = use_container_width)
            with pot2:
                line4,color4 = st.columns(2)

                line4.plotly_chart(ne_potential, clear_figure=True,use_container_width = use_container_width)
                if use_color_plots:
                    color4.plotly_chart(_self.get_ne_p_color(state),use_container_width = use_container_width)


        with st.expander("Positive electrode"):

            conc3,pot3 = st.tabs(["Concentration", "Potential"])
            with conc3:
                line5,color5 = st.columns(2)

                line5.plotly_chart(pe_concentration, clear_figure=True,use_container_width = use_container_width)
                if use_color_plots:
                    color5.plotly_chart(_self.get_pe_c_color(state),use_container_width = use_container_width)

            with pot3:
                line6,color6 = st.columns(2)

                line6.plotly_chart(pe_potential, clear_figure=True,use_container_width = use_container_width)
                if use_color_plots:
                    color6.plotly_chart(_self.get_pe_p_color(state),use_container_width = use_container_width)

    @st.cache_data
    def find_max(_self,data, state = None):
            if isinstance(_self.selected_data_sets, list) and len(_self.selected_data_sets) > 1:
                if state:
                    maxi = max(np.max(array[state]) for array in data)
                else:
                    maxi = max(np.max(array) for array in data)
            else:
                if state:
                    maxi = np.max(data[state])
                else:   
                    maxi = np.max(data)
            return maxi

    @st.cache_data
    def find_min(_self,data, state = None):
            if isinstance(_self.selected_data_sets, list) and len(_self.selected_data_sets) > 1:
                mini = min(np.min(array) for array in data)
            else:
                mini = np.min(data)
            return mini


    @st.cache_data
    def get_graph_initial_limits(_self):

        xmin = _self.find_min(_self.electrolyte_grid_bc)

        xmax = _self.find_max(_self.electrolyte_grid_bc)

        cmax_elyte = _self.find_max(_self.electrolyte_concentration)
        cmin_elyte = _self.find_min(_self.electrolyte_concentration)

        cmax_ne = _self.find_max(_self.negative_electrode_concentration)
        cmin_ne = _self.find_min(_self.negative_electrode_concentration)

        cmax_pe = _self.find_max(_self.positive_electrode_concentration)
        cmin_pe = _self.find_min(_self.positive_electrode_concentration)

        phimax_elyte = _self.find_max(_self.electrolyte_potential)
        phimin_elyte = _self.find_min(_self.electrolyte_potential)

        phimax_ne = _self.find_max(_self.negative_electrode_potential)
        phimin_ne = _self.find_min(_self.negative_electrode_potential)

        phimax_pe = _self.find_max(_self.positive_electrode_potential)
        phimin_pe = _self.find_min(_self.positive_electrode_potential)

        return [
            xmin,
            xmax,
            cmin_elyte,
            cmax_elyte,
            cmin_ne,
            cmax_ne,
            cmin_pe,
            cmax_pe,
            phimax_elyte,
            phimin_elyte,
            phimax_ne,
            phimin_ne,
            phimax_pe,
            phimin_pe
        ]

    @st.cache_data
    def get_graph_limits_from_state(_self,state):
        [
            xmin,
            xmax,
            init_cmin_elyte,
            init_cmax_elyte,
            init_cmin_ne,
            init_cmax_ne,
            init_cmin_pe,
            init_cmax_pe,
            init_phimax_elyte,
            init_phimin_elyte,
            init_phimax_ne,
            init_phimin_ne,
            init_phimax_pe,
            init_phimin_pe
        ] = _self.get_graph_initial_limits()

        cmax_elyte_sub = _self.find_max(_self.electrolyte_concentration,state)
        cmin_elyte_sub = _self.find_min(_self.electrolyte_concentration,state)

        cmax_ne_sub = _self.find_max(_self.negative_electrode_concentration,state)
        cmin_ne_sub = _self.find_min(_self.negative_electrode_concentration,state)

        cmax_pe_sub = _self.find_max(_self.positive_electrode_concentration,state)
        cmin_pe_sub = _self.find_min(_self.positive_electrode_concentration,state)

        phimax_elyte_sub = _self.find_max(_self.electrolyte_potential,state)
        phimin_elyte_sub = _self.find_min(_self.electrolyte_potential,state)

        phimax_ne_sub = _self.find_max(_self.negative_electrode_potential,state)
        phimin_ne_sub = _self.find_min(_self.negative_electrode_potential,state)

        phimax_pe_sub = _self.find_max(_self.positive_electrode_potential,state)
        phimin_pe_sub = _self.find_min(_self.positive_electrode_potential,state)

        cmax_elyte = max(init_cmax_elyte, cmax_elyte_sub)
        cmin_elyte = min(init_cmin_elyte, cmin_elyte_sub)

        cmax_ne = max(init_cmax_ne, cmax_ne_sub)
        cmin_ne = min(init_cmin_ne, cmin_ne_sub)

        cmax_pe = max(init_cmax_pe, cmax_pe_sub)
        cmin_pe = min(init_cmin_pe, cmin_pe_sub)

        phimax_elyte = max(init_phimax_elyte, phimax_elyte_sub)
        phimin_elyte = min(init_phimin_elyte, phimin_elyte_sub)

        phimax_ne = max(init_phimax_ne, phimax_ne_sub)
        phimin_ne = min(init_phimin_ne, phimin_ne_sub)

        phimax_pe = max(init_phimax_pe, phimax_pe_sub)
        phimin_pe = min(init_phimin_pe, phimin_pe_sub)



        return [
            cmax_elyte_sub,
            cmin_elyte_sub,
            cmax_ne_sub,
            cmin_ne_sub,
            cmax_pe_sub,
            cmin_pe_sub,
            phimax_elyte_sub,
            phimin_elyte_sub,
            phimax_ne_sub,
            phimin_ne_sub,
            phimax_pe_sub,
            phimin_pe_sub,
            cmin_elyte,
            cmax_elyte,
            cmin_ne,
            cmax_ne,
            cmin_pe,
            cmax_pe,
            phimax_elyte,
            phimin_elyte,
            phimax_ne,
            phimin_ne,
            phimax_pe,
            phimin_pe
        ]

    def create_subplot(_self,x_data, y_data, title, x_label, y_label, x_min=None, y_min_sub=None, y_max_sub=None,x_max=None, y_min=None, y_max=None, vertical_line=None):

        # Create a DataFrame from the data
        # df = pd.DataFrame({
        #     "x": [x for sublist in x_data for x in sublist],
        #     "y": [y for sublist in y_data for y in sublist],
        #     "label": [label for label in _self.selected_data_sets for _ in range(len(x_data))]
        # })
        fig = go.Figure()

        if isinstance(_self.selected_data_sets, list) and len(_self.selected_data_sets) > 1:

            for i,x in enumerate(x_data):
                trace_label = _self.selected_data_sets[i].rsplit('.', 1)[0]
                fig.add_trace(go.Scatter(x=x, y=y_data[i], mode='lines', line=dict(width=5), name = trace_label))
                # fig = px.line(x=x_data, y=y_data[i])

        else:
            fig.add_trace(go.Scatter(x=x_data, y=y_data, mode='lines', line=dict(width=5)))
            

        fig.update_traces(line=dict(width=5))

        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title = y_label
            # xaxis = dict(range =[0, x_max]),
            # yaxis=dict(range=[0, y_max])
        )
        fig.update_xaxes(
            range=[0,x_max],  # sets the range of xaxis
            constrain="domain",  # meanwhile compresses the xaxis by decreasing its "domain"
        )
        if vertical_line:
             fig.add_vline(x=vertical_line, line_width=3, line_dash="dash", line_color = "grey")
             #ax.axvline(x=vertical_line, color='k', linestyle="dashed")

        # fig, ax = plt.subplots()


        # ax.plot(x_data, y_data)

        # ax.set_title(title)
        # ax.set_xlabel(x_label)
        # ax.get_yaxis().get_major_formatter().set_useOffset(False)

        # if x_max:
        #     ax.set_xlim(x_min, x_max)
        # if y_max and y_min != y_max:
        #     ax.set_ylim(y_min, y_max)
        # if y_max and y_min_sub and abs(y_min_sub- y_max_sub) <= 0.001:
        #     delta = y_min_sub/10
        #     ax.set_ylim(y_min - delta, y_max + delta)

        # if vertical_line:
        #     ax.axvline(x=vertical_line, color='k', linestyle="dashed")

        return fig


class SetMaterialDescription():
    """
    Used to render the 'Available materials' section on the Materials and models page
    """
    def __init__(self):


        self.set_material_description()

    def set_material_description(self):

        ##############################
        # Remember user changed values
        for k, v in st.session_state.items():
            st.session_state[k] = v
        ##############################

        materials = db_helper.get_all_default_material()

        st.title("The available materials")

        display_names = []
        for material_values in materials:

            material = material_values
            id,name,_,_,_,reference_name,reference,reference_link,_,display_name,number_of_components,component_name_1,component_name_2,_,context_type,_,_,context_type_iri,_ = material
            display_names.append(display_name)


        select = st.multiselect(label = "Materials",options = display_names, label_visibility="collapsed")

        for material_values in materials:

            material = material_values
            id,name,_,_,_,reference_name,reference,reference_link,_,display_name,number_of_components,component_name_1,component_name_2,_,context_type,_,_,context_type_iri,_ = material

            for choice in select:
                if choice == display_name:

                    with st.expander("{} information".format(display_name)):
                        context_type_encoded = context_type.replace(":", "&colon;")
                        st.markdown("**Context**:")
                        st.write("[{}]({})".format(context_type_encoded + " ", context_type_iri))
                        if reference_link:
                            st.markdown("**Reference**:")
                            st.write("[{}]({})".format(reference, reference_link))
                        st.markdown("**Parameter values**:")

                        parameter_set_id = db_helper.get_parameter_set_id_by_name(name)

                        parameter_values = tuple(db_helper.extract_parameters_by_parameter_set_id(parameter_set_id))

                        for parameter in parameter_values:

                            id,parameter_name,_,template_parameter_id,value = parameter

                            template_parameter = db_helper.get_template_from_name(parameter_name)

                            template_parameter_id, template_parameter_name,_,_,_,_,template_context_type, template_context_type_iri,_,unit,unit_name,unit_iri,_,_,_,_,parameter_display_name = template_parameter

                            if template_parameter_name == "open_circuit_potential" or template_parameter_name == "conductivity" or template_parameter_name == "diffusion_coefficient":

                                json_formatted_string = value.replace("'", '"')
                                value_dict = json.loads(json_formatted_string)
                                st.write("[{}]({}) = ".format(parameter_display_name, template_context_type_iri))

                                if "function" in value_dict:

                                    st.markdown('''```<Julia>
                                                {}'''.format(value_dict["function"]))
                                    string_py = value_dict["function"].replace("^", "**")



                                    fun = st.toggle(
                                        label = "Visualize function",
                                        key = "toggle_{}_{}".format(parameter_name, name)
                                        )
                                    if fun:
                                        if len(string_py) == 0:
                                            st.write("This material doesn't include the function yet.")
                                        else:
                                            st.latex(sp.latex(sp.sympify(string_py)))

                                else:
                                    st.markdown('''```<Julia>
                                                {}'''.format(value_dict["functionname"]))

                            else:

                                st.write("[{}]({}) = ".format(parameter_display_name, template_context_type_iri)+
                                            value + " / " + "[{}]({})".format(unit, unit_iri))





