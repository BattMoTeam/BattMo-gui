from PIL import Image
import pprint
import json
import pickle
import io
import h5py
import streamlit as st
import numpy as np
from copy import deepcopy
from uuid import uuid4
import sys
import requests
import pdb
from streamlit_extras.switch_page_button import switch_page
import sympy as sp
import matplotlib.pyplot as plt
from streamlit_theme import st_theme
from streamlit_javascript import st_javascript
import os
import plotly.express as px
import plotly.graph_objects as go
import streamlit_elements as el
from scipy import ndimage


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app_scripts.app_parameter_model import *
from database import db_helper
from app_scripts import app_access, match_json_LD, LD_struct, match_json_upload, app_controller
from app_scripts import app_calculations as calc
from LD_struct import SetupLinkedDataStruct 
LD = SetupLinkedDataStruct()



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
        st_space(space_width=6)
        _,col2,_ = st.columns(3)
        st_space(space_width=6)
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
        self.validate_volume_fraction = calc.validate_volume_fraction
        self.calc_density_mix = calc.calc_density_mix
        self.calc_mass_loading = calc.calc_mass_loading
        self.calc_thickness = calc.calc_thickness
        self.calc_porosity = calc.calc_porosity
        self.calc_n_to_p_ratio = calc.calc_n_to_p_ratio
        self.calc_cell_mass = calc.calc_cell_mass
        self.calc_capacity_electrode = calc.calc_capacity_electrode
        self.calc_specific_capacity_active_material = calc.calc_specific_capacity_active_material
        self.calc_cell_capacity = calc.calc_cell_capacity
        
        # user_input is the dict containing all the json LD data
        self.user_input = LD.setup_linked_data_dict(self.model_id, self.model_name)

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

    def set_tabs(self):

        cell_parameters = LD.setup_sub_dict(type="cell")

        all_tab_display_names = db_helper.get_basis_tabs_display_names(self.model_name)

        all_tabs = st.tabs(all_tab_display_names)

        db_tab_ids = db_helper.get_db_tab_id(self.model_name)

        index = 0
        for tab in all_tabs:

            db_tab_id = db_tab_ids[index][0]


            tab_context_type= db_helper.get_context_type_and_iri_by_id(db_tab_id)
            tab_name = db_helper.get_tab_name_by_id(db_tab_id)

            tab_parameters = LD.setup_sub_dict(display_name=db_helper.get_basis_tabs_display_names(self.model_name)[index], context_type=tab_context_type, existence="new")

            tab_relation = LD.get_relation(db_tab_id, "tab")

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

                    category_parameters = LD.setup_sub_dict(display_name=db_helper.get_basis_categories_display_names(db_tab_id)[i][0],
                                                            context_type=db_helper.get_categories_context_type(db_tab_id)[i][0],
                                                            existence="new"
                                                            )
                    
                    category_id, category_name,_,_, category_context_type, category_context_type_iri, emmo_relation, category_display_name, _, default_template_id, _ = category

                    category_relation = LD.get_relation(category_id, "category")

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
            self.user_input = LD.fill_linked_data_dict(self.user_input, cell_parameters)

            index +=1
        self.update_json_LD()
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

    def calc_indicators(self,user_input):

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
        specific_capacity_am_ne = self.calc_specific_capacity_active_material(c_max_ne, densities["negative_electrode_active_material"], 
                                                                     li_stoich_max_ne, 
                                                                     li_stoich_min_ne,
                                                                     n)
        specific_capacity_am_pe = self.calc_specific_capacity_active_material(c_max_pe, densities["positive_electrode_active_material"], 
                                                                     li_stoich_max_pe, 
                                                                     li_stoich_min_pe,
                                                                     n)
        
        raw_template_am_ne = db_helper.get_template_parameter_by_parameter_name("specific_capacity")
        raw_template_am_pe = db_helper.get_template_parameter_by_parameter_name("specific_capacity")
        # specific_cap_am_ne_parameter = self.formatter.initialize_parameters(raw_template_am_ne)
        # specific_cap_am_ne_parameter["selected_value"] = specific_capacity_am_ne
        # specific_cap_am_pe_parameter = self.formatter.initialize_parameters(raw_template_am_pe)
        # specific_cap_am_pe_parameter["selected_value"] = specific_capacity_am_pe
        specific_capacities_category_parameters_am_ne = LD.setup_parameter_struct(raw_template_am_ne, value = specific_capacity_am_ne)  
        specific_capacities_category_parameters_am_pe = LD.setup_parameter_struct(raw_template_am_pe, value = specific_capacity_am_pe) 

        # Specific capacity electrodes
        specific_capacity_ne = self.calc_capacity_electrode(specific_capacity_am_ne, 
                                                                    mf_ne, 
                                                                    densities["negative_electrode"],
                                                                    volumes["negative_electrode"], 
                                                                    porosities["negative_electrode"])
        specific_capacity_pe = self.calc_capacity_electrode(specific_capacity_am_pe, 
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
        specific_capacities_category_parameters_ne= LD.setup_parameter_struct(raw_template_ne,value=specific_capacity_ne)  
        specific_capacities_category_parameters_pe= LD.setup_parameter_struct(raw_template_pe,value=specific_capacity_pe)  

        # N to P ratio
        n_to_p_ratio = self.calc_n_to_p_ratio(specific_capacities_electrodes)
        raw_template_np = db_helper.get_template_parameter_by_parameter_name("n_to_p_ratio")
        n_to_p_category_parameters= LD.setup_parameter_struct(raw_template_np, value=n_to_p_ratio)

        # Cell Mass
        cc_mass = volumes["current_collector"]* 8950
        cell_mass, ne_mass, pe_mass = self.calc_cell_mass(densities, porosities, volumes, cc_mass, packing_mass)
        raw_template_cellmass = db_helper.get_template_parameter_by_parameter_name("cell_mass")
        cell_mass_category_parameters= LD.setup_parameter_struct(raw_template_cellmass,value=cell_mass)

        # Cell Capacity
        masses = {
            "negative_electrode": ne_mass,
            "positive_electrode": pe_mass
        }
        cell_capacity = self.calc_cell_capacity(specific_capacities_electrodes)
        raw_template_cellcap = db_helper.get_template_parameter_by_parameter_name("nominal_cell_capacity")
        cell_capacity_category_parameters= LD.setup_parameter_struct(raw_template_cellcap,value=cell_capacity)

        # Include indicators in linked data input dict
        user_input = LD.add_indicators_to_struct(user_input,n_to_p_category_parameters,cell_mass_category_parameters,cell_capacity_category_parameters,specific_capacities_category_parameters_ne,specific_capacities_category_parameters_pe,specific_capacities_category_parameters_am_ne,specific_capacities_category_parameters_am_pe)
        
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

                

                material_formatted_parameters,formatted_materials, selected_value_id, component_parameters_, emmo_relation, density = self.fill_material_components(component_name,component_parameters,component_parameters_,material_comp_default_template_id,material_component_id,material_col,material_comp_display_name,material_comp_context_type_iri,material_component,category_parameters,density)

                component_parameters_ = LD.fill_component_dict(component_parameters_, "new")
                component_parameters = LD.setup_sub_dict(display_name=material_comp_display_name,context_type=material_comp_context_type, existence="new")
                component_parameters = LD.fill_component_dict(component_parameters=component_parameters_,existence="existing",dict=component_parameters)
                
                material_comp_relation = LD.get_relation(material_component_id,"component")
                category_parameters = LD.fill_sub_dict(category_parameters,material_comp_relation,component_parameters,"new",)
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
                    component_parameters_ = LD.fill_component_dict(component_parameters_, "new")
                    component_parameters = LD.setup_sub_dict(dict=component_parameters,display_name=material_comp_display_name,context_type=material_comp_context_type)
                    component_parameters = LD.fill_component_dict(component_parameters_, "existing",dict=component_parameters)
                    
                    material_comp_relation = LD.get_relation(material_component_id,"component")
                    
                    category_parameters = LD.fill_component_dict(component_parameters,"existing",dict=category_parameters,relation=material_comp_relation)
        else:
            mass_fraction_id_dict = None

        if mass_fraction_id_dict:    
            self.validate_volume_fraction(mass_fraction_id_dict, category_display_name,tab)
            density_mix = self.calc_density_mix(mass_fraction_id_dict, density) 

            try:
                with open(app_access.get_path_to_calculated_values(), 'r') as f:
                    parameters_dict = json.load(f)
            except json.JSONDecodeError as e:
                st.write(app_access.get_path_to_calculated_values())


            parameters_dict["calculatedParameters"]["effective_density"][category_name] = density_mix

            with open(app_access.get_path_to_calculated_values(),'w') as f:
                json.dump(parameters_dict,f, indent=3) 
        
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
        non_material_parameter,user_input,category_parameters, mass_loadings = self.fill_non_material_components(category_parameters,component_parameters,non_material_comp_display_name,non_material_comp_context_type, category_id,category_name,non_material_comp_default_template_id,non_material_component_id,property_col,value_col,non_material_parameters_sets,self.model_id, component_parameters_, check_col,non_material_component_name,tab, density_mix, mass_loadings)

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

                    st_space(tab)
                    name_col, input_col = tab.columns([1, 2])

                    if isinstance(parameter, NumericalParameter):
                    
                        name_col.write("[{}]({})".format(parameter.display_name, parameter.context_type_iri) + " /" + "[{}]({})".format(parameter.unit, parameter.unit_iri))

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

                component_parameters_ = LD.setup_parameter_struct(parameter,component_parameters=component_parameters_)

        parameter_details = {
                "label": "protocol_name",
                "value": {
                    "@type": "emmo:String",
                    "hasStringData": Protocol_name
                }
            }
        component_parameters_.append(parameter_details)
        component_parameters_ = LD.fill_component_dict(component_parameters_,"new")
        component_parameters = LD.setup_sub_dict(existence="new",display_name=non_material_comp_display_name,context_type=non_material_comp_context_type)
        component_parameters = LD.fill_component_dict(component_parameters_,"existing", dict=component_parameters)

        relation = LD.get_relation(non_material_component_id, "component")
        category_parameters = LD.fill_sub_dict(category_parameters,relation, component_parameters, "new")

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
                            format=parameter.format,
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
                    component_parameters_ = LD.setup_parameter_struct(parameter, component_parameters=component_parameters_)

                    if parameter.name == "density" and density:
                        density[material_component_id] = parameter.selected_value

            component_parameters_ = LD.fill_component_dict(component_parameters_,"new")

            component_parameters = LD.setup_sub_dict(existence="new",display_name=material_comp_display_name,context_type=material_comp_context_type)
            component_parameters = LD.fill_component_dict(component_parameters_,"existing",dict=component_parameters)

            material_comp_relation = LD.get_relation(material_component_id, "component")

            category_parameters = LD.fill_sub_dict(category_parameters, material_comp_relation, component_parameters,"new")

        return category_parameters
    
    def fill_non_material_components(self,category_parameters,component_parameters,non_material_comp_display_name,non_material_comp_context_type, category_id,category_name,non_material_comp_default_template_id,non_material_component_id,property_col,value_col,non_material_parameters_sets,model_id, component_parameters_, check_col,non_material_component_name,tab, density_mix, mass_loadings):
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
                                      args = (checkbox_key, tab, category_id, non_material_parameter.name,non_material_parameter),
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

                component_parameters_ = LD.setup_parameter_struct(non_material_parameter, component_parameters=component_parameters_)
                
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
                if par_index:
                    
                    component_parameters_ = LD.change_numerical_value(component_parameters_,par_index,st.session_state[input_value])
                    st.experimental_rerun

        component_parameters_ = LD.fill_component_dict(component_parameters_,"new")
        component_parameters = LD.setup_sub_dict(dict=component_parameters,display_name=non_material_comp_display_name,context_type=non_material_comp_context_type)
        component_parameters = LD.fill_component_dict(component_parameters_,"existing", dict=component_parameters)

        component_relation = LD.get_relation(non_material_component_id, "component")

        category_parameters = LD.fill_component_dict(component_parameters,"existing",dict=category_parameters,relation=component_relation)


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

    
    def fill_material_components(self,component_name,component_parameters,component_parameters_,material_comp_default_template_id,material_component_id,material_col,material_comp_display_name,material_comp_context_type_iri,material_component,category_parameters, density, emmo_relation = None):

        material_parameter_sets = []
        # get corresponding template parameters from db
        material_raw_template_parameters = db_helper.get_all_material_by_template_id(material_comp_default_template_id, self.model_name)

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
        
        if formatted_component:

            material_choice = formatted_component.options.get(selected_value_id)

            material_parameter_set_id = material_choice.parameter_set_id

            parameter_ids = material_choice.parameter_ids
            parameters = material_choice.parameters

            for parameter_id in parameters:

                parameter = parameters.get(parameter_id)

                set_parameter = parameter.options.get(material_parameter_set_id)
                parameter.set_selected_value(set_parameter.value)
                component_parameters_ = LD.setup_parameter_struct(parameter, component_parameters=component_parameters_)
                if parameter.name == "density" and density != None:
                    density[material_component_id] = set_parameter.value    

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
                            st_space(tab_advanced)
                            name_col, input_col = tab_advanced.columns(2)

                            if isinstance(parameter, NumericalParameter):
                                name_col.write("[{}]({})".format(parameter.display_name, parameter.context_type_iri) + " / " + "[{}]({})".format(parameter.unit, parameter.unit_iri))
                                
                                user_input = input_col.number_input(
                                    label=parameter.name,
                                    value=parameter.options.get(selected_parameter_id).value,
                                    min_value=parameter.min_value,
                                    max_value=parameter.max_value,
                                    key="input_{}_{}".format(non_material_component_name, parameter.name),
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

                            component_parameters_ = LD.setup_parameter_struct(parameter,component_parameters=component_parameters_)
                    component_parameters = LD.setup_sub_dict(display_name=non_material_comp_display_name, context_type=non_material_comp_context_type,existence="new")
                    component_parameters = LD.fill_component_dict(component_parameters_,existence="new", dict=component_parameters)
                    non_material_comp_relation = LD.get_relation(non_material_component_id, "component")
                    category_parameters = LD.fill_component_dict(component_parameters,"existing",dict=category_parameters,relation=non_material_comp_relation )


                
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
                    format=parameter.format,
                    step=parameter.increment,
                    label_visibility="collapsed"
                    )
                
                if parameter:
                    parameter.set_selected_value(user_input)

                    component_parameters = LD.setup_parameter_struct(parameter, component_parameters=component_parameters_) 

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
        self.set_buttons(save_run)

    def set_header(self,save_run):

        save_run.markdown("### " + self.header)
        save_run.text(" ")

    def set_buttons(self,save_run):

        #empty,run,empty2 = save_run.columns((0.3,1,1))

        # update = update.button(
        #     label="UPDATE",
        #     on_click=self.update_on_click,
        #     args= (save_run, )
        #     #help = "Update the parameter values."
        # )
        col1,_ = save_run.columns((1,3))
        runing = col1.button(
            label="RUN",
            on_click= self.execute_api_on_click,
            args = (save_run, ),
            type = "primary",
            use_container_width = True
            #help = "Run the simulation (after updating the parameters)."
            
        )

        
    def update_on_click(self):
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

            st.session_state.reponse = True

            with open(app_access.get_path_to_battmo_results(), "wb") as f:
                    f.write(response_start.content)

            success = DivergenceCheck(response_start).success

                

        else:
                st.session_state.reponse = False
                #success = DivergenceCheck(response_start.status_code).success
                
    
        
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
    def __init__(self,response):

        self.response = response
        self.success = False
        self.check_for_divergence()
        

    def check_for_divergence(self):

        if st.session_state.sim_finished:

            results = app_controller.get_results_data().get_results_data()

            N = self.get_timesteps_setting()
            number_of_states, log_messages = self.get_timesteps_execution(results)

            self.divergence_check_logging(N,number_of_states, log_messages)

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
    
    def divergence_check_logging(self,N, number_of_states,log_messages):
        save_run = st.empty()
        if st.session_state.reponse == False:
            st.error("The data has not been retrieved succesfully, most probably due to an unsuccesful simulation")
            
        else:
            if number_of_states == 0:
                self.success = False
                  
                st.session_state.succes = False
                if len(log_messages[()]) > 1:
                    c = save_run.container()
                    c.error("Simulation wasn't successful unfortunately. Some errors were produced, see the logging.")
                    c.markdown("***Logging:***")
                        
                    log_message = ''' \n'''
                    for message in log_messages[()]:
                        log_message = log_message + message+ '''\n'''
                    
                    c.code(log_message + ''' \n''')
                else:

                    save_run.error("Simulation wasn't successful unfortunately.")

            else: 
                self.success = True
                save_run.success("Simulation finished successfully! Check the results on the 'Results' page.")  
                st.session_state.succes = True

                if self.response:
                    with open(app_access.get_path_to_linked_data_input(), 'r') as f:
                        gui_parameters = json.load(f)

                    indicators = match_json_LD.get_indicators_from_gui_dict(gui_parameters)

                    with open(app_access.get_path_to_indicator_values(), 'w') as f:
                        json.dump(indicators, f, indent=3)

                    with open(app_access.get_path_to_battmo_results(), "wb") as f:
                        f.write(self.response.content)


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
            "3": image_open("separator_icon.png"),
            "1": image_open("plus_icon.png"),
            "0": image_open("minus_icon.png"),
            "2": image_open("electrolyte_icon.png"),
            "5": image_open("bc_icon.png"),
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
    def __init__(self):
        self.results = None
        self.get_results_data()

    def get_results_data(self):

        #results = self.retrieve_results()
        formatted_results = self.format_results()

        self.results = formatted_results
        return self.results

    def retrieve_results(self):

        with h5py.File(app_access.get_path_to_battmo_results(), "r") as f:
            result = f

        return result
    
    def format_results(self):

        results = h5py.File(app_access.get_path_to_battmo_results(), "r")

        # Retrieve the attributes
        number_of_states = results["number_of_states"][()]
        
        # Retrieve datasets
        log_messages = results["log_messages"].asstr()
        time_values = results["time_values"][:]
        cell_voltage = results["cell_voltage"][:]
        cell_current = results["cell_current"][:]
        negative_electrode_grid_bc = results["negative_electrode_grid_bc"][:]
        electrolyte_grid_bc = results["electrolyte_grid_bc"][:]
        positive_electrode_grid_bc = results["positive_electrode_grid_bc"][:]


        # Retrieve grid datasets
        negative_electrode_grid = np.squeeze(results["grids/negative_electrode_grid"][:])
        positive_electrode_grid = np.squeeze(results["grids/positive_electrode_grid"][:])
        electrolyte_grid = np.squeeze(results["grids/electrolyte_grid"][:])
        
        # Retrieve concentration datasets
        negative_electrode_concentration = [results["concentrations/negative_electrode_concentration_{}".format(i+1)][:] for i in range(number_of_states)]
        positive_electrode_concentration = [results["concentrations/positive_electrode_concentration_{}".format(i+1)][:] for i in range(number_of_states)]
        electrolyte_concentration = [results["concentrations/electrolyte_concentration_{}".format(i+1)][:] for i in range(number_of_states)]
        
        # Retrieve potential datasets
        negative_electrode_potential = [results["potentials/negative_electrode_potential_{}".format(i+1)][:] for i in range(number_of_states)]
        positive_electrode_potential = [results["potentials/positive_electrode_potential_{}".format(i+1)][:] for i in range(number_of_states)]
        electrolyte_potential = [results["potentials/electrolyte_potential_{}".format(i+1)][:] for i in range(number_of_states)]

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
        
        #self.style = get_theme_style()
        self.set_indicators()

    def set_indicators(self):

        if self.page_name == "Simulation":
            indicators= self.get_indicators_from_LD()
        else:
            indicators= self.get_indicators_from_run()

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
    
    def render_indicators(self,indicators):

        cell_mass = indicators["Cell"]["cellMass"]
        # cell_energy = indicators["Cell"]["cellEnergy"]
        cell_capacity = indicators["Cell"]["nominalCellCapacity"]
        n_to_p_ratio = indicators["Cell"]["NPRatio"]

        ne_mass_loading = indicators["NegativeElectrode"]["massLoading"]
        ne_thickness = indicators["NegativeElectrode"]["thickness"]
        ne_porosity = indicators["NegativeElectrode"]["porosity"]
        ne_specific_capacity = indicators["NegativeElectrode"]["specificCapacity"]
        ne_am_specific_capacity = indicators["NegativeElectrode"]["ActiveMaterial"]["specificCapacity"]
        pe_mass_loading = indicators["PositiveElectrode"]["massLoading"]
        pe_thickness = indicators["PositiveElectrode"]["thickness"]
        pe_porosity = indicators["PositiveElectrode"]["porosity"]
        pe_specific_capacity = indicators["PositiveElectrode"]["specificCapacity"]
        pe_am_specific_capacity = indicators["PositiveElectrode"]["ActiveMaterial"]["specificCapacity"]

        if self.page_name == "Simulation":
            col1, col2, col3, col4 = st.columns(4)
            col2.metric(
                label = "Cell Mass / {}".format(cell_mass["unit"]),
                value = int(np.round(cell_mass["value"])),
                label_visibility= "visible"
            )
            # col2.metric(
            #         label = "Energy ({})".format(cell_energy["unit"]),
            #         value = np.round(cell_energy["value"],2),
            #         label_visibility= "visible"
            #     )
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
            # col2.metric(
            #         label = "Energy ({})".format(cell_energy["unit"]),
            #         value = np.round(cell_energy["value"],2),
            #         label_visibility= "visible"
            #     )
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
            title="Electrolyte - Liquid phase lithium concentration",
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
            title="Positive Electrode - Solid phase lithium concentration",
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
            title="Negative Electrode - Solid phase lithium concentration",
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
        length_grid_elyte = len(_self.electrolyte_grid)
        length_grid_NE = len(_self.negative_electrode_grid)
        negative_electrode_concentration_ext = np.full(length_grid_elyte, np.nan)
        negative_electrode_concentration_ext[0:length_grid_NE] = np.squeeze(_self.negative_electrode_concentration)[state]
        ne_concentration = _self.create_subplot(
            x_data=_self.electrolyte_grid,
            y_data=negative_electrode_concentration_ext,
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
        elyte_concentration = _self.create_subplot(
            x_data=_self.electrolyte_grid,
            y_data=_self.electrolyte_concentration[state],
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
        length_grid_elyte = len(_self.electrolyte_grid)
        length_grid_PE = len(_self.positive_electrode_grid)
        positive_electrode_concentration_ext = np.full(length_grid_elyte, np.nan)
        positive_electrode_concentration_ext[-length_grid_PE:] = np.squeeze(_self.positive_electrode_concentration)[state]
        pe_concentration = _self.create_subplot(
            x_data=_self.electrolyte_grid,
            y_data=positive_electrode_concentration_ext,
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
        cell_current_fig = _self.create_subplot(
            x_data=_self.time_values,
            y_data=_self.cell_current,
            title="Cell Current  /  A",
            x_label="Time  /  h",
            y_label="Cell Current  /  A",
            vertical_line=_self.time_values[state]
        )

        # Negative Electrode Potential
        length_grid_elyte = len(_self.electrolyte_grid)
        length_grid_NE = len(_self.negative_electrode_grid)
        negative_electrode_potential_ext = np.full(length_grid_elyte, np.nan)
        negative_electrode_potential_ext[0:length_grid_NE] = np.squeeze(_self.negative_electrode_potential)[state]
        ne_potential = _self.create_subplot(
            x_data=_self.electrolyte_grid,
            y_data=negative_electrode_potential_ext,
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
        elyte_potential = _self.create_subplot(
            x_data=_self.electrolyte_grid,
            y_data=_self.electrolyte_potential[state],
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
        length_grid_elyte = len(_self.electrolyte_grid)
        length_grid_PE = len(_self.positive_electrode_grid)
        positive_electrode_potential_ext = np.full(length_grid_elyte, np.nan)
        positive_electrode_potential_ext[-length_grid_PE:] = _self.positive_electrode_potential[state]
        pe_potential = _self.create_subplot(
            x_data=_self.electrolyte_grid,
            y_data=positive_electrode_potential_ext,
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





