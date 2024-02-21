
from PIL import Image
import pprint
import json
import pickle
import io
import h5py
import streamlit as st
from copy import deepcopy
from uuid import uuid4
import sys
import requests
import pdb
from jsonschema import validate, ValidationError
from streamlit_extras.switch_page_button import switch_page
import sympy as sp
import matplotlib.pyplot as plt
import os
import plotly.express as px
import plotly.graph_objects as go
import streamlit_elements as el


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app_scripts.app_parameter_model import *
from database import db_helper
from app_scripts import app_access, match_json_LD
from app_scripts import app_calculations as calc




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

        _,col1,_ = st.columns([2.95,2,2.5])
        st_space(space_width=6)
        _,col2,_ = st.columns([3.15,2,2.5])
        st_space(space_width=6)
        _,col3,col4 = st.columns([2.45,2,2.5])
        st_space(space_width=6)

        simulation_page = col1.button(label = "Simulation",
                        help = self.help_simulation
                        )
        
        results_page = col2.button(label = "Results",
                        help = self.help_results
                        )
        
        materials_and_models_page = col3.button(label = "Materials and models",
                        help = self.help_materials_and_models
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
        self.documentation = "[![Repo](https://badgen.net/badge/Doc/BattMo-app)](https://battmoteam.github.io/battmo-doc-test/gui.html)"

        self.set_external_links()

    def set_external_links(self):
        
        st.divider()
        website_col, doi_col, github_col, doc_col = st.columns([3.5, 5, 3,3])
        website_col.markdown(self.batterymodel)
        doi_col.markdown(self.zenodo)
        github_col.markdown(self.github)
        doc_col.markdown(self.documentation)
        st.divider()



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


# class GetTabData:
#     def __init__(self):

#         self.basis_tabs = db_helper.all_basis_tab_display_names
#         self.advanced_tabs = db_helper.all_advanced_tab_display_names

#     def get_sql_data(self,model_id):

#         print("nothing")

#         # Get data relevent to chosen model



def checkbox_input_connect(checkbox_key, tab, category_id, parameter_name,non_material_parameter):
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
        self.validate_volume_fraction = calc.validate_volume_fraction
        self.calc_density_mix = calc.calc_density_mix
        self.calc_mass_loading = calc.calc_mass_loading
        self.calc_thickness = calc.calc_thickness
        self.calc_porosity = calc.calc_porosity
        self.calc_n_to_p_ratio = calc.calc_n_to_p_ratio
        self.calc_cell_mass = calc.calc_cell_mass
        self.calc_cell_energy = calc.calc_cell_energy
        self.calc_specific_capacity_electrode = calc.calc_specific_capacity_electrode

        # Ontology definitions
        
        self.hasActiveMaterial = "hasActiveMaterial"
        self.hasBinder = "hasBinder"
        self.hasConductiveAdditive = "hasConductiveAdditive"
        self.hasElectrode = "hasElectrode"
        self.hasElectrolyte = "hasElectrolyte"
        self.hasSeparator = "hasSeparator"
        self.hasBoundaryConditions = "hasBoundaryConditions"
        self.hasCyclingProcess = "hasCyclingProcess"

        self.hasQuantitativeProperty = "hasQuantitativeProperty"
        self.hasObjectiveProperty = "hasObjectiveProperty"
        self.hasNumericalData = "hasNumericalData"
        self.hasStringData = "hasStringData"
        self.hasModel = "hasModel"
        self.hasCell = "hasCell"

        self.universe_label = "MySimulationSetup"
        self.model_label = "{} model".format(np.squeeze(db_helper.get_model_name_from_id(model_id)))
        self.model_type = "battery:{}Model".format(np.squeeze(db_helper.get_model_name_from_id(model_id)))
        self.cell_label = "MyCell"
        self.cell_type = "battery:Cell"
        
        # user_input is the dict containing all the json LD data
        self.user_input = {
            "@context": context,
        
            self.universe_label:{
                self.hasModel:{
                    "label": self.model_label,
                    "@type": self.model_type,
                    self.hasQuantitativeProperty: db_helper.get_model_parameters_as_dict(model_id)
                }
            }             
        }

        # Create fill input
        #self.set_file_input()

        # Fill tabs
        self.set_tabs()


    def set_file_input(self):

        ############################################################
        # Function that create a file input at the Simulation page
        # NOT USED YET
        ############################################################
        upload, update = st.columns((3,1))
        uploaded_file = upload.file_uploader(self.info, type='json', help= self.help)
        
        if uploaded_file:
            st.success("Your file is succesfully uploaded. Click on the 'PUSH' button to automatically fill in the parameter inputs specified in your file.")

        update.text(" ")
        update.text(" ")

        push = update.button("PUSH")
        if push:
            if uploaded_file is not None:
                uploaded_file = uploaded_file.read()
                uploaded_file_dict = json.loads(uploaded_file)
                uploaded_file_str = str(uploaded_file_dict)

                with open("uploaded_input.json", "w") as outfile:
                    outfile.write(uploaded_file_str)

                st.success("The input values are succesfully adapted to your input file. You can still change some settings below if wanted.")  
                
            else:
                st.error("ERROR: No file has been uploaded yet.")

    def set_title(self):
        st.markdown("### " + self.title)

    def create_component_parameters_dict(self,component_parameters):
        return {self.hasQuantitativeProperty: component_parameters}  
    
    def set_check_col(self,toggle_states, check_col, i, ac,category_id,non_material_parameter):
        # Create a dictionary to store toggle states
        

        st.title("Toggle System")

        for name, state in toggle_states.items():
            toggle_states[name] = check_col.checkbox(label =name, 
                                                   value =state,
                                                   key = "toggle_{}_{}".format(category_id, non_material_parameter.id),
                                                   label_visibility="collapsed")

        # Count the number of active toggles
        active_count = sum(toggle_states.values())

        # If more than 2 toggles are active, deactivate the extra ones
        if active_count > 2:
            for name in toggle_states:
                if toggle_states[name] and active_count > 2:
                    toggle_states[name] = False
                    active_count -= 1

        for name, state in toggle_states.items():
            st.write(f"{name}: {state}")

        # Display the count of active toggles
        st.write(f"Active Count: {active_count}")
        
        
        return toggle_states#, disabled


    def schema_to_form(self,p,schema):
        with st.form("active_material_form"):
            
            form_data = {}  # Store user input data
            header = st.container()
            col1, col2, col3 = st.columns(3)
            
            for property_name, property_details in schema["properties"].items():
                if "type" in property_details:
                    property_type = property_details["type"]
                else:
                    property_type = None
                
                if "$ref" in property_details:
                    ref = property_details["$ref"]
                else:
                    ref = None
                
                if property_type == "string":
                    with header:
                        form_data[property_name] = st.text_input(property_name, "")
                elif property_type == "number":
                    with header:
                        form_data[property_name] = st.number_input(property_name, 0.0)
                elif ref == "#/definitions/quantity":
                    with col1:
                        st.text_input('quantity', property_name, disabled=True)
                    with col2:
                        value = st.number_input('value', key=f"{property_name} - Value", value=0.0)
                    with col3:
                        unit = st.text_input('unit', "", key=f"{property_name} - Unit")
            
                    # Store value and unit in form_data
                    form_data[property_name] = {"value": value, "unit": unit}            
            
            # Every form must have a submit button.
            submitted = st.form_submit_button("Submit")
            if submitted:
                try:
                    validate(form_data, schema)  # Validate form data against the schema
                    st.success("Form data is valid!")
                except ValidationError as e:
                    st.error(f"Validation error: {e.message}")
                
            return form_data

    def set_pe_advanced_tabs(self, tab,category_display_name, category_parameters):
        
        advanced_pe_input= tab.expander("Show '{}' advanced parameters".format(category_display_name))
        all_advanced_tabs = advanced_pe_input.tabs(db_helper.get_pe_advanced_tab_display_names(self.model_id))
        db_tab_ids_advanced = db_helper.get_pe_advanced_db_tab_id(self.model_id)
        index_advanced = 0
        for tab_advanced in all_advanced_tabs:
            #tab_index_advanced = db_helper.get_tab_index_from_st_tab(tab_advanced)
            db_tab_id_advanced = db_tab_ids_advanced[index_advanced][0]
            

            tab_context_type, tab_context_type_iri = db_helper.get_context_type_and_iri_by_id(db_tab_id_advanced)
            tab_parameters = {
                "label": db_helper.get_advanced_tabs_display_names(self.model_id)[index_advanced],
                "@type": tab_context_type_iri
            }
                # get tab's categories
            categories_advanced = db_helper.get_advanced_categories_from_tab_id(db_tab_id_advanced)


            if len(categories_advanced) > 1:  # create one sub tab per category

                all_category_display_names = [a[8] for a in categories_advanced]
                all_sub_tabs = tab_advanced.tabs(all_category_display_names)
                i = 0

                for category in categories_advanced:
                    component_parameters = []
                    category_id, category_name,_,_,_, category_context_type, category_context_type_iri, emmo_relation, category_display_name, _, default_template_id, _ = category

                    
                    tab_advanced_pe = all_sub_tabs[i]

                    
                    i += 1


                    non_material_component = tuple(db_helper.get_advanced_components_from_category_id(category_id))     

                    non_material_component_id, non_material_component_name, _,_,_,_,_,non_material_comp_display_name,_,_,_,non_material_comp_default_template_id,non_material_comp_context_type,non_material_comp_context_type_iri,_ = non_material_component

                    raw_template_parameters = db_helper.get_advanced_template_by_template_id(default_template_id)


                    if raw_template_parameters:
                        non_material_parameters_sets = np.squeeze(db_helper.get_non_material_set_id_by_component_id(non_material_component_id))
                        non_material_parameter_set_id, non_material_parameters_set_name, _ ,_,_ = non_material_parameters_sets
                        
                        non_material_parameters_raw = []
                        for non_material_parameter_raw_template in raw_template_parameters:

                            non_material_parameter_id,name,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_ = non_material_parameter_raw_template

                        
                            non_material_parameter = db_helper.get_advanced_parameters_by_parameter_set_id(non_material_parameter_id, non_material_parameter_set_id)

                            non_material_parameters_raw.append(non_material_parameter)
                        
                        non_material_parameters_raw = tuple(np.squeeze(non_material_parameters_raw))

                        formatted_parameters = self.formatter.format_parameters(non_material_parameters_raw, raw_template_parameters, non_material_parameters_set_name)

                        
                        for parameter_id in formatted_parameters:

                            parameter = formatted_parameters.get(str(parameter_id))
                            if parameter.is_shown_to_user:
                                selected_parameter_id = db_helper.get_parameter_id_from_template_parameter_and_parameter_set(
                                    template_parameter_id=parameter.id,
                                    parameter_set_id=non_material_parameter_set_id
                                )
                                st_space(tab_advanced_pe)
                                name_col, input_col = tab_advanced_pe.columns(2)

                                if isinstance(parameter, NumericalParameter):
                                    name_col.write("[{}]({})".format(parameter.display_name, parameter.context_type_iri) + " (" + "[{}]({})".format(parameter.unit, parameter.unit_iri) + ")")
                                    
                                    user_input = input_col.number_input(
                                        label=parameter.name,
                                        value=parameter.options.get(str(selected_parameter_id)).value,
                                        min_value=parameter.min_value,
                                        max_value=parameter.max_value,
                                        key="input_{}_{}".format(non_material_component_id, selected_parameter_id),
                                        format=parameter.format,
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

                            formatted_value_dict = parameter.selected_value

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

                            parameter_details = {
                                "label": parameter.name,
                                "@type": parameter.context_type_iri if parameter.context_type_iri else "None",
                                "value": formatted_value_dict
                            }
                            if isinstance(parameter, NumericalParameter):
                                parameter_details["unit"] = {
                                    "label": parameter.unit_name if parameter.unit_name else parameter.unit,
                                    "symbol": parameter.unit,
                                    "@type": "emmo:"+parameter.unit_name if parameter.unit_name else parameter.unit
                                }
                            component_parameters.append(parameter_details)

                        if non_material_component_name == "positive_electrode_active_material_advanced":
                            material_comp_relation = self.hasActiveMaterial
                        elif non_material_component_name == "positive_electrode_binder_advanced":
                            material_comp_relation = self.hasBinder
                        elif non_material_component_name == "positive_electrode_additive_advanced":
                            material_comp_relation = self.hasConductiveAdditive
                        elif non_material_component_name == "positive_electrode_properties_advanced":
                            material_comp_relation = self.hasObjectiveProperty

                        category_parameters[material_comp_relation][self.hasQuantitativeProperty] += component_parameters

    
    
        return category_parameters

    def set_ne_advanced_tabs(self, tab, category_display_name,category_parameters):
        
        advanced_ne_input=tab.expander("Show '{}' advanced parameters".format(category_display_name))
        all_advanced_tabs = advanced_ne_input.tabs(db_helper.get_ne_advanced_tab_display_names(self.model_id))
        db_tab_ids_advanced = db_helper.get_ne_advanced_db_tab_id(self.model_id)
        index_advanced = 0
        for tab_advanced in all_advanced_tabs:
            
            db_tab_id_advanced = db_tab_ids_advanced[index_advanced][0]

            tab_context_type, tab_context_type_iri = db_helper.get_context_type_and_iri_by_id(db_tab_id_advanced)
            tab_parameters = {
                "label": db_helper.get_advanced_tabs_display_names(self.model_id)[index_advanced],
                "@type": tab_context_type_iri
            }
            # get tab's categories
            categories_advanced = db_helper.get_advanced_categories_from_tab_id(db_tab_id_advanced)
            

            if len(categories_advanced) > 1:  # create one sub tab per category

                all_category_display_names = [a[8] for a in categories_advanced]
                all_sub_tabs = tab_advanced.tabs(all_category_display_names)
                i = 0

                for category in categories_advanced:
                    component_parameters = []
                    category_id, category_name,_,_,_, category_context_type, category_context_type_iri, emmo_relation, category_display_name, _, default_template_id, _ = category

                    
                    tab_advanced = all_sub_tabs[i]

                    
                    i += 1

                    
                    non_material_component = tuple(db_helper.get_advanced_components_from_category_id(category_id))     
                    

                    non_material_component_id, non_material_component_name, _,_,_,_,_,non_material_comp_display_name,_,_,_,non_material_comp_default_template_id,non_material_comp_context_type,non_material_comp_context_type_iri,_ = non_material_component
                        
                    raw_template_parameters = db_helper.get_advanced_template_by_template_id(default_template_id)
                    

                    if raw_template_parameters:
                        
                        non_material_parameters_sets = np.squeeze(db_helper.get_non_material_set_id_by_component_id(non_material_component_id))
                        non_material_parameter_set_id, non_material_parameters_set_name, _ ,_,_ = non_material_parameters_sets
                        
                        non_material_parameters_raw = []
                        for non_material_parameter_raw_template in raw_template_parameters:

                            non_material_parameter_id,name,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_ = non_material_parameter_raw_template
                          
                        
                            non_material_parameter = db_helper.get_advanced_parameters_by_parameter_set_id(non_material_parameter_id, non_material_parameter_set_id)
                           
                            non_material_parameters_raw.append(non_material_parameter)
                            

                        
                        non_material_parameters_raw = tuple(np.squeeze(non_material_parameters_raw))

                        formatted_parameters = self.formatter.format_parameters(non_material_parameters_raw, raw_template_parameters, non_material_parameters_set_name)
                        
                        
                        for parameter_id in formatted_parameters:
                            
                            parameter = formatted_parameters.get(str(parameter_id))
                            if parameter.is_shown_to_user:
                                selected_parameter_id = db_helper.get_parameter_id_from_template_parameter_and_parameter_set(
                                    template_parameter_id=parameter.id,
                                    parameter_set_id=non_material_parameter_set_id
                                )
                                st_space(tab_advanced)
                                name_col, input_col = tab_advanced.columns(2)

                                if isinstance(parameter, NumericalParameter):
                                    name_col.write("[{}]({})".format(parameter.display_name, parameter.context_type_iri) + " (" + "[{}]({})".format(parameter.unit, parameter.unit_iri) + ")")
                                    
                                    user_input = input_col.number_input(
                                        label=parameter.name,
                                        value=parameter.options.get(str(selected_parameter_id)).value,
                                        min_value=parameter.min_value,
                                        max_value=parameter.max_value,
                                        key="input_{}_{}".format(non_material_component_id, parameter_id),
                                        format=parameter.format,
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

                            formatted_value_dict = parameter.selected_value

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

                            parameter_details = {
                                "label": parameter.name,
                                "@type": parameter.context_type_iri if parameter.context_type_iri else "None",
                                "value": formatted_value_dict
                            }
                            if isinstance(parameter, NumericalParameter):
                                parameter_details["unit"] = {
                                        "label": parameter.unit_name if parameter.unit_name else parameter.unit,
                                        "symbol": parameter.unit,
                                        "@type": "emmo:"+parameter.unit_name if parameter.unit_name else parameter.unit,
                                        #"@type_iri": n_to_p_parameter.unit_iri if n_to_p_parameter.unit_iri else None
                                    }
                            component_parameters.append(parameter_details)

                    if non_material_component_name == "negative_electrode_active_material_advanced":
                        material_comp_relation = self.hasActiveMaterial
                    elif non_material_component_name == "negative_electrode_binder_advanced":
                        material_comp_relation = self.hasBinder
                    elif non_material_component_name == "negative_electrode_additive_advanced":
                        material_comp_relation = self.hasConductiveAdditive
                    elif non_material_component_name == "negative_electrode_properties_advanced":
                        material_comp_relation = self.hasObjectiveProperty

                    category_parameters[material_comp_relation][self.hasQuantitativeProperty] += component_parameters
                
                return category_parameters
                    
    def set_tabs(self):

        cell_parameters = {
                    "label": self.cell_label,
                    "@type": self.cell_type,
                    #"@type_iri": "http://emmo.info/battery#battery_68ed592a_7924_45d0_a108_94d6275d57f0",

                }

        all_tabs = st.tabs(db_helper.get_basis_tabs_display_names(self.model_id))

        db_tab_ids = db_helper.get_db_tab_id(self.model_id)
        index = 0
        for tab in all_tabs:

            db_tab_id = db_tab_ids[index][0]

            tab_context_type, tab_context_type_iri = db_helper.get_context_type_and_iri_by_id(db_tab_id)
            tab_name = np.squeeze(db_helper.get_tab_name_by_id(db_tab_id))
            
            tab_parameters = {
                "label": db_helper.get_basis_tabs_display_names(self.model_id)[index],
                "@type": tab_context_type,
                #"@type_iri": tab_context_type_iri

            }

            if tab_name == "electrodes":
                tab_relation = self.hasElectrode
            elif tab_name == "electrolyte":
                tab_relation = self.hasElectrolyte
            elif tab_name == "separator":
                tab_relation = self.hasSeparator
            elif tab_name == "boundary_conditions":
                tab_relation = self.hasBoundaryConditions
            elif tab_name == "protocol":
                tab_relation = self.hasCyclingProcess

        

            # logo and title
            self.set_logo_and_title(tab, index)
            

            # get tab's categories
            categories = db_helper.get_basis_categories_from_tab_id(db_tab_id)

            if len(categories) > 1:  # create one sub tab per category

                all_category_display_names = [a[8] for a in categories]
                all_sub_tabs = tab.tabs(all_category_display_names)
                i = 0
                mass_loadings = {}

                for category in categories:
                    category_id, category_name,_,_,_, category_context_type, category_context_type_iri, emmo_relation, category_display_name, _, default_template_id, _ = category
 
                for category in categories:

                    category_parameters = {
                        "label": db_helper.get_basis_categories_display_names(db_tab_id)[i][0],
                        "@type": db_helper.get_categories_context_type(db_tab_id)[i][0],
                        #"@type_iri": db_helper.get_categories_context_type_iri(db_tab_id)[i][0]

                    }

                    
                    category_id, category_name,_,_,_, category_context_type, category_context_type_iri, emmo_relation, category_display_name, _, default_template_id, _ = category

                    if category_name == "negative_electrode":
                        category_relation = "hasNegativeElectrode"
                    elif category_name == "positive_electrode":
                        category_relation = "hasPositiveElectrode"

                    category_parameters, emmo_relation, mass_loadings = self.fill_category(
                        category_id=category_id,
                        category_display_name=category_display_name,
                        category_name=category_name,
                        emmo_relation=emmo_relation,
                        default_template_id=default_template_id,
                        tab=all_sub_tabs[i],
                        category_parameters = category_parameters,
                        mass_loadings = mass_loadings
                    )
                    i += 1
                    
                    tab_parameters[category_relation] = category_parameters 
                    cell_parameters[tab_relation] = tab_parameters   

                # with tab:
                    
                #     st.divider()


                #     category_parameters, emmo_relation = self.fill_electrode_tab_comp( db_tab_id ,mass_loadings,category_id,emmo_relation = None)


                    
                #     tab_display_name = db_helper.get_tabs_display_name_from_id(db_tab_id)
                    

                #     cell_parameters[tab_relation][self.hasObjectiveProperty] = category_parameters
         

            else:  # no sub tab is needed

                category_parameters = {}
                
                category_id, category_name,_,_,_, category_context_type, category_context_type_iri, emmo_relation, category_display_name, _, default_template_id, _= categories[0]
                
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

                    protocol_parameters = category_parameters

                    self.user_input[self.universe_label][tab_relation] = protocol_parameters[tab_relation]

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
                
            
            
            

            # cell is fully defined, its parameters are saved in the user_input dict
            self.user_input[self.universe_label][self.hasCell] = cell_parameters

            index +=1

        self.user_input = self.calc_indicators(self.user_input)

        self.update_json_LD()
        st.divider()

        # if os.path.exists("uploaded_input.json"):
        #     os.remove("uploaded_input.json")


    def update_json_LD(self):

        path_to_battmo_input = app_access.get_path_to_linked_data_input()

        # save formatted parameters in json file
        with open(path_to_battmo_input, "w") as new_file:
            json.dump(
                self.user_input,
                new_file,
                indent=3)

    def calc_indicators(self,user_input):

        with open(app_access.get_path_to_calculated_values(),'r') as f:
            mass_loadings = json.load(f)["calculatedParameters"]["mass_loadings"]
        
        n_to_p_ratio = self.calc_n_to_p_ratio(mass_loadings)

        n_to_p_category_parameters, emmo = self.setup_n_to_p_ratio(n_to_p_ratio)



        user_input[self.universe_label][self.hasCell][self.hasBoundaryConditions][self.hasQuantitativeProperty] += n_to_p_category_parameters[self.hasQuantitativeProperty]

        return user_input
    
    def setup_n_to_p_ratio(self, n_to_p_ratio_value):

        category_parameters = []
         
        n_to_p_ratio_raw_template = db_helper.get_template_parameter_by_parameter_name("n_to_p_ratio")

        parameter_id, \
                    name, \
                    model_name, \
                    par_class, \
                    difficulty, \
                    model_id, \
                    template_id, \
                    context_type, \
                    n_to_p_context_type_iri, \
                    parameter_type, \
                    n_to_p_unit, \
                    unit_name, \
                    n_to_p_unit_iri, \
                    max_value, \
                    min_value, \
                    is_shown_to_user, \
                    description,  \
                    n_to_p_display_name = tuple(np.squeeze(n_to_p_ratio_raw_template[0]))
        
        # st.text(" ")
        # st.write("[{}]({})".format(n_to_p_display_name, n_to_p_context_type_iri)+ " (" + "[{}]({})".format(n_to_p_unit, n_to_p_unit_iri) + ")")


        formatted_value_dict = n_to_p_ratio_value

    
        formatted_value_dict = {
            "@type": "emmo:Numerical",
            self.hasNumericalData: n_to_p_ratio_value
        }

        parameter_details = {
            "label": name,
            "@type": context_type,
            #"@type_iri": n_to_p_parameter.context_type_iri if n_to_p_parameter.context_type_iri else "None",
            "value": formatted_value_dict
        }
        
        parameter_details["unit"] = {
            "label": unit_name,
            "symbol": n_to_p_unit,
            "@type": "emmo:"+unit_name
            #"@type_iri": n_to_p_parameter.unit_iri if n_to_p_parameter.unit_iri else None
        }

        category_parameters.append(parameter_details)

        return {self.hasQuantitativeProperty: category_parameters}, n_to_p_context_type_iri
        

    def set_logo_and_title(self, tab, tab_index):
        if tab_index == 0:
            image_collumn,image_collumn_2, title_column = tab.columns([0.9,0.9,6])
            image_collumn.image(self.image_dict[str(tab_index)])
            image_collumn_2.image(self.image_dict[str(tab_index+1)])
        else:

            image_column, title_column = tab.columns([1, 5])
            image_column.image(self.image_dict[str(tab_index+1)])

        title_column.text(" ")
        title_column.subheader(db_helper.get_basis_tabs_display_names(self.model_id)[tab_index])


    def fill_vf_column(self, vf_col,category_id,material_comp_default_template_id,material_component_id,component_parameters,vf_sum,tab,emmo_relation=None):

        
        
        volume_fraction_raw_template = db_helper.get_vf_template_by_template_id(material_comp_default_template_id)
        
        vf_parameter_set_id, vf_parameters_set_name = db_helper.get_vf_parameter_set_id_by_component_id(material_component_id)
        vf_parameter_set_id = int(vf_parameter_set_id)
        vf_parameters_set_name = str(vf_parameters_set_name)

        volume_fraction_raw = tuple(np.squeeze(db_helper.get_vf_raw_parameter_by_parameter_set_id(vf_parameter_set_id)))

        
        formatted_vf_parameters = self.formatter.format_parameters(volume_fraction_raw, volume_fraction_raw_template,vf_parameters_set_name )


        for parameter_id in formatted_vf_parameters:
            vf_parameter = formatted_vf_parameters.get(parameter_id)
            if vf_parameter.is_shown_to_user:
                selected_parameter_id = db_helper.get_parameter_id_from_template_parameter_and_parameter_set(
                    template_parameter_id=vf_parameter.id,
                    parameter_set_id=vf_parameter_set_id
        )

            user_input = vf_col.number_input(
                label=vf_parameter.name,
                value=vf_parameter.default_value,
                min_value=vf_parameter.min_value,
                max_value=vf_parameter.max_value,
                key="input_{}_{}".format(category_id, vf_parameter.id),
                format=vf_parameter.format,
                step=vf_parameter.increment,
                label_visibility="collapsed"
                )
            
            if vf_parameter:
                vf_parameter.set_selected_value(user_input)
                formatted_value_dict = vf_parameter.selected_value
                if isinstance(vf_parameter, NumericalParameter):
                    formatted_value_dict = {
                        "@type": "emmo:Numerical",
                        self.hasNumericalData: vf_parameter.selected_value
                    }

                elif isinstance(vf_parameter, StrParameter):
                    formatted_value_dict = {
                        "@type": "emmo:String",
                        self.hasStringData: vf_parameter.selected_value
                    }

                elif isinstance(vf_parameter, BooleanParameter):
                    formatted_value_dict = {
                        "@type": "emmo:Boolean",
                        self.hasStringData: vf_parameter.selected_value
                    }

                elif isinstance(vf_parameter, FunctionParameter):
                    formatted_value_dict = {
                        "@type": "emmo:Function",
                        self.hasStringData: vf_parameter.selected_value
                    }

                parameter_details = {
                    "label": vf_parameter.name,
                    "@type": vf_parameter.context_type if vf_parameter.context_type else "None",
                    #"@type_iri": vf_parameter.context_type_iri if vf_parameter.context_type_iri else "None",
                    "value": formatted_value_dict
                }
                if isinstance(vf_parameter, NumericalParameter):
                    parameter_details["unit"] = {
                        "label": vf_parameter.unit_name if vf_parameter.unit_name else vf_parameter.unit,
                        "symbol": vf_parameter.unit,
                        "@type": "emmo:"+vf_parameter.unit_name if vf_parameter.unit_name else vf_parameter.unit,
                        #"@type_iri": vf_parameter.unit_iri if vf_parameter.unit_iri else None
                    }
                    
                component_parameters.append(parameter_details)
                vf_sum[material_component_id] = vf_parameter.selected_value 
        
        return vf_parameter, user_input, component_parameters, emmo_relation, vf_sum
            
    def fill_material_column(self,component_name,material_comp_default_template_id,material_component_id,material_col,material_comp_display_name,material_comp_context_type_iri,material_component,category_parameters, density, emmo_relation = None):
        
        component_parameters = []
        material_parameter_sets = []
        # get corresponding template parameters from db
        material_raw_template_parameters = db_helper.get_all_material_by_template_id(material_comp_default_template_id)

        materials = tuple(db_helper.get_material_from_component_id(material_component_id))
        

        for material in materials:

            material_id,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_ = material
            # get parameter sets corresponding to component, then parameters from each set
            material_parameter_sets.append(tuple(db_helper.get_material_by_material_id(material_id)[0]))

        material_parameter_sets_name_by_id = {}
        for id, name, _,_,_ in material_parameter_sets:
            material_parameter_sets_name_by_id[id] = name

        material_raw_parameters = []
        for material_parameter_set_id in material_parameter_sets_name_by_id:
            material_raw_parameters += db_helper.extract_parameters_by_parameter_set_id(material_parameter_set_id)
        material_raw_parameters = tuple(material_raw_parameters)        
        # format all those parameters: use template parameters for metadata, and parameters for values.
        # all information is packed in a single python object
        # formatted_parameters is a dict containing those python objects

        material_formatted_parameters, formatted_component, formatted_components = self.formatter.format_parameter_sets(material_component,materials,material_parameter_sets,material_parameter_sets_name_by_id, material_raw_template_parameters, material_raw_parameters,material_component_id)
        
        selected_value_id = material_col.selectbox(
            label="[{}]({})".format(formatted_component.name, formatted_component.context_type_iri),
            options=formatted_component.options,
            key="select_{}".format(material_component_id),
            label_visibility="collapsed",
            format_func=lambda x: formatted_component.options.get(x).display_name,
            # on_change=reset_func,
            # args=(material_component_id, material_parameter_set_id, formatted_component)
        )

       

        
       
        if formatted_component:
            material_choice = formatted_component.options.get(selected_value_id)

            material_parameter_set_id = material_choice.parameter_set_id

            parameter_ids = material_choice.parameter_ids
            parameters = material_choice.parameters

            
            for parameter_id in parameters:

                parameter = parameters.get(parameter_id)

                set_parameter = parameter.options.get(material_parameter_set_id)

                formatted_value_dict = set_parameter.value
                if isinstance(parameter, NumericalParameter):
                    formatted_value_dict = {
                        "@type": "emmo:Numerical",
                        self.hasNumericalData: set_parameter.value
                    }

                elif isinstance(parameter, StrParameter):
                    formatted_value_dict = {
                        "@type": "emmo:String",
                        self.hasStringData: set_parameter.value
                    }

                elif isinstance(parameter, BooleanParameter):
                    formatted_value_dict = {
                        "@type": "emmo:Boolean",
                        self.hasStringData: set_parameter.value
                    }

                parameter_details = {
                    "label": parameter.name,
                    "@type": parameter.context_type if parameter.context_type else "None",
                    #"@type_iri": parameter.context_type_iri if parameter.context_type_iri else "None",
                    "value": formatted_value_dict
                }
                if isinstance(parameter, NumericalParameter):
                    parameter_details["unit"] = {
                        "label": parameter.unit_name if parameter.unit_name else parameter.unit,
                        "symbol": parameter.unit,
                        "@type": "emmo:"+parameter.unit_name if parameter.unit_name else parameter.unit,
                        #"@type_iri": parameter.unit_iri if parameter.unit_iri else None
                    }

                component_parameters.append(parameter_details)
                if parameter.name == "density" and density != None:
                    density[material_component_id] = set_parameter.value
                

        return material_formatted_parameters,formatted_component, selected_value_id, component_parameters, emmo_relation, density
        

    
    def fill_non_material_component(self,category_id,category_name,non_material_comp_default_template_id,non_material_component_id,property_col,value_col,non_material_parameters_sets,model_id, component_parameters, check_col,non_material_component_name,tab, density_mix, mass_loadings):
        non_material_parameters_raw_template = db_helper.get_non_material_template_by_template_id(non_material_comp_default_template_id,model_id)
        
        
        
        non_material_parameter_sets_name_by_id = {}
        non_material_parameter_set_id, non_material_parameters_set_name, _ ,_,_ = non_material_parameters_sets

        parameter_id = []
        non_material_parameters_raw = []
        for non_material_parameter_raw_template in non_material_parameters_raw_template:

            non_material_parameter_id,name,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_ = non_material_parameter_raw_template

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
                                      on_change = checkbox_input_connect,
                                      args = (checkbox_key, tab, category_id, non_material_parameter.name,non_material_parameter),
                                      label_visibility="collapsed")
                    st.text(" ")  
                   
            property_col.write("[{}]({})".format(non_material_parameter.display_name, non_material_parameter.context_type_iri)+ " (" + "[{}]({})".format(non_material_parameter.unit, non_material_parameter.unit_iri) + ")")

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
                    format=non_material_parameter.format,
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
                formatted_value_dict = non_material_parameter.selected_value
                if isinstance(non_material_parameter, NumericalParameter):
                    formatted_value_dict = {
                        "@type": "emmo:Numerical",
                        self.hasNumericalData: non_material_parameter.selected_value
                    }

                elif isinstance(non_material_parameter, StrParameter):
                    formatted_value_dict = {
                        "@type": "emmo:String",
                        self.hasStringData: non_material_parameter.selected_value
                    }

                elif isinstance(non_material_parameter, BooleanParameter):
                    formatted_value_dict = {
                        "@type": "emmo:Boolean",
                        self.hasStringData: non_material_parameter.selected_value
                    }
                
                # elif isinstance(non_material_parameter, FunctionParameter):
                #     formatted_value_dict = {
                #         "@type": "emmo:Function",
                #         self.hasStringData: non_material_parameter.selected_value
                #     }


                parameter_details = {
                    "label": non_material_parameter.name,
                    "@type": non_material_parameter.context_type if non_material_parameter.context_type else "None",
                    #"@type_iri": non_material_parameter.context_type_iri if non_material_parameter.context_type_iri else "None",
                    "value": formatted_value_dict
                }
                if isinstance(non_material_parameter, NumericalParameter):
                    parameter_details["unit"] = {
                        "label": non_material_parameter.unit_name if non_material_parameter.unit_name else non_material_parameter.unit,
                        "symbol": non_material_parameter.unit,
                        "@type": "emmo:"+non_material_parameter.unit_name if non_material_parameter.unit_name else non_material_parameter.unit,
                        #"@type_iri": non_material_parameter.unit_iri if non_material_parameter.unit_iri else None
                    }
                    
                component_parameters.append(parameter_details)

                if non_material_parameter.name == "coating_thickness":
                    thickness = non_material_parameter.selected_value
                elif non_material_parameter.name == "coating_porosity":
                    porosity = non_material_parameter.selected_value
                elif non_material_parameter.name == "mass_loading":
                    mass_loading= non_material_parameter.selected_value
                    mass_loadings[category_name]=mass_loading
            i +=1
            ac += 1
        
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
                            json.dump(parameters_dict,f)

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
                            format=non_material_parameter.format,
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
                            format=non_material_parameter.format,
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
                            format=non_material_parameter.format,
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
                component_parameters[par_index]["value"][self.hasNumericalData]=st.session_state[input_value]
                st.experimental_rerun

        return non_material_parameter,user_input, {self.hasQuantitativeProperty: component_parameters}, mass_loadings
    
    def fill_electrode_tab_comp(self, db_tab_id,mass_loadings,category_id ,emmo_relation):

        category_parameters = []
        n_to_p_parameter_col, empty, n_to_p_value_n, empty = st.columns([3,1,1.5,7])

        n_to_p_component = db_helper.get_n_to_p_component_by_tab_id(db_tab_id)  

        n_to_p_component_id, n_to_p_component_name, _,_,_,_,_,n_to_p_comp_display_name,_,_,_,n_to_p_comp_default_template_id,n_to_p_comp_context_type,n_to_p_comp_context_type_iri,_ = n_to_p_component     
        n_to_p_ratio_raw_template = db_helper.get_n_p_template_by_template_id(n_to_p_comp_default_template_id)

        parameter_id, \
                    name, \
                    model_name, \
                    par_class, \
                    difficulty, \
                    model_id, \
                    template_id, \
                    context_type, \
                    n_to_p_context_type_iri, \
                    parameter_type, \
                    n_to_p_unit, \
                    unit_name, \
                    n_to_p_unit_iri, \
                    max_value, \
                    min_value, \
                    is_shown_to_user, \
                    description,  \
                    n_to_p_display_name = tuple(np.squeeze(n_to_p_ratio_raw_template[0]))
        
        n_to_p_parameter_col.text(" ")
        n_to_p_parameter_col.write("[{}]({})".format(n_to_p_display_name, n_to_p_context_type_iri)+ " (" + "[{}]({})".format(n_to_p_unit, n_to_p_unit_iri) + ")")

        n_to_p_parameter_set_id, n_to_p_parameter_set_name = db_helper.get_n_p_parameter_set_id_by_component_id(n_to_p_component_id)
        n_to_p_parameter_set_id=int(n_to_p_parameter_set_id)
        n_to_p_parameter_set_name= str(n_to_p_parameter_set_name)
        
        n_to_p_ratio_raw_parameter = db_helper.get_n_p_parameter_by_template_id(n_to_p_parameter_set_id)
        formatted_n_to_p_parameters = self.formatter.format_parameters(n_to_p_ratio_raw_parameter, n_to_p_ratio_raw_template,n_to_p_parameter_set_name )
        
        for parameter_id in formatted_n_to_p_parameters:
            n_to_p_parameter = formatted_n_to_p_parameters.get(parameter_id)
            input_key = "input_{}_{}".format(db_tab_id, n_to_p_parameter.id)
            if input_key not in st.session_state:
                st.session_state[input_key] = n_to_p_parameter.default_value,
        
        mass_load_n = mass_loadings["negative_electrode"]
        mass_load_p = mass_loadings["positive_electrode"]

        n_to_p = round(mass_load_n/mass_load_p,2)
        mass_load = "mass_load_"+ str(category_id)
        
        columns = [n_to_p_parameter_col]
        ind = 0
        for parameter_id in formatted_n_to_p_parameters:
            n_to_p_parameter = formatted_n_to_p_parameters.get(parameter_id)
            input_key = "input_{}_{}".format(db_tab_id, n_to_p_parameter.id)
            column = columns[ind]
            st.session_state[input_key] = n_to_p

            if n_to_p_parameter.is_shown_to_user:
                selected_parameter_id = db_helper.get_parameter_id_from_template_parameter_and_parameter_set(
                    template_parameter_id=n_to_p_parameter.id,
                    parameter_set_id=n_to_p_parameter_set_id
        )

            column.metric(
                label = "n_to_p",
                value = st.session_state[input_key],
                #key = input_key,
                label_visibility= "collapsed"
            )

            ind += 1

            n_to_p_parameter.set_selected_value(st.session_state[input_key])
            formatted_value_dict = n_to_p_parameter.selected_value

            if isinstance(n_to_p_parameter, NumericalParameter):
                formatted_value_dict = {
                    "@type": "emmo:Numerical",
                    self.hasNumericalData: n_to_p_parameter.selected_value
                }

            elif isinstance(n_to_p_parameter, StrParameter):
                formatted_value_dict = {
                    "@type": "emmo:String",
                    self.hasStringData: n_to_p_parameter.selected_value
                }

            elif isinstance(n_to_p_parameter, BooleanParameter):
                formatted_value_dict = {
                    "@type": "emmo:Boolean",
                    self.hasStringData: n_to_p_parameter.selected_value
                }

            # elif isinstance(n_to_p_parameter, FunctionParameter):
            #     formatted_value_dict = {
            #         "@type": "emmo:Function",
            #         self.hasStringData: n_to_p_parameter.selected_value
            #     }

            parameter_details = {
                "label": n_to_p_parameter.name,
                "@type": n_to_p_parameter.context_type if n_to_p_parameter.context_type else "None",
                #"@type_iri": n_to_p_parameter.context_type_iri if n_to_p_parameter.context_type_iri else "None",
                "value": formatted_value_dict
            }
            

            if isinstance(n_to_p_parameter, NumericalParameter):
                parameter_details["unit"] = {
                    "label": n_to_p_parameter.unit_name if n_to_p_parameter.unit_name else n_to_p_parameter.unit,
                    "symbol": n_to_p_parameter.unit,
                    "@type": "emmo:"+n_to_p_parameter.unit_name if n_to_p_parameter.unit_name else n_to_p_parameter.unit,
                    #"@type_iri": n_to_p_parameter.unit_iri if n_to_p_parameter.unit_iri else None
                }

            category_parameters.append(parameter_details)
        return {self.hasQuantitativeProperty: category_parameters}, emmo_relation
        

    def fill_category(self, category_id, category_display_name,category_name, emmo_relation, default_template_id, tab, category_parameters,mass_loadings,selected_am_value_id=None):

        

        # get components associated with material parameter sets
        material_components = db_helper.get_material_components_from_category_id(category_id)
        
        
        if category_name == "negative_electrode" or category_name == "positive_electrode":
            
            component_col, material_col, vf_col = tab.columns(3)
            component_col.markdown("**Component**")
            material_col.markdown("**Material**")
            material_component_id, component_name, _,_,_,_,_,material_comp_display_name,_,_,_,material_comp_default_template_id,material_comp_context_type,material_comp_context_type_iri,_ = material_components[0]
            parameter_id, \
                    name, \
                    model_name, \
                    par_class, \
                    difficulty, \
                    model_id, \
                    template_id, \
                    context_type, \
                    vf_context_type_iri, \
                    parameter_type, \
                    vf_unit, \
                    unit_name, \
                    vf_unit_iri, \
                    max_value, \
                    min_value, \
                    is_shown_to_user, \
                    description,  \
                    vf_display_name = tuple(np.squeeze(db_helper.get_vf_template_by_template_id(material_comp_default_template_id)))
            vf_col.write("[{}]({})".format(vf_display_name, vf_context_type_iri) + " (" + "[{}]({})".format(vf_unit, vf_unit_iri) + ")")

            vf_sum = {}
            density = {}
            for material_component in material_components:
                component_parameters = []
                material_component_id, component_name, _,_,_,_,_,material_comp_display_name,_,_,_,material_comp_default_template_id,material_comp_context_type,material_comp_context_type_iri,_ = material_component
                
                

                
                component_col.write("[{}]({})".format(material_comp_display_name, material_comp_context_type_iri))
                component_col.text(" ")

                material_formatted_parameters,formatted_materials, selected_value_id, component_parameter_mat, emmo_relation, density = self.fill_material_column(component_name,material_comp_default_template_id,material_component_id,material_col,material_comp_display_name,material_comp_context_type_iri,material_component,category_parameters,density)

                component_parameters.extend(component_parameter_mat)

                component_parameters = self.create_component_parameters_dict(component_parameters)

                component_parameters["label"] = material_comp_display_name
                component_parameters["@type"] = material_comp_context_type
                #component_parameters["@type_iri"] = material_comp_context_type_iri

                if component_name == "negative_electrode_active_material" or component_name == "positive_electrode_active_material":
                    material_comp_relation = self.hasActiveMaterial
                elif component_name == "negative_electrode_binder" or component_name == "positive_electrode_binder":
                    material_comp_relation = self.hasBinder
                elif component_name == "negative_electrode_additive" or component_name == "positive_electrode_additive":
                    material_comp_relation = self.hasConductiveAdditive
                category_parameters[material_comp_relation] = component_parameters


                material_choice = formatted_materials.options.get(selected_value_id).name
 
                material = formatted_materials.options.get(selected_value_id)
                parameters = material.parameters
                
                
                if material_choice == "user_defined":

                    component_parameters = []
                    ex = tab.expander("Fill in '%s' parameters" % material_comp_display_name)
                        
                    with ex:
                        for parameter_id in parameters:
                            parameter = parameters.get(parameter_id)
                            parameter_options =parameter.options.get(selected_value_id)
 

                            if not isinstance(parameter, FunctionParameter):
                                property_col, value_col= ex.columns((1.5,2))


                                property_col.write("[{}]({})".format(parameter.display_name, parameter.context_type_iri)+ " (" + "[{}]({})".format(parameter.unit, parameter.unit_iri) + ")")

                                user_input = value_col.number_input(
                                    label=parameter.name,
                                    value=parameter.min_value,
                                    min_value=parameter.min_value,
                                    max_value=parameter.max_value,
                                    key="input_{}_{}".format(category_id, parameter.id),
                                    format=parameter.format,
                                    step=parameter.increment,
                                    label_visibility="collapsed"
                                    )
                                
                            elif isinstance(parameter, FunctionParameter):

                                st.divider()
                                st.write("[{}]({})".format(parameter.display_name, parameter.context_type_iri))

                                # if component_name == "electrolyte_materials":

                                #     if parameter.name == "conductivity":
                                #         conductivity = "conductivity_{}".format(parameter_id)
                                #         if conductivity not in st.session_state:
                                #             st.session_state[conductivity] = r'''1e-4*c*((-10.5 + 0.668e-3*c + 0.494e-6*c^2) + (0.074 - 1.78e-5*c - 8.86e-10*c^2)*T + (-6.96e-5 + 2.80e-8*c)*T^2)^2'''
                                #     else:
                                #         diffusion_coefficient = "diffusion_coefficient_{}".format(parameter_id)
                                #         if diffusion_coefficient not in st.session_state:
                                #             st.session_state[diffusion_coefficient] = r'''1e-4 * 10^(-4.43 - 54/(T - 229 - 5*c*1e-3) - 0.22*c*1e-3)'''

                                #     variables = "variables_{}".format(parameter_id)

                                #     if variables not in st.session_state:
                                #         #st.session_state[du_dt] = r'''(1e-3 *( 0.005269056+ 3.299265709 * (c/cmax)- 91.79325798 * (c/cmax)^2+ 1004.911008 * (c/cmax)^3- 5812.278127 * (c/cmax)^4+ 19329.75490 * (c/cmax)^5- 37147.89470 * (c/cmax)^6+ 38379.18127 * (c/cmax)^7- 16515.05308 * (c/cmax)^8 )
                                #         #/ ( 1- 48.09287227 * (c/cmax)+ 1017.234804 * (c/cmax)^2- 10481.80419 * (c/cmax)^3+ 59431.30000 * (c/cmax)^4- 195881.6488 * (c/cmax)^5+ 374577.3152 * (c/cmax)^6- 385821.1607 * (c/cmax)^7+ 165705.8597 * (c/cmax)^8 ))'''
                                #         st.session_state[variables] = r'c,T'
                                    
                                #     #ex.latex(r'OCP = OCP_{ref}\left(\frac{c}{c_{max}}\right) + (T - refT) * \frac{dU}{dT}\left(\frac{c}{c_{max}}\right) ')
                                #     #ex.latex(r'or')
                                #     #ex.latex(r'OCP = OCP\left(\frac{c}{c_{max}}\right)')

                                #     info = ex.toggle(label="Guidelines", key = "toggle_{}".format(parameter_id))
                                #     if info:
                                #         parameters,language  = ex.columns(2)
                                #         language.markdown(r'''
                                #                 **Allowed language** 
                                #                 - Use '^' to indicate a superscript
                                #                 - Use '*' to indicate a multiplication
                                #                 - Use 'exp(a)' to indicate an exponential with power a
                                #                 - Use 'tanh()' for hyperbolic tangent
                                #                 - Use '/' for dividing
                                                
                                #                 ''')
                                        
                                #         parameters.markdown(r'''
                                #                 **Allowed variables**
                                #                 - Surface concentration : c
                                #                 - Temperature    : T
                                                
                                #                 ''')

                                #     quantity = ex.toggle(label="Create your {} own function".format(parameter.display_name), key = "toggle_quantity_{}".format(parameter_id))

                                #     if quantity:
                                #         ex.text_input(
                                #             label = "{}".format(parameter.display_name),
                                #             value = st.session_state[parameter.name],
                                #             key = parameter.name,
                                #             label_visibility= "visible"
                                #         )
                                #         quantity_str = st.session_state[parameter.name]
                                #         func_quantity = ex.toggle(label="Visualize {}".format(parameter.display_name), key = "toggle_vis_{}".format(parameter_id))

                                #         if func_ocpref:
                                #             # Convert the input string to a SymPy equation
                                #             try:
                                #                 quantity_str_py = quantity_str.replace("^", "**")
                                #                 eq_quantity = sp.sympify(quantity_str_py)
                                #                 ex.latex("{} = ".format(parameter.display_name) + sp.latex(eq_quantity))
                                                
                                #             except sp.SympifyError:
                                #                 ex.warning("Invalid equation input. Please enter a valid mathematical expression.")


                                #         ex.text_input(
                                #             label = "Variables (ex: c,T)",
                                #             value = st.session_state[variables],
                                #             key = variables,
                                #             label_visibility= "visible"
                                #         )

                                    
                                #         variables_str = st.session_state[variables]

                                        
                                #         func_du = ex.toggle(label="Visualize your variables", key = "toggle_vis_du_{}".format(parameter_id))

                                #         if func_du:
                                #             # Convert the input string to a SymPy equation
                                #             try:
                                        
                                #                 eq_variables = sp.sympify(variables_str)
                                #                 ex.latex(sp.latex(eq_variables))
                                #             except sp.SympifyError:
                                #                 ex.warning("Invalid equation input. Please enter a valid mathematical expression.")

                                #         if variables_str == "":
                                #             ex.warning("You haven't specified the variables your equation depends on.")
                                            
                                #         else:
                                #             user_input = quantity_str
                                #             argumentlist = [variables_str]

                                #     else: 
                                #         user_input = None


                                if component_name == "negative_electrode_active_material" or component_name == "positive_electrode_active_material":
                            
                            
                                    ref_ocp = "ref_ocp_{}".format(material_component_id)
                                    variables = "variables_{}".format(material_component_id)

                                    if variables not in st.session_state:
                                        
                                        st.session_state[variables] = r'c,cmax,T,refT'
                                    if ref_ocp not in st.session_state:
                                        if component_name == "negative_electrode_active_material":
                                            st.session_state[ref_ocp] = r'''0.7222+ 0.1387*(c/cmax) + 0.0290*(c/cmax)^(0.5) - 0.0172/(c/cmax) + 0.0019/(c/cmax)^(1.5)+ 0.2808 * exp(0.9 - 15.0*c/cmax) - 0.7984 * exp(0.4465*c/cmax - 0.4108) + (T - refT) *1e-3 *( 0.005269056+ 3.299265709 * (c/cmax)- 91.79325798 * (c/cmax)^2+ 1004.911008 * (c/cmax)^3- 5812.278127 * (c/cmax)^4+ 19329.75490 * (c/cmax)^5- 37147.89470 * (c/cmax)^6+ 38379.18127 * (c/cmax)^7- 16515.05308 * (c/cmax)^8 )/ ( 1- 48.09287227 * (c/cmax)+ 1017.234804 * (c/cmax)^2- 10481.80419 * (c/cmax)^3+ 59431.30000 * (c/cmax)^4- 195881.6488 * (c/cmax)^5+ 374577.3152 * (c/cmax)^6- 385821.1607 * (c/cmax)^7+ 165705.8597 * (c/cmax)^8 )'''
                                        elif component_name == "positive_electrode_active_material":
                                            st.session_state[ref_ocp] = r'''(-4.656 + 0 * (c/cmax) + 88.669 * (c/cmax)^2 + 0 * (c./cmax)^3 - 401.119 * (c/cmax)^4 + 0 * (c/cmax)^5 + 342.909 * (c/cmax)^6 + 0 * (c/cmax)^7 - 462.471 * (c/cmax)^8 + 0 * (c/cmax)^9 + 433.434 * (c/cmax)^10)/(-1 + 0  * (c/cmax)+ 18.933 * (c./cmax)^2+ 0 * (c/cmax)^3- 79.532 * (c/cmax)^4+ 0 * (c/cmax)^5+ 37.311 * (c/cmax)^6+ 0 * (c/cmax)^7- 73.083 * (c/cmax)^8+ 0 * (c/cmax)^9+ 95.960 * (c/cmax)^10)+ (T - refT) * ( -1e-3* ( 0.199521039- 0.928373822 * (c/cmax)+ 1.364550689000003 * (c/cmax)^2- 0.611544893999998 * (c/cmax)^3)/ (1- 5.661479886999997 * (c/cmax)+ 11.47636191 * (c/cmax)^2- 9.82431213599998 * (c/cmax)^3+ 3.048755063 * (c/cmax)^4))'''

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

                                    #ocp = ex.toggle(label="Create your own OCP function", key = "toggle_ocp_{}".format(material_component_id))

                                    #if ocp:
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

                                    
                                    #func_du = ex.toggle(label="Visualize your variables", key = "toggle_vis_du_{}".format(material_component_id))

                                    # if func_du:
                                    #     # Convert the input string to a SymPy equation
                                    #     try:
                                    
                                    #         eq_variables = sp.sympify(variables_str)
                                    #         ex.latex(sp.latex(eq_variables))
                                    #     except sp.SympifyError:
                                    #         ex.warning("Invalid equation input. Please enter a valid mathematical expression.")

                                    if variables_str == "":
                                        ex.warning("You haven't specified the variables your equation depends on.")
                                        
                                    else:
                                        variables_array = variables_str.split(',')
                                        user_input = {'@type': 'emmo:String', 'hasStringData': {'function': ref_ocp_str, 'argument_list':variables_array}}
                                            

                                    # else: 
                                    #     user_input = None

                            if not user_input:
                                st.warning("You still have to define the function for the {}. Enable the 'Create you own {} function' toggle.".format(parameter.display_name,parameter.display_name))


                            if parameter:
                                
                                parameter.set_selected_value(user_input)

                                formatted_value_dict = parameter.selected_value
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
                                
                                # elif isinstance(non_material_parameter, FunctionParameter):
                                #     formatted_value_dict = {
                                #         "@type": "emmo:Function",
                                #         self.hasStringData: non_material_parameter.selected_value
                                #     }

                                parameter_details = {
                                    "label": parameter.name,
                                    "@type": parameter.context_type_iri if parameter.context_type_iri else "None",
                                    "value": formatted_value_dict
                                }
                                if isinstance(parameter, NumericalParameter):
                                    parameter_details["unit"] = {
                                        "label": parameter.unit_name if parameter.unit_name else parameter.unit,
                                        "symbol": parameter.unit,
                                        "@type": "emmo:"+parameter.unit_name if parameter.unit_name else parameter.unit,
                                        #"@type_iri": n_to_p_parameter.unit_iri if n_to_p_parameter.unit_iri else None
                                    }

                                component_parameters.append(parameter_details)
                                if parameter.name == "density":
                                    density[material_component_id] = parameter.selected_value
                                    
                        component_parameters = self.create_component_parameters_dict(component_parameters)
                

                        component_parameters["label"] = material_comp_display_name
                        component_parameters["@type"] = material_comp_context_type
                        #component_parameters["@type_iri"] = material_comp_context_type_iri

                        if component_name == "negative_electrode_active_material" or component_name == "positive_electrode_active_material":
                            material_comp_relation = self.hasActiveMaterial
                        elif component_name == "negative_electrode_binder" or component_name == "positive_electrode_binder":
                            material_comp_relation = self.hasBinder
                        elif component_name == "negative_electrode_additive" or component_name == "positive_electrode_additive":
                            material_comp_relation = self.hasConductiveAdditive
                        category_parameters[material_comp_relation] = component_parameters

                
                component_parameters = []
                vf_parameter, user_input, component_parameter,_,vf_sum = self.fill_vf_column(vf_col,category_id,material_comp_default_template_id,material_component_id,component_parameters,vf_sum,tab,emmo_relation=None)

                component_parameters = self.create_component_parameters_dict(component_parameters)

                component_parameters["label"] = material_comp_display_name
                component_parameters["@type"] = material_comp_context_type
                #component_parameters["@type_iri"] = material_comp_context_type_iri

                if component_name == "negative_electrode_active_material" or component_name == "positive_electrode_active_material":
                    material_comp_relation = self.hasActiveMaterial
                elif component_name == "negative_electrode_binder" or component_name == "positive_electrode_binder":
                    material_comp_relation = self.hasBinder
                elif component_name == "negative_electrode_additive" or component_name == "positive_electrode_additive":
                    material_comp_relation = self.hasConductiveAdditive
    

                category_parameters[material_comp_relation][self.hasQuantitativeProperty] += (component_parameters[self.hasQuantitativeProperty])
                
                ########################################################
                # Not sure what to do with this 
                ########################################################
                        # # Load the JSON schema from a file
                        # schema_file_path = app_access.get_path_to_schema_dir() + "/user_defined_am.json"
                        # with open(schema_file_path, "r") as schema_file:
                        #     schema = json.load(schema_file)

                        # # Load the JSON schema from a file
                        # data_file_path = app_access.get_path_to_schema_dir() + "/user_defined_am_data.json"
                        # with open(data_file_path, "r") as data_file:
                        #     data = json.load(data_file)    
                        

                        # form_data = self.schema_to_form(ex,schema)
                        # ex.write(form_data)
      
      
            self.validate_volume_fraction(vf_sum, category_display_name,tab)
            density_mix = self.calc_density_mix(vf_sum, density) 

            try:
                with open(app_access.get_path_to_calculated_values(), 'r') as f:
                    parameters_dict = json.load(f)
            except json.JSONDecodeError as e:
                st.write(app_access.get_path_to_calculated_values())
                    # Handle the error gracefully, e.g., by providing a default value or logging the error.

            parameters_dict["calculatedParameters"]["effective_density"] = density_mix

            with open(app_access.get_path_to_calculated_values(),'w') as f:
                json.dump(parameters_dict,f) 
            
            non_material_component = db_helper.get_non_material_components_from_category_id(category_id)      
            component_parameters = []
            non_material_component_id, non_material_component_name, _,_,_,_,_,non_material_comp_display_name,_,_,_,non_material_comp_default_template_id,non_material_comp_context_type,non_material_comp_context_type_iri,_ = non_material_component
            
            tab.markdown("**%s**" % non_material_comp_display_name)
            check_col, property_col, value_col= tab.columns((0.3,1,2))

            
            non_material_parameters_sets = np.squeeze(db_helper.get_non_material_set_id_by_component_id(non_material_component_id))
            
            non_material_parameter,user_input,component_parameters, mass_loadings = self.fill_non_material_component(category_id,category_name,non_material_comp_default_template_id,non_material_component_id,property_col,value_col,non_material_parameters_sets,self.model_id, component_parameters, check_col,non_material_component_name,tab, density_mix, mass_loadings)

            component_parameters["label"] = non_material_comp_display_name
            component_parameters["@type"] = material_comp_context_type
            #component_parameters["@type_iri"] = material_comp_context_type_iri

            category_parameters[self.hasObjectiveProperty] = component_parameters

        if category_name == "negative_electrode":
            
            category_parameters = self.set_ne_advanced_tabs(tab, category_display_name, category_parameters)
            

        elif category_name == "positive_electrode":
            category_parameters = self.set_pe_advanced_tabs(tab,category_display_name,category_parameters)    

        if category_name == "electrolyte" or category_name == "separator":
            
            
            component_col, material_col = tab.columns((1,2))
            component_parameters = []
            material_component_id, component_name, _,_,_,_,_,material_comp_display_name,_,_,_,material_comp_default_template_id,material_comp_context_type,material_comp_context_type_iri,_ = material_components[0]
                
                
            component_col.markdown("**%s**" % material_comp_display_name)
    
            material_formatted_parameters,formatted_materials,selected_value_id, component_parameters,_,_ = self.fill_material_column(component_name,material_comp_default_template_id,material_component_id,material_col,material_comp_display_name,material_comp_context_type_iri,material_components[0], category_parameters, density=None)
           
            component_parameters = self.create_component_parameters_dict(component_parameters)    

            if component_name == "electrolyte_materials":
                material_comp_relation = self.hasElectrolyte
                label = "Electrolyte properties"
            elif component_name == "separator_materials":
                material_comp_relation = self.hasSeparator
                label = "Separator properties"

            component_parameters["label"] = label
            component_parameters["@type"] = material_comp_context_type
            #component_parameters["@type_iri"] = material_comp_context_type_iri

            category_parameters[material_comp_relation] = component_parameters
            

            material_choice = formatted_materials.options.get(selected_value_id).name

            material = formatted_materials.options.get(selected_value_id)
            parameters = material.parameters
            
            
            if material_choice == "user_defined":
                
                if "conductivity" not in st.session_state:
                    st.session_state.conductivity = r'''1e-4*c*((-10.5 + 0.668e-3*c + 0.494e-6*c^2) + (0.074 - 1.78e-5*c - 8.86e-10*c^2)*T + (-6.96e-5 + 2.80e-8*c)*T^2)^2'''
            
                if "diffusion_coefficient" not in st.session_state:
                    st.session_state.diffusion_coefficient = r'''1e-4 * 10^(-4.43 - 54/(T - 229 - 5*c*1e-3) - 0.22*c*1e-3)'''

                component_parameters = []
                ex = tab.expander("Fill in '%s' parameters" % material_comp_display_name)
                    
                with ex:
                    for parameter_id in parameters:
                        parameter = parameters.get(parameter_id)
                        if parameter.name == "charge_carrier_transference_number" or parameter.name == "counter_ion_transference_number":  
                            tr_value = "tr_value_{}_{}".format(category_id, parameter.name)
                            index_key= "index_{}_{}".format(category_id, parameter.name)

                            if tr_value not in st.session_state:
                                st.session_state[tr_value] = parameter.min_value
                            if index_key not in st.session_state:
                                st.session_state[index_key] = None    


                    par_indexes = 0
                    for parameter_id in parameters:

                        parameter = parameters.get(parameter_id)
                        parameter_options =parameter.options.get(selected_value_id)
     
                        tr_value = "tr_value_{}_{}".format(category_id, parameter.name)

                        if not isinstance(parameter, FunctionParameter):
                            property_col, value_col= ex.columns((1.5,2))
                            if parameter.name == "charge_carrier_transference_number":
                                cc_tr_place = st.empty()
                            elif parameter.name == "counter_ion_transference_number":
                                cion_tr_place = st.empty()
                                

                            if isinstance(parameter, StrParameter):
                                property_col.write("[{}]({})".format(parameter.display_name, parameter.context_type_iri))


                                user_input = value_col.text_input(
                                label=parameter.name,
                                value=parameter_options.value,
                                key="input_{}_{}".format(category_id, parameter.id),
                                label_visibility="collapsed"
                                )

  
                            else:
                                property_col.write("[{}]({})".format(parameter.display_name, parameter.context_type_iri)+ " (" + "[{}]({})".format(parameter.unit, parameter.unit_iri) + ")")

                                user_input = value_col.number_input(
                                label=parameter.name,
                                value=parameter.min_value,
                                min_value=parameter.min_value,
                                max_value=parameter.max_value,
                                key="input_{}_{}".format(category_id, parameter.id),
                                format=parameter.format,
                                step=parameter.increment,
                                label_visibility="collapsed"
                                )
                  
                        elif isinstance(parameter, FunctionParameter):
                                

                                st.divider()
                                st.write("[{}]({})".format(parameter.display_name, parameter.context_type_iri))

                                if component_name == "electrolyte_materials":

                                   

                                    variables = "variables_{}".format(parameter_id)

                                    if variables not in st.session_state:
                                       
                                        st.session_state[variables] = r'c,T'
                                    

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

                                    
                                    #func_du = ex.toggle(label="Visualize your variables", key = "toggle_vis_du_{}".format(parameter_id))

                                    # if func_du:
                                    #     # Convert the input string to a SymPy equation
                                    #     try:
                                    
                                    #         eq_variables = sp.sympify(variables_str)
                                    #         ex.latex(sp.latex(eq_variables))
                                    #     except sp.SympifyError:
                                    #         ex.warning("Invalid equation input. Please enter a valid mathematical expression.")

                                    if variables_str == "":
                                        ex.warning("You haven't specified the variables your equation depends on.")
                                        
                                    else:
                                        variables_array = variables_str.split(',')
                                        
                                        user_input = {'@type': 'emmo:String', 'hasStringData': {'function': quantity_str, 'argument_list':variables_array}}
                                    

                                    # else: 
                                    #     user_input = None

                            
                        if not user_input:
                            st.warning("You haven't defined the function for the {} yet. Enable the 'Create you own {} function' toggle.".format(parameter.display_name,parameter.display_name))

                        if parameter:
                            parameter.set_selected_value(user_input)

                            formatted_value_dict = parameter.selected_value
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
                            
                            # elif isinstance(non_material_parameter, FunctionParameter):
                            #     formatted_value_dict = {
                            #         "@type": "emmo:Function",
                            #         self.hasStringData: non_material_parameter.selected_value
                            #     }

                            parameter_details = {
                                "label": parameter.name,
                                "@type": parameter.context_type if parameter.context_type else "None",
                                "value": formatted_value_dict
                            }
                            if isinstance(parameter, NumericalParameter):
                                parameter_details["unit"] = {
                                        "label": parameter.unit_name if parameter.unit_name else parameter.unit,
                                        "symbol": parameter.unit,
                                        "@type": "emmo:"+parameter.unit_name if parameter.unit_name else parameter.unit,
                                        #"@type_iri": n_to_p_parameter.unit_iri if n_to_p_parameter.unit_iri else None
                                    }

                          
                            component_parameters.append(parameter_details)
                            
                        par_indexes +=1


                    component_parameters = self.create_component_parameters_dict(component_parameters)
            

                    component_parameters["label"] = material_comp_display_name
                    component_parameters["@type"] = material_comp_context_type
                    #component_parameters["@type_iri"] = material_comp_context_type_iri
            
                    if component_name == "electrolyte_materials":
                        material_comp_relation = self.hasElectrolyte
                    elif component_name == "separator_materials":
                        material_comp_relation = self.hasSeparator
                    
                    
                    category_parameters[material_comp_relation] = component_parameters

        non_material_component = db_helper.get_non_material_components_from_category_id(category_id)      

        non_material_component_id, non_material_component_name, _,_,_,_,_,non_material_comp_display_name,_,_,_,non_material_comp_default_template_id,non_material_comp_context_type,non_material_comp_context_type_iri,_ = non_material_component
        
        if category_name == "separator" or category_name == "boundary_conditions" or category_name == "electrolyte":
            component_parameters = []
            tab.markdown("**%s**" % non_material_comp_display_name)
            property_col, value_col= tab.columns((1,2))
            non_material_parameters_sets = db_helper.get_non_material_set_id_by_component_id(non_material_component_id)[0]
            
            non_material_parameter,user_input, component_parameters,_ = self.fill_non_material_component(category_id,category_name,non_material_comp_default_template_id,non_material_component_id,property_col,value_col,non_material_parameters_sets,self.model_id,component_parameters, check_col = None,non_material_component_name = None, tab = None, density_mix = None, mass_loadings = None)
            
            component_parameters["label"] = non_material_comp_display_name
            component_parameters["@type"] = non_material_comp_context_type
            #component_parameters["@type_iri"] = non_material_comp_context_type_iri
    
            if non_material_component_name == "electrolyte_materials":
                material_comp_relation = self.hasElectrolyte
            elif non_material_component_name == "separator_materials":
                material_comp_relation = self.hasSeparator
            if category_name == "boundary_conditions":
                material_comp_relation = self.hasBoundaryConditions
                category_parameters[material_comp_relation] = component_parameters
            else:
                category_parameters[material_comp_relation][self.hasQuantitativeProperty] += (component_parameters[self.hasQuantitativeProperty])


            adv_input =tab.expander("Show '{}' advanced parameters".format(category_display_name))
            
            component_parameters = []
            non_material_component = db_helper.get_advanced_components_from_category_id(category_id)      

            non_material_component_id, non_material_component_name, _,_,_,_,_,non_material_comp_display_name,_,_,_,non_material_comp_default_template_id,non_material_comp_context_type,non_material_comp_context_type_iri,_ = non_material_component

            raw_template_parameters = tuple(np.squeeze(db_helper.get_advanced_template_by_template_id(default_template_id)))

            non_material_parameters_sets = db_helper.get_non_material_set_id_by_component_id(non_material_component_id)
            non_material_parameter_set_id, non_material_parameters_set_name, _ ,_,_ = non_material_parameters_sets[0]
            
            if np.ndim(raw_template_parameters) > 1:
                non_material_parameters_raw = []
                for non_material_parameter_raw_template in raw_template_parameters:
                    
                    non_material_parameter_id,name,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_ = non_material_parameter_raw_template

                    non_material_parameter = db_helper.get_advanced_parameters_by_parameter_set_id(non_material_parameter_id, non_material_parameter_set_id)[0]
                    
                    non_material_parameters_raw.append(non_material_parameter)

            else:

                non_material_parameter_id,name,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_ = raw_template_parameters
                non_material_parameter_id = int(non_material_parameter_id)
          
                non_material_parameters_raw = db_helper.get_advanced_parameters_by_parameter_set_id(non_material_parameter_id, non_material_parameter_set_id)[0]
            parameter_sets_name_by_id = {}
            for id, name, _,_,_ in non_material_parameters_sets:

                parameter_sets_name_by_id[id] = name

            formatted_parameters = self.formatter.format_parameters(non_material_parameters_raw, raw_template_parameters, parameter_sets_name_by_id)

            for parameter_id in formatted_parameters:
                parameter = formatted_parameters.get(parameter_id)
                if parameter.is_shown_to_user:
                    selected_parameter_id = db_helper.get_parameter_id_from_template_parameter_and_parameter_set(
                        template_parameter_id=parameter.id,
                        parameter_set_id=non_material_parameter_set_id
                    )
                    st_space(tab)
                    name_col, input_col = adv_input.columns([1, 2])

                    if isinstance(parameter, NumericalParameter):
                        name_col.write("[{}]({})".format(parameter.display_name, parameter.context_type_iri) + " (" + "[{}]({})".format(parameter.unit, parameter.unit_iri) + ")")

                        user_input = input_col.number_input(
                            label=parameter.name,
                            value=parameter.options.get(selected_parameter_id).value,
                            min_value=parameter.min_value,
                            max_value=parameter.max_value,
                            key="input_{}_{}".format(non_material_component_id, parameter_id),
                            format=parameter.format,
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

                formatted_value_dict = parameter.selected_value

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

                # elif isinstance(parameter, FunctionParameter):
                #     formatted_value_dict = {
                #         "@type": "emmo:Boolean",
                #         self.hasStringData: parameter.selected_value
                #     }
                

                parameter_details = {
                    "label": parameter.name,
                    "@type": parameter.context_type_iri if parameter.context_type_iri else "None",
                    "value": formatted_value_dict
                }
                if isinstance(parameter, NumericalParameter):
                    parameter_details["unit"] = {
                                        "label": parameter.unit_name if parameter.unit_name else parameter.unit,
                                        "symbol": parameter.unit,
                                        "@type": "emmo:"+parameter.unit_name if parameter.unit_name else parameter.unit,
                                        #"@type_iri": n_to_p_parameter.unit_iri if n_to_p_parameter.unit_iri else None
                                    }


                component_parameters.append(parameter_details)

            
            if non_material_component_name == "electrolyte_materials":
                material_comp_relation = self.hasElectrolyte
            elif non_material_component_name == "separator_materials":
                material_comp_relation = self.hasSeparator
            elif category_name == "boundary_conditions":
                material_comp_relation = self.hasBoundaryConditions   

            category_parameters[material_comp_relation][self.hasQuantitativeProperty] += component_parameters

            
        return category_parameters, emmo_relation, mass_loadings

    def fill_category_protocol(self, category_id,category_display_name, category_name, emmo_relation, default_template_id, tab,category_parameters):
        """
        same idea as fill category, just choosing a Protocol to set all params
        """

        component_parameters = []
        non_material_component = db_helper.get_non_material_components_from_category_id(category_id)      

        non_material_component_id, non_material_component_name, _,_,_,_,_,non_material_comp_display_name,_,_,_,non_material_comp_default_template_id,non_material_comp_context_type,non_material_comp_context_type_iri,_ = non_material_component
            
        raw_template_parameters = db_helper.get_non_material_template_by_template_id(default_template_id,self.model_id)

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

        raw_parameters = db_helper.extract_parameters_by_parameter_set_id(selected_parameter_set_id)

        formatted_parameters = self.formatter.format_parameters(raw_parameters, raw_template_parameters, parameter_sets_name_by_id)

        for parameter_id in formatted_parameters:
            parameter = formatted_parameters.get(parameter_id)
            if parameter.is_shown_to_user:
                selected_parameter_id = db_helper.get_parameter_id_from_template_parameter_and_parameter_set(
                    template_parameter_id=parameter.id,
                    parameter_set_id=selected_parameter_set_id
                )
                st_space(tab)
                name_col, input_col = tab.columns([1, 2])

                if isinstance(parameter, NumericalParameter):
                    name_col.write("[{}]({})".format(parameter.display_name, parameter.context_type_iri) + " (" + "[{}]({})".format(parameter.unit, parameter.unit_iri) + ")")

                    user_input = input_col.number_input(
                        label=parameter.name,
                        value=parameter.options.get(selected_parameter_id).value,
                        min_value=parameter.min_value,
                        max_value=parameter.max_value,
                        key="input_{}_{}".format(non_material_component_id, parameter_id),
                        format=parameter.format,
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

            formatted_value_dict = parameter.selected_value

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
                        "@type": "emmo:Boolean",
                        self.hasStringData: parameter.selected_value
                    }

            parameter_details = {
                "label": parameter.name,
                "@type": parameter.context_type_iri if parameter.context_type_iri else "None",
                "value": formatted_value_dict
            }
            if isinstance(parameter, NumericalParameter):
                parameter_details["unit"] = {
                    "label": parameter.unit_name if parameter.unit_name else parameter.unit,
                    "symbol": parameter.unit,
                    "@type": "emmo:"+parameter.unit_name if parameter.unit_name else parameter.unit,
                    #"@type_iri": n_to_p_parameter.unit_iri if n_to_p_parameter.unit_iri else None
                }

            component_parameters.append(parameter_details)
        component_parameters = self.create_component_parameters_dict(component_parameters)
        component_parameters["label"] = non_material_comp_display_name
        component_parameters["@type"] = non_material_comp_context_type
        #component_parameters["@type_iri"] = non_material_comp_context_type_iri
    
        category_parameters[self.hasCyclingProcess] = component_parameters

        adv_input =tab.expander("Show '{}' advanced parameters".format(category_display_name))
        component_parameters = []
        non_material_component = db_helper.get_advanced_components_from_category_id(category_id)      

        non_material_component_id, non_material_component_name, _,_,_,_,_,non_material_comp_display_name,_,_,_,non_material_comp_default_template_id,non_material_comp_context_type,non_material_comp_context_type_iri,_ = non_material_component

        raw_template_parameters = tuple(np.squeeze(db_helper.get_advanced_template_by_template_id(default_template_id)))

        non_material_parameters_sets = db_helper.get_non_material_set_id_by_component_id(non_material_component_id)
        non_material_parameter_set_id, non_material_parameters_set_name, _ ,_,_ = non_material_parameters_sets[0]
        
        if np.ndim(raw_template_parameters) > 1:
            non_material_parameters_raw = []
            for non_material_parameter_raw_template in raw_template_parameters:
                
                non_material_parameter_id,name,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_ = non_material_parameter_raw_template

                non_material_parameter = db_helper.get_advanced_parameters_by_parameter_set_id(non_material_parameter_id, non_material_parameter_set_id)[0]
                
                non_material_parameters_raw.append(non_material_parameter)

        else:

            non_material_parameter_id,name,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_ = raw_template_parameters
            non_material_parameter_id = int(non_material_parameter_id)

            non_material_parameters_raw = db_helper.get_advanced_parameters_by_parameter_set_id(non_material_parameter_id, non_material_parameter_set_id)[0]
        parameter_sets_name_by_id = {}
        for id, name, _,_,_ in non_material_parameters_sets:

            parameter_sets_name_by_id[id] = name

        formatted_parameters = self.formatter.format_parameters(non_material_parameters_raw, raw_template_parameters, parameter_sets_name_by_id)

        for parameter_id in formatted_parameters:
            parameter = formatted_parameters.get(parameter_id)
            if parameter.is_shown_to_user:
                selected_parameter_id = db_helper.get_parameter_id_from_template_parameter_and_parameter_set(
                    template_parameter_id=parameter.id,
                    parameter_set_id=non_material_parameter_set_id
                )
                st_space(tab)
                name_col, input_col = adv_input.columns([1, 2])

                if isinstance(parameter, NumericalParameter):
                    name_col.write("[{}]({})".format(parameter.display_name, parameter.context_type_iri) + " (" + "[{}]({})".format(parameter.unit, parameter.unit_iri) + ")")

                    user_input = input_col.number_input(
                        label=parameter.name,
                        value=parameter.options.get(selected_parameter_id).value,
                        min_value=parameter.min_value,
                        max_value=parameter.max_value,
                        key="input_{}_{}".format(non_material_component_id, parameter_id),
                        format=parameter.format,
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

            formatted_value_dict = parameter.selected_value

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

            # elif isinstance(parameter, FunctionParameter):
            #     formatted_value_dict = {
            #         "@type": "emmo:Boolean",
            #         self.hasStringData: parameter.selected_value
            #     }
            

            parameter_details = {
                "label": parameter.name,
                "@type": parameter.context_type_iri if parameter.context_type_iri else "None",
                "value": formatted_value_dict
            }
            if isinstance(parameter, NumericalParameter):
                parameter_details["unit"] = {
                    "label": parameter.unit_name if parameter.unit_name else parameter.unit,
                    "symbol": parameter.unit,
                    "@type": "emmo:"+parameter.unit_name if parameter.unit_name else parameter.unit,
                    #"@type_iri": n_to_p_parameter.unit_iri if n_to_p_parameter.unit_iri else None
                }


            component_parameters.append(parameter_details)


        category_parameters[self.hasCyclingProcess][self.hasQuantitativeProperty] += component_parameters

        return category_parameters


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
        self.button_style = st.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: #e1e7f2;
                
                
                height:3em;
                width:10em;
                font-size:20px;
                        
                border-radius:10px 10px 10px 10px;
            }
            </style>""", unsafe_allow_html=True)

        self.gui_parameters = gui_parameters
        #self.gui_file_data = json.dumps(gui_parameters, indent=2)
        #self.gui_file_name = "gui_output_parameters.json"
        #self.file_mime_type = "application/json"

        self.api_url = "http://flask_api:8000/run_simulation"
        self.json_input_folder = 'BattMoJulia'
        self.json_input_file = 'battmo_formatted_input.json'
        self.julia_module_folder = 'BattMoJulia'
        self.julia_module = 'runP2DBattery.jl'
        self.results_folder = "results"
        self.temporary_results_file = "battmo_result"
        
        self.set_section()

    def set_section(self):

        save_run = st.container()

        self.set_header(save_run)
        self.set_buttons(save_run)

    def set_header(self,save_run):

        save_run.markdown("### " + self.header)
        save_run.text(" ")

    def set_buttons(self, save_run):

        #empty,run,empty2 = save_run.columns((0.3,1,1))

        self.button_style

        # update = update.button(
        #     label="UPDATE",
        #     on_click=self.update_on_click,
        #     args= (save_run, )
        #     #help = "Update the parameter values."
        # )

        runing = save_run.button(
            label="RUN",
            on_click= self.execute_api_on_click,
            args = (save_run, )
            #help = "Run the simulation (after updating the parameters)."
            
        )

        
    def update_on_click(self):
        
        self.update_json_battmo_input()
        self.update_json_LD()
        
        st.session_state.update_par = True

        #save_run.success("Your parameters are saved! Run the simulation to get your results.")

    def update_json_battmo_input(self):

        path_to_battmo_input = app_access.get_path_to_linked_data_input()

        # save formatted parameters in json file
        with open(path_to_battmo_input, "w") as new_file:
            json.dump(
                self.gui_parameters,
                new_file,
                indent=3)
            
    def update_json_LD(self):

        # Format parameters from json-LD to needed format
        path_to_battmo_formatted_input = app_access.get_path_to_battmo_formatted_input()

        # save formatted parameters in json file
        with open(path_to_battmo_formatted_input, "w") as new_file:
            json.dump(
                match_json_LD.get_batt_mo_dict_from_gui_dict(self.gui_parameters),
                new_file,
                indent=3
            )

    def execute_api_on_click(self, save_run):

        ##############################
        # # Remember user changed values
        # for k, v in st.session_state.items():
        #     st.session_state[k] = v
        # ##############################

        ##############################
        # Set page directory to base level to allow for module import from different folder

        sys.path.insert(0, app_access.get_path_to_streamlit_dir())
        
        ##############################

        self.update_on_click()

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

            with open(app_access.get_path_to_battmo_results(), "wb") as f:
                f.write(response_start.content)

            # with open(app_access.get_path_to_battmo_results(), "wb") as f:
            #     pickle.dump(response_start.content, f)

        else:
            st.write(response_start)
    
        
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
    def __init__(self):

        self.check_for_divergence()
        

    def check_for_divergence(self):

        if st.session_state.sim_finished:

            N = self.get_timesteps_setting()
            number_of_states, log_messages = self.get_timesteps_execution()

            self.divergence_check_logging(N,number_of_states, log_messages)

    def get_timesteps_setting(self):

        # retrieve saved parameters from json file
        with open(app_access.get_path_to_battmo_formatted_input()) as json_gui_parameters:
            gui_parameters = json.load(json_gui_parameters)

        N = gui_parameters["TimeStepping"]["N"]

        return N
    
    def get_timesteps_execution(self):

        # Retrieve latest results
        with open(app_access.get_path_to_battmo_results(), "rb") as pickle_result:
            result = pickle.load(pickle_result)
            #result_str = pickle_result.read()

        
        #sresult = eval(result_str)
        
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

        return number_of_states, log_messages
    
    def divergence_check_logging(self,N, number_of_states,log_messages):

        save_run = st.empty()
        if len(log_messages) > 1:
            c = save_run.container()
            if number_of_states >= N:
                
                st.session_state.succes = True
                c.success("Simulation finished successfully, but some warnings were produced. See the logging below for the warnings and check the results on the next page.")

            else:
                c.error("Simulation did not finish, some warnings were produced. See the logging below for the warnings.")
                st.session_state.succes = False
            
            c.markdown("***Logging:***")
                
            log_message = ''' \n'''
            for message in log_messages:
                log_message = log_message + message+ '''\n'''
            
            c.code(log_message + ''' \n''')

        else:    
            save_run.success("Simulation finished successfully! Check the results on the 'Results' page.")  
            st.session_state.succes = True


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
        with open(app_access.get_path_to_battmo_formatted_input()) as json_formatted_gui_parameters:
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
            st.markdown("## " + self.download_header)

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

        l, w = 80, 80

        def image_open(file_name):
            image = Image.open(join_path(file_name))
            return image.resize((l, w))

        """
        This dict has to be refactored, it needs at least:
        - images for every parameter category
        - proper naming
        - remove useless items
        """
        return {
            "4": image_open("cell_coin.png"),
            "9": image_open("cell_prismatic.png"),
            "3": image_open("plus.png"),
            "1": image_open("plus.png"),
            "0": image_open("minus.png"),
            "2": image_open("electrolyte.png"),
            "5": image_open("current.png"),
            "6": image_open("current.png"),
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
        P2D_model= db_helper.get_model_parameters_as_dict(1)
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
    def __init__(self):
        self.results = None
        self.get_results_data()

    def get_results_data(self):

        results = self.retrieve_results()
        formatted_results = self.format_results(results)

        self.results = formatted_results
        return self.results

    def retrieve_results(self):

        with open(app_access.get_path_to_battmo_results(), "rb") as pickle_result:
            result = pickle.load(pickle_result)

        return result
    
    def format_results(self, results):
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
            negative_electrode_concentration_jl,
            electrolyte_concentration_jl,
            positive_electrode_concentration_jl,
            negative_electrode_potential_jl,
            electrolyte_potential_jl,
            positive_electrode_potential_jl

        ] = results

        length_1d_ne = len(negative_electrode_concentration_jl)
        length_2d_ne = len(negative_electrode_concentration_jl[0])
        length_1d_pe = len(positive_electrode_concentration_jl)
        length_2d_pe = len(positive_electrode_concentration_jl[0])
        length_1d_el = len(electrolyte_concentration_jl)
        length_2d_el = len(electrolyte_concentration_jl[0])
        negative_electrode_concentration = np.zeros((length_1d_ne,length_2d_ne))
        positive_electrode_concentration = np.zeros((length_1d_pe,length_2d_pe))
        negative_electrode_potential = np.zeros((length_1d_ne,length_2d_ne))
        positive_electrode_potential = np.zeros((length_1d_pe,length_2d_pe))
        electrolyte_concentration = np.zeros((length_1d_el,length_2d_el))
        electrolyte_potential = np.zeros((length_1d_el,length_2d_el))

        for i in range(length_1d_pe):
            for j in range(length_2d_pe):
                pe_c_sub = positive_electrode_concentration_jl[i]
                pe_p_sub = positive_electrode_potential_jl[i]
                positive_electrode_concentration[i,j] = pe_c_sub[j]
                positive_electrode_potential[i,j] = pe_p_sub[j]

        for i in range(length_1d_el):
            for j in range(length_2d_el):
                el_c_sub = electrolyte_concentration_jl[i]
                el_p_sub = electrolyte_potential_jl[i]
                electrolyte_concentration[i,j] = el_c_sub[j]
                electrolyte_potential[i,j] = el_p_sub[j]

        for i in range(length_1d_ne):
            for j in range(length_2d_ne):
                ne_c_sub = negative_electrode_concentration_jl[i]
                ne_p_sub = negative_electrode_potential_jl[i]
                negative_electrode_concentration[i,j] = ne_c_sub[j]
                negative_electrode_potential[i,j] = ne_p_sub[j]
            
        results = [
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
        
        return results
    
class SetIndicators():
    """
    used to render the indicator parameters on the results page.
    """
    def __init__(self, page_name):

        self.page_name = page_name
        self.set_indicators()

    def set_indicators(self):
        indicators= self.get_indicators()
        self.render_indicators(indicators)

    def get_indicators(self):

        with open(app_access.get_path_to_linked_data_input(), 'r') as f:
            gui_parameters = json.load(f)

        indicators = match_json_LD.get_indicators_from_gui_dict(gui_parameters)   

        return indicators
    
    def render_indicators(self,indicators):

        # cell_mass = indicators["Cell"]["cellMass"]
        # cell_energy = indicators["Cell"]["cellEnergy"]
        # cell_capacity = indicators["Cell"]["nominalCellCapacity"]
        n_to_p_ratio = indicators["Cell"]["NPRatio"]

        ne_mass_loading = indicators["NegativeElectrode"]["massLoading"]
        ne_thickness = indicators["NegativeElectrode"]["thickness"]
        ne_porosity = indicators["NegativeElectrode"]["porosity"]
        #ne_specific_capacity = indicators["NegativeElectrode"]["specificCapacity"]
        pe_mass_loading = indicators["PositiveElectrode"]["massLoading"]
        pe_thickness = indicators["PositiveElectrode"]["thickness"]
        pe_porosity = indicators["PositiveElectrode"]["porosity"]
        #pe_specific_capacity = indicators["PositiveElectrode"]["specificCapacity"]

        if self.page_name == "Simulation":
            col1, col2, col3, col4 = st.columns(4)
            # col4.metric(
            #     label = "Cell Mass ({})".format(cell_mass["unit"]),
            #     value = np.round(cell_mass["value"],2),
            #     label_visibility= "visible"
            # )
            # col2.metric(
            #         label = "Energy ({})".format(cell_energy["unit"]),
            #         value = np.round(cell_energy["value"],2),
            #         label_visibility= "visible"
            #     )
            # col3.metric(
            #         label = "Capacity ({})".format(cell_capacity["unit"]),
            #         value = np.round(cell_capacity["value"],2),
            #         label_visibility= "visible"
            #     )
            col1.metric(
                    label = "N/P ratio ({})".format(n_to_p_ratio["unit"]),
                    value = np.round(n_to_p_ratio["value"],2),
                    label_visibility= "visible"
                )

        elif self.page_name == "Results":
            NE, PE,cell = st.tabs(["Negative Electrode", "Positive Electrode","Cell"])

            col1, col2, col3, col4 = cell.columns(4)

            # col1.metric(
            #     label = "Cell Mass ({})".format(cell_mass["unit"]),
            #     value = np.round(cell_mass["value"],2),
            #     label_visibility= "visible"
            # )
            # col2.metric(
            #         label = "Energy ({})".format(cell_energy["unit"]),
            #         value = np.round(cell_energy["value"],2),
            #         label_visibility= "visible"
            #     )
            # col3.metric(
            #         label = "Capacity ({})".format(cell_capacity["unit"]),
            #         value = np.round(cell_capacity["value"],2),
            #         label_visibility= "visible"
            #     )
            col1.metric(
                    label = "N/P ratio ({})".format(n_to_p_ratio["unit"]),
                    value = np.round(n_to_p_ratio["value"],2),
                    label_visibility= "visible"
                )

            mass_loading, thickness, porosity = NE.columns(3)

            mass_loading.metric(
                    label = "Mass Loading ({})".format(ne_mass_loading["unit"]),
                    value = np.round(ne_mass_loading["value"],2),
                    label_visibility= "visible"
                )
            
            thickness.metric(
                    label = "Thickness ({})".format(ne_thickness["unit"]),
                    value = np.round(ne_thickness["value"],2),
                    label_visibility= "visible"
                )
            
            porosity.metric(
                    label = "Porosity ({})".format(ne_porosity["unit"]),
                    value = np.round(ne_porosity["value"],2),
                    label_visibility= "visible"
                )
            # capacity.metric(
            #         label = "Specific Capacity ({})".format(ne_specific_capacity["unit"]),
            #         value = np.round(ne_specific_capacity["value"],2),
            #         label_visibility= "visible"
            #     )
            
            mass_loading, thickness, porosity= PE.columns(3)

            mass_loading.metric(
                    label = "Mass Loading ({})".format(pe_mass_loading["unit"]),
                    value = np.round(pe_mass_loading["value"],2),
                    label_visibility= "visible"
                )
            
            thickness.metric(
                    label = "Thickness ({})".format(pe_thickness["unit"]),
                    value = np.round(pe_thickness["value"],2),
                    label_visibility= "visible"
                )
            
            porosity.metric(
                    label = "Porosity ({})".format(pe_porosity["unit"]),
                    value = np.round(pe_porosity["value"],2),
                    label_visibility= "visible"
                )
            # capacity.metric(
            #         label = "Specific Capacity ({})".format(pe_specific_capacity["unit"]),
            #         value = np.round(pe_specific_capacity["value"],2),
            #         label_visibility= "visible"
            #     )
            
        else:
            print("ERROR: Page name '{}' to get indicators doesn't match.".format(self.page_name))

            


class SetHDF5Download():
    """
    Used to render the hdf5 output file on the Results page.
    """
    def __init__(self,results):

        self.header = "Download results"
        self.results = results
        self.set_download_hdf5_button()

    def set_download_hdf5_button(self):

        with st.sidebar:
            # set Download header
            st.markdown("## " + self.header)

            st.download_button(
                label="HDF5 Results",
                file_name="hdf5_results.hdf5",
                data=self.prepare_h5_file(),
                mime="application/x-hdf",
                help="Download your results."
            )

    # Create hdf5 from numpy arrays, result cached to optimize software.
    # Cache cleared after generating new results (cf RunSimulation)
    @st.cache_data
    def prepare_h5_file(_self):

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

            ] = _self.results


        bio = io.BytesIO()
        # cf https://stackoverflow.com/questions/73157377/how-to-download-various-data-from-streamlit-to-hdf5-file-with-st-download-butto

        with h5py.File(bio, "w") as f:
            f.attrs['number_of_states'] = number_of_states

            f.create_dataset("time_values", data=time_values)
            f.create_dataset("cell_voltage", data=cell_voltage)
            f.create_dataset("cell_current", data=cell_current)

            grids = f.create_group("grids")
            grids.create_dataset("negative_electrode_grid", data=negative_electrode_grid)
            grids.create_dataset("positive_electrode_grid", data=positive_electrode_grid)
            grids.create_dataset("electrolyte_grid", data=electrolyte_grid)

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
                    "ne_c_state_{}".format(i),
                    data=np.array(negative_electrode_concentration[i], dtype=float)
                )
                positive_electrode_concentrations.create_dataset(
                    "pe_c_state_{}".format(i),
                    data=np.array(positive_electrode_concentration[i], dtype=float)
                )
                electrolyte_concentrations.create_dataset(
                    "elyte_c_state_{}".format(i),
                    data=np.array(electrolyte_concentration[i], dtype=float)
                )

                negative_electrode_potentials.create_dataset(
                    "ne_p_state_{}".format(i),
                    data=np.array(negative_electrode_potential[i], dtype=float)
                )
                positive_electrode_potentials.create_dataset(
                    "pe_p_state_{}".format(i),
                    data=np.array(positive_electrode_potential[i], dtype=float)
                )
                electrolyte_potentials.create_dataset(
                    "elyte_p_state_{}".format(i),
                    data=np.array(electrolyte_potential[i], dtype=float)
                )

        return bio



class SetGraphs():
    """
    Used to render the graphs on the Results page.
    """
    def __init__(_self,results):

        _self.header = "Visualize results"
        _self.dashboard_header = "Dynamic dashboard"
        _self.results = results

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

        ] = results
         
        _self.set_graphs()

    def set_graphs(_self):

        ##############################
        # Remember user changed values
        for k, v in st.session_state.items():
            st.session_state[k] = v

        #Remember widget actions when switching between pages (for example: selectbox choice)
        st.session_state.update(st.session_state)
        ##############################
        
        #dynamic, colormaps = _self.set_graph_toggles()

        #if dynamic:
       
        st.markdown("# " + _self.dashboard_header)

        st_space(space_number=1, space_width= 3 )

        _self.set_dynamic_dashboard()

        #if colormaps:
        _self.set_colormaps()

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
        init_time_value = 0.0
        max_time_value = max(_self.time_values)
        step_size = _self.get_min_difference()
        selected_time = st.slider(
            key = "DynamicDashboard",
            label="Select a time (hours)",
            min_value=init_time_value,
            max_value= max_time_value,
            step=step_size
            )


        state = 0
        while _self.time_values[state] < selected_time:
            state += 1

        _self.view_plots_static(state)

    def set_colormaps(_self):
        # Colormaps


        with st.sidebar:
            select = st.multiselect(label= "Select contour plots.",
                                    options=["Negative electrode concentration", "Positive electrode concentration", 
                                             "Negative electrode potential", "Positive electrode potential", 
                                             "Electrolyte concentration", "Electrolyte potential" ],
                                             key = "multi_contour_plots"
                                             )

        #col1, col2= st.columns(2)
        for choice in select:
            if choice == "Negative electrode concentration":
                st.plotly_chart(_self.get_ne_c_color())
            if choice == "Positive electrode concentration":
                st.plotly_chart(_self.get_pe_c_color())
            if choice == "Negative electrode potential":
                st.plotly_chart(_self.get_ne_p_color())
            if choice == "Positive electrode potential":
                st.plotly_chart(_self.get_pe_p_color())
            if choice == "Electrolyte concentration":
                st.plotly_chart(_self.get_elyte_c_color())
            if choice == "Electrolyte potential":
                st.plotly_chart(_self.get_elyte_p_color())


    @st.cache_data
    def get_elyte_p_color(_self):
        return _self.create_colormap(
            x_data=_self.electrolyte_grid,
            y_data=_self.time_values,
            z_data=_self.electrolyte_potential,
            title="Electrolyte - Potential",
            x_label="Position  /  \u00B5m",
            y_label="Time  /  h",
            cbar_label="Potential  /  V"
        )

    @st.cache_data
    def get_elyte_c_color(_self):
        return _self.create_colormap(
            x_data=_self.electrolyte_grid,
            y_data=_self.time_values,
            z_data=_self.electrolyte_concentration,
            title="Electrolyte - Concentration",
            x_label="Position  /  \u00B5m",
            y_label="Time  /  h",
            cbar_label="Concentration  /  mol . L-1"
        )
    
    @st.cache_data
    def get_pe_p_color(_self):
        return _self.create_colormap(
            x_data=_self.positive_electrode_grid,
            y_data=_self.time_values,
            z_data=_self.positive_electrode_potential,
            title="Positive Electrode - Potential",
            x_label="Position  /  \u00B5m",
            y_label="Time  /  h",
            cbar_label="Potential  /  V"
        )
    
    @st.cache_data
    def get_pe_c_color(_self):
        return _self.create_colormap(
            x_data=_self.positive_electrode_grid,
            y_data=_self.time_values,
            z_data=np.array(_self.positive_electrode_concentration),
            title="Positive Electrode - Concentration",
            x_label="Position  /  \u00B5m",
            y_label="Time  /  h",
            cbar_label="Concentration  /  mol . L-1"
        )
    
    @st.cache_data
    def get_ne_c_color(_self):
        return _self.create_colormap(
            x_data=_self.negative_electrode_grid,
            y_data=_self.time_values,
            z_data=_self.negative_electrode_concentration,
            title="Negative Electrode - Concentration",
            x_label="Position  / \u00B5m",
            y_label="Time  /  h",
            cbar_label="Concentration  /  mol . L-1"
        )


    @st.cache_data
    def get_ne_p_color(_self):
        return _self.create_colormap(
            x_data=_self.negative_electrode_grid,
            y_data=_self.time_values,
            z_data=_self.negative_electrode_potential,
            title="Negative Electrode - Potential",
            x_label="Position  /  \u00B5m",
            y_label="Time  /  h",
            cbar_label="Potential  /  V"
        )
    
    def create_colormap(_self,x_data, y_data, z_data, title, x_label, y_label, cbar_label):

        
        x_data = np.squeeze(np.array(x_data))
        y_data = np.array(y_data)

        x_color, y_color = np.meshgrid(x_data, y_data)

        fig = go.Figure(data = go.Contour(
                                    z=z_data, 
                                    y=y_data,
                                    x = x_data,
                                    colorbar=dict(title=cbar_label)
                                    ))
        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label
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
    def get_min_difference(_self):
        diff = []
        n = len(_self.time_values)
        for i in range(1, n):
            diff.append(round(_self.time_values[i] - _self.time_values[i - 1], 5))
        return float(min(diff))
    
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
        ne_concentration = _self.create_subplot(
            x_data=np.squeeze(_self.negative_electrode_grid),
            y_data=np.squeeze(_self.negative_electrode_concentration)[state],
            title="Negative Electrode Concentration  /  mol . L-1",
            x_label="Position  /  \u00B5m",
            y_label="Negative Electrode Concentration  /  mol . L-1",
            x_min=xmin,
            x_max=xmax,
            y_min=cmin_ne,
            y_max=cmax_ne,
            y_min_sub = cmin_ne_sub,
            y_max_sub = cmax_ne_sub
        )

        # Electrolyte Concentration
        elyte_concentration = _self.create_subplot(
            x_data=_self.electrolyte_grid,
            y_data=_self.electrolyte_concentration[state],
            title="Electrolyte Concentration  /  mol . L-1",
            x_label="Position  /  \u00B5m",
            y_label="Electrolyte Concentration  /  mol . L-1",
            x_min=xmin,
            x_max=xmax,
            y_min=cmin_elyte,
            y_max=cmax_elyte,
            y_min_sub = cmin_elyte_sub,
            y_max_sub = cmax_elyte_sub
        )
        
        # Positive Electrode Concentration
        positive_electrode_concentration_ext = np.full(len(_self.electrolyte_grid), np.nan)
        positive_electrode_concentration_ext[-10:] = np.squeeze(_self.positive_electrode_concentration)[state]
        pe_concentration = _self.create_subplot(
            x_data=_self.electrolyte_grid,
            y_data=positive_electrode_concentration_ext,
            title="Positive Electrode Concentration  /  mol . L-1",
            x_label="Position  /  \u00B5m",
            y_label="Positive Electrode Concentration  /  mol . L-1",
            x_min=xmin,
            x_max=xmax,
            y_min=cmin_pe,
            y_max=cmax_pe,
            y_min_sub = cmin_pe_sub,
            y_max_sub = cmax_pe_sub
        )

        # Cell Current
        cell_current_fig = _self.create_subplot(
            x_data=_self.time_values,
            y_data=_self.cell_current,
            title="Cell Current  /  A",
            x_label="Time  /  h",
            y_label="Cell Current  /  A",
            vertical_line=_self.time_values[state]
        )

        # Negative Electrode Potential
        ne_potential = _self.create_subplot(
            x_data=np.squeeze(_self.negative_electrode_grid),
            y_data=_self.negative_electrode_potential[state],
            title="Negative Electrode Potential  /  V",
            x_label="Position  /  \u00B5m",
            y_label="Negative Electrode Potential  /  V",
            x_min=xmin,
            x_max=xmax,
            y_min=phimin_ne,
            y_max=phimax_ne,
            y_min_sub = phimin_ne_sub,
            y_max_sub = phimax_ne_sub
        )

        # Electrolyte Potential
        elyte_potential = _self.create_subplot(
            x_data=_self.electrolyte_grid,
            y_data=_self.electrolyte_potential[state],
            title="Electrolyte Potential  /  V",
            x_label="Position  /  \u00B5m",
            y_label="Electrolyte Potential  /  V",
            x_min=xmin,
            x_max=xmax,
            y_min=phimin_elyte,
            y_max=phimax_elyte,
            y_min_sub = phimin_elyte_sub,
            y_max_sub = phimax_elyte_sub
        )

        # Positive Electrode Potential
        positive_electrode_potential_ext = np.full(len(_self.electrolyte_grid), np.nan)
        positive_electrode_potential_ext[-10:] = _self.positive_electrode_potential[state]
        pe_potential = _self.create_subplot(
            x_data=_self.electrolyte_grid,
            y_data=positive_electrode_potential_ext,
            title="Positive Electrode Potential  /  V",
            x_label="Position  /  \u00B5m",
            y_label="Positive Electrode Potential  /  V",
            x_min=xmin,
            x_max=xmax,
            y_min=phimin_pe,
            y_max=phimax_pe,
            y_min_sub = phimin_pe_sub,
            y_max_sub = phimax_pe_sub
            
        )

        # Cell Voltage
        cell_voltage_fig = _self.create_subplot(
            x_data=_self.time_values,
            y_data=_self.cell_voltage,
            title="Cell Voltage  /  V",
            x_label="Time  /  h",
            y_label = "Cell Voltage  /  V",
            vertical_line=_self.time_values[state]
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


        with st.sidebar:
            st.markdown("## " + _self.header)
            select = st.multiselect(label= "Select line plots.",
                                    options=["Cell current","Cell voltage", "Negative electrode concentration", 
                                             "Positive electrode concentration", "Negative electrode potential", 
                                             "Positive electrode potential", "Electrolyte concentration", "Electrolyte potential" ],
                                             default= "Cell voltage",
                                             key = "multi_line_plots"
                                             )

        #col1, col2= st.columns(2)
        for choice in select:
            if choice == "Cell current":
                st.plotly_chart(cell_current_fig, clear_figure=True)
            if choice == "Cell voltage":
                st.plotly_chart(cell_voltage_fig, clear_figure=True)
            if choice == "Negative electrode concentration":
                st.plotly_chart(ne_concentration, clear_figure=True)
            if choice == "Positive electrode concentration":
                st.plotly_chart(pe_concentration, clear_figure=True)
            if choice == "Negative electrode potential":
                st.plotly_chart(ne_potential, clear_figure=True)
            if choice == "Positive electrode potential":
                st.plotly_chart(pe_potential, clear_figure=True)
            if choice == "Electrolyte concentration":
                st.plotly_chart(elyte_concentration, clear_figure=True)
            if choice == "Electrolyte potential":
                st.plotly_chart(elyte_potential, clear_figure=True)

        
        

        
    
    @st.cache_data
    def get_graph_initial_limits(_self):
        xmin = min(_self.electrolyte_grid_bc)
        xmax = max(_self.electrolyte_grid_bc)

        cmax_elyte = max(_self.electrolyte_concentration[0])
        cmin_elyte = min(_self.electrolyte_concentration[0])

        cmax_ne = max(_self.negative_electrode_concentration[0])
        cmin_ne = min(_self.negative_electrode_concentration[0])

        cmax_pe = max(_self.positive_electrode_concentration[0])
        cmin_pe = min(_self.positive_electrode_concentration[0])

        phimax_elyte = max(_self.electrolyte_potential[0])
        phimin_elyte = min(_self.electrolyte_potential[0])

        phimax_ne = max(_self.negative_electrode_potential[0])
        phimin_ne = min(_self.negative_electrode_potential[0])

        phimax_pe = max(_self.positive_electrode_potential[0])
        phimin_pe = min(_self.positive_electrode_potential[0])

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

        cmax_elyte_sub = max(_self.electrolyte_concentration[state])
        cmin_elyte_sub = min(_self.electrolyte_concentration[state])

        cmax_ne_sub = max(_self.negative_electrode_concentration[state])
        cmin_ne_sub = min(_self.negative_electrode_concentration[state])

        cmax_pe_sub = max(_self.positive_electrode_concentration[state])
        cmin_pe_sub = min(_self.positive_electrode_concentration[state])

        phimax_elyte_sub = max(_self.electrolyte_potential[state])
        phimin_elyte_sub =min(_self.electrolyte_potential[state])

        phimax_ne_sub = max(_self.negative_electrode_potential[state])
        phimin_ne_sub = min(_self.negative_electrode_potential[state])

        phimax_pe_sub = max(_self.positive_electrode_potential[state])
        phimin_pe_sub = min(_self.positive_electrode_potential[state])

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
        
        # st.write(x_data)
        # st.write(y_data)
        fig = px.line(x=x_data, y=y_data)

        fig.update_traces(line=dict(width=5))

        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title = y_label,
            # xaxis = dict(range =[0, x_max]),
            # yaxis=dict(range=[0, y_max])
        )
        fig.update_xaxes(
            range=[0,x_max],  # sets the range of xaxis
            constrain="domain",  # meanwhile compresses the xaxis by decreasing its "domain"
        )
        if vertical_line:
             fig.add_vline(x=vertical_line, line_width=3, line_dash="dash")
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
        materials = db_helper.get_all_default_material()

        st.title("The available materials")

        display_names = []
        for material_values in materials:
            
            material = material_values
            id,name,_,_,reference_name,reference,reference_link,_,_,display_name,number_of_components,component_name_1,component_name_2,_,context_type,_,_,context_type_iri,_ = material
            display_names.append(display_name)


        select = st.multiselect(label = "Materials",options = display_names, label_visibility="collapsed")

        for material_values in materials:
            
            material = material_values
            id,name,_,_,reference_name,reference,reference_link,_,_,display_name,number_of_components,component_name_1,component_name_2,_,context_type,_,_,context_type_iri,_ = material

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
                            
                            template_parameter_id, template_parameter_name,_,_,_,_,_,template_context_type, template_context_type_iri,_,unit,unit_name,unit_iri,_,_,_,_,parameter_display_name = template_parameter
                            
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
                                        st.latex(sp.latex(sp.sympify(string_py)))
                                    
                                else:
                                    st.markdown('''```<Julia> 
                                                {}'''.format(value_dict["functionname"]))

                            else:

                                st.write("[{}]({}) = ".format(parameter_display_name, template_context_type_iri)+ 
                                            value + " (" + "[{}]({})".format(unit, unit_iri) + ")")





