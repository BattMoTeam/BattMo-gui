
from PIL import Image
import pprint
import json
import pickle
import match_json
import streamlit as st
from app_parameter_model import *
from resources.db import db_helper, db_access
#from oct2py import Oct2Py
from copy import deepcopy
from uuid import uuid4
import sys
import requests
from flask_restful import Resource
import pdb
from jsonschema import validate, ValidationError
from streamlit_toggle_component.src.st_toggle_component import st_toggle_component
import sympy as sp


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
    Only used in the "About" tab, nothing important here, opened for complete modification.
    """
    def __init__(self, logo):
        self.logo = logo

        self.title = "BattMo"
        self.subtitle = "Framework for continuum modelling of electrochemical devices."
        self.description = """
            BattMo simulates the Current-Voltage response of a battery, using on Physics-based
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


class GetTabData:
    def __init__(self):

        self.basis_tabs = db_helper.all_basis_tab_display_names
        self.advanced_tabs = db_helper.all_advanced_tab_display_names

    def get_sql_data(self,model_id):

        print("nothing")

        # Get data relevent to chosen model


class SetBasisInputTabs:
    def __init__(self, images):

        self.image_dict = images

        #Initialize tabs
        self.title = "Parameters"
        self.set_title()
        self.set_basis_tabs()

    def set_title(self):
        st.markdown("### " + self.title)

    def set_basis_tabs(self):

        Electrodes, Electrolyte, Seperator, Protocol, BC = st.tabs(["Electrodes", "Electrolyte", "Seperator", "Protocol", "Boundary Conditions"])
        
        with Electrodes:
            image_collumn_electrodes,image2_collumn_electrodes, title_electrodes = st.columns([0.9,0.9,6])
            image_collumn_electrodes.image(self.image_dict['2'])
            image2_collumn_electrodes.image(self.image_dict['1'])
            with title_electrodes:
                st.text(" ")
                st.subheader("Electrodes")

            NE, PE = st.tabs(["Negative Electrode", "Positive Electrode"])
            with NE:
                parameter_NE_AM, selectbox_NE_AM, volumefraction_NE_AM = st.columns(3)
                parameter_NE_B, selectbox_NE_B, volumefraction_NE_B = st.columns(3)
                parameter_NE_Ad, selectbox_NE_Ad, volumefraction_NE_Ad = st.columns(3)

                with parameter_NE_AM:
                    st.markdown("###### "+ "Component")
                
                    st.markdown("Active Material")
                with selectbox_NE_AM:
                    st.markdown("###### "+ "Material")
                    NE_AM_choice = st.selectbox('Material', ('Graphite_Xu2015', 'Graphite_Safari2009', 'User Defined'), key = "NE_AM_choice",label_visibility="collapsed")
                with volumefraction_NE_AM:
                    st.markdown("###### "+ "Volume Fraction []")
                    volume_fraction_NE_AM = st.number_input(label = "Volume fraction",key = "volume fraction input NE AM", label_visibility="collapsed")
                if NE_AM_choice == 'User Defined':
                    NE_AM_exp = st.expander("Define active material parameters")
                    with NE_AM_exp:
                        st.write("parameter form")

                with parameter_NE_B:
                    st.markdown("Binder")
                with selectbox_NE_B:
                    NE_B_choice = st.selectbox('Material', ('PVDF', 'User Defined'), key = "NE_B_choice",label_visibility="collapsed")
                with volumefraction_NE_B:
                    volume_fraction_NE_B = st.number_input(label = "Volume fraction",key = "volume fraction input NE B", label_visibility="collapsed")
                if NE_B_choice == 'User Defined':
                    NE_B_exp = st.expander("Define binder parameters")
                    with NE_B_exp:
                        st.write("parameter form")
                with parameter_NE_Ad:
                    st.markdown("Additive")
                with selectbox_NE_Ad:
                    NE_Ad_choice = st.selectbox('Material', ('carbon_black', 'User Defined'), key = "NE_Ad_choice",label_visibility="collapsed")
                with volumefraction_NE_Ad:
                    volume_fraction_NE_Ad = st.number_input(label = "Volume fraction",key = "volume fraction input NE Ad", label_visibility="collapsed")
                if NE_Ad_choice == 'User Defined':
                    NE_Ad_exp = st.expander("Define additive parameters")
                    with NE_Ad_exp:
                        st.write("parameter form")

                    #Electrode_properties = st.tabs(["Electrode properties"])
                st.markdown("###### " + "Electrode properties")

                electrode_properties_NE, graphics_Electrodes_NE = st.columns([2,1])
                with graphics_Electrodes_NE:
                    st.markdown("Coating porosity []")
                with electrode_properties_NE:
                    parameter_Electrodes_porosity_NE, input_Electrodes_porosity_NE = st.columns(2)
                    with parameter_Electrodes_porosity_NE: 
                        st.markdown("Coating porosity []")
                    with input_Electrodes_porosity_NE: 
                        coating_porosity_NE = st.number_input(label = "Coating Porosity",key = "coating porosity input NE", label_visibility="collapsed")
                    parameter_Electrodes_mass_load_NE, input_Electrodes_mass_load_NE = st.columns(2)
                    with parameter_Electrodes_mass_load_NE: 
                        st.markdown("Mass loading []")
                    with input_Electrodes_mass_load_NE: 
                        mass_loading_NE = st.number_input(label = "Mass loading",key = "mass loading input NE", label_visibility="collapsed")
                    parameter_Electrodes_thickness_NE, input_Electrodes_thickness_NE = st.columns(2)
                    with parameter_Electrodes_thickness_NE: 
                        st.markdown("Coating thickness []")
                    with input_Electrodes_thickness_NE: 
                        coating_thickness_NE = st.number_input(label = "Coating thickness",key = "coating thickness input NE", label_visibility="collapsed")
            with PE:
                parameter_PE_AM, selectbox_PE_AM, volumefraction_PE_AM = st.columns(3)
                parameter_PE_B, selectbox_PE_B, volumefraction_PE_B = st.columns(3)
                parameter_PE_Ad, selectbox_PE_Ad, volumefraction_PE_Ad = st.columns(3)

                with parameter_PE_AM:
                    st.markdown("###### "+ "Component")
                    st.markdown("Active Material")
                with selectbox_PE_AM:
                    st.markdown("###### "+ "Material")
                    PE_AM_choice = st.selectbox('Material', ('Graphite_Xu2015', 'Graphite_Safari2009', 'User Defined'), key = "PE_AM_choice",label_visibility="collapsed")
                with volumefraction_PE_AM:
                    st.markdown("###### "+ "Volume Fraction []")
                    volume_fraction_PE_AM = st.number_input(label = "Volume fraction",key = "volume fraction input PE AM", label_visibility="collapsed")
                if PE_AM_choice == 'User Defined':
                    PE_AM_exp = st.expander("Define active material parameters")
                    with NE_AM_exp:
                        st.write("parameter form")

                with parameter_PE_B:
                    st.markdown("Binder")
                with selectbox_PE_B:
                    PE_B_choice = st.selectbox('Material', ('PVDF', 'User DefiPed'), key = "PE_B_choice",label_visibility="collapsed")
                with volumefraction_PE_B:
                    volume_fraction_PE_B = st.number_input(label = "Volume fraction",key = "volume fraction input PE B", label_visibility="collapsed")
                if PE_B_choice == 'User Defined':
                    PE_B_exp = st.expander("Define binder parameters")
                    with PE_B_exp:
                        st.write("parameter form")
                with parameter_PE_Ad:
                    st.markdown("Additive")
                with selectbox_PE_Ad:
                    PE_Ad_choice = st.selectbox('Material', ('carbon_black', 'User Defined'), key = "PE_Ad_choice",label_visibility="collapsed")
                with volumefraction_PE_Ad:
                    volume_fraction_PE_Ad = st.number_input(label = "Volume fraction",key = "volume fraction input PE Ad", label_visibility="collapsed")
                if PE_Ad_choice == 'User Defined':
                    PE_Ad_exp = st.expander("Define additive parameters")
                    with PE_Ad_exp:
                        st.write("parameter form")

                #Electrode_properties = st.tabs(["Electrode properties"])
                st.markdown("###### " + "Electrode properties")

                electrode_properties, graphics_Electrodes = st.columns([2,1])
                with graphics_Electrodes:
                    st.markdown("Coating porosity []")
                with electrode_properties:
                    parameter_Electrodes_porosity, input_Electrodes_porosity = st.columns(2)
                    with parameter_Electrodes_porosity: 
                        st.markdown("Coating porosity []")
                    with input_Electrodes_porosity: 
                        coating_porosity = st.number_input(label = "Coating Porosity",key = "coating porosity input", label_visibility="collapsed")
                    parameter_Electrodes_mass_load, input_Electrodes_mass_load = st.columns(2)
                    with parameter_Electrodes_mass_load: 
                        st.markdown("Mass loading []")
                    with input_Electrodes_mass_load: 
                        coating_porosity = st.number_input(label = "Mass loading",key = "mass loading input", label_visibility="collapsed")
                    parameter_Electrodes_thickness, input_Electrodes_thickness = st.columns(2)
                    with parameter_Electrodes_thickness: 
                        st.markdown("Coating thickness []")
                    with input_Electrodes_thickness: 
                        coating_porosity = st.number_input(label = "Coating thickness",key = "coating thickness input", label_visibility="collapsed")
            st.divider()
            
            n_to_p_parameter, empty, n_to_p_value_n, to, n_to_p_value_p, empty = st.columns([3,1.5,2.5,0.5,2.5,3])

            with n_to_p_parameter:
                st.markdown("N/P ratio")
            with n_to_p_value_n:
                n_to_p_n = st.number_input(label = "ntop_n", key = "ntop_n", value = 1.0, label_visibility="collapsed")
            with to:
                st.markdown(" / ")
            with n_to_p_value_p:
                n_to_p_p = st.number_input(label = "ntop_p", key = "ntop_p", value = 1.2, label_visibility="collapsed")

        st.divider()


def checkbox_input_connect(checkbox_key, tab, category_id, parameter_name,non_material_parameter):
        """
        Function needed for the checkboxes and number_inputs to work properly together.
        """
        print("session1= ", st.session_state[checkbox_key])

        #st.session_state[checkbox_key] = new_value
        state_count ="state_count_" + str(category_id)
        states = "states_" + str(category_id)
        
        if st.session_state[checkbox_key]==True:
            print("ok")
            st.session_state[state_count] += 1
            st.session_state[states][parameter_name] = True
            #st.experimental_rerun()

        elif st.session_state[checkbox_key]== False:
            st.session_state[state_count] -= 1
            st.session_state[states][parameter_name] = False
            #st.experimental_rerun()
        print("state_count=", st.session_state[state_count])
        if st.session_state[state_count] >2:
            st.session_state[checkbox_key] = False
            st.session_state[state_count] -= 1
            st.session_state[states][parameter_name] = False
            tab.warning("Only two of three parameters can be defined. The third one is calculated.")
            #st.experimental_rerun()

        elif st.session_state[state_count] < 2:
            tab.warning("Enable at least two of three parameters.")
        else:
            pass
            # if st.session_state[states]["coating_thickness"] and st.session_state[states]["coating_porosity"]:
            #     input_key = "input_key_{}_{}".format(category_id, "mass_loading")
            #     empty_key = "empty_{}_{}".format(category_id,"mass_loading") 
            #     input_value = "input_value_{}_{}".format(category_id, "mass_loading")

                
            #     user_input = st.session_state[empty_key].number_input(
            #         label=non_material_parameter.name,
            #         value=st.session_state[input_value],
            #         min_value=non_material_parameter.min_value,
            #         max_value=non_material_parameter.max_value,
            #         key=input_key,
            #         format=non_material_parameter.format,
            #         step=non_material_parameter.increment,
            #         label_visibility="collapsed",
            #         disabled = not st.session_state[checkbox_key]
            #         )   
                
                
            # elif st.session_state[states]["coating_thickness"] and st.session_state[states]["mass_loading"]:
            #     input_key = "input_key_{}_{}".format(category_id, "coating_porosity")
            #     empty_key = "empty_{}_{}".format(category_id,"coating_porosity") 
            #     input_value = "input_value_{}_{}".format(category_id, "coating_porosity")

            #     print("val=", st.session_state[input_value])
            #     user_input = st.session_state[empty_key].number_input(
            #         label=non_material_parameter.name,
            #         value=st.session_state[input_value],
            #         min_value=non_material_parameter.min_value,
            #         max_value=non_material_parameter.max_value,
            #         key=input_key,
            #         format=non_material_parameter.format,
            #         step=non_material_parameter.increment,
            #         label_visibility="collapsed",
            #         disabled = not st.session_state[checkbox_key]
            #         )
                


            # elif st.session_state[states]["mass_loading"] and st.session_state[states]["coating_porosity"]:
            #     input_key = "input_key_{}_{}".format(category_id, "coating_thickness")
            #     empty_key = "empty_{}_{}".format(category_id,"coating_thickness") 
            #     input_value = "input_value_{}_{}".format(category_id, "coating_thickness")

                
            #     user_input = st.session_state[empty_key].number_input(
            #         label=non_material_parameter.name,
            #         value=st.session_state[input_value],
            #         min_value=non_material_parameter.min_value,
            #         max_value=non_material_parameter.max_value,
            #         key=input_key,
            #         format=non_material_parameter.format,
            #         step=non_material_parameter.increment,
            #         label_visibility="collapsed",
            #         disabled = not st.session_state[checkbox_key]
            #         )
                

                   

def calc_mass_loading(density_mix, thickness, porosity):
        
        ml = thickness*density_mix*1000*(1-porosity)
        return ml
    
def calc_thickness( density_mix, mass_loading, porosity):
    th = mass_loading/(density_mix*1000*(1-porosity))
    return th

def calc_porosity( density_mix, thickness, mass_loading):
    por = 1-(mass_loading/(thickness*density_mix*1000))
    return por
    

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

        self.has_quantitative_property = "hasQuantitativeProperty"

        # Create info box
        self.info = "Push on the 'Save Parameters' button at the bottom of the page to update the parameters for the simulation."
        #self.set_info()

        # Initialize tabs
        self.title = "Parameters"
        self.set_title()
    

        # user_input is the dict containing all the json LD data
        self.user_input = {
            "@context": context,
            "battery:P2DModel": {
                "hasQuantitativeProperty": db_helper.get_model_parameters_as_dict(model_id)
            }
        }

        # Fill tabs
        self.set_tabs()
        #self.set_advanced_tabs()


    def set_info(self):
        st.info(self.info)

    def set_title(self):
        st.markdown("### " + self.title)

    def create_component_parameters_dict(self,component_parameters):
        return {self.has_quantitative_property: component_parameters}
    
    

    

    def validate_volume_fraction(self, vf_sum,category_display_name,tab):
        vf_summing = 0
        for id, value in vf_sum.items():
            vf_summing += value
        if vf_summing != 1.0:
            tab.warning("The sum of the '%s' material volume fractions is not equal to 1." % (category_display_name))
        

    def calc_density_mix(self, vf, density):
        print("dens=", density)
        print("vf=",vf)
        density_mix=0
        for id, weight in vf.items():
            print("id=", id)
            density_mix += weight*density.get(id)
        print(density_mix)
        return density_mix
    
    

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
        
        
        # if state[0]==True and state[1]==True and ac == 3:
        #     print("1")
        #     state[i]=False
        #     activated = False
        #     #tog_disabled = True
        # elif state[0]==False and state[1]==True and ac == 3:
        #     print("2")
            
        #     state[i]=True
        #     activated = True
        #     #tog_disabled = False
        # elif state[1]==True and state[2]==True and ac == 1:
        #     print("3")

        #     state[i]=False
        #     activated = False
        #     #tog_disabled = True
        # elif state[0]==True and state[2]==True and ac == 2:
        #     print("4")

        #     state[i]=False
        #     activated = False
        #     #tog_disabled = True
        # else:
        #     print("5")

        #     state[i]=True
        #     activated = True
        #     #tog_disabled = False

        # if check_col != None:
            
        #     tog = check_col.toggle(
        #         label ="Activate",
        #         value = state[i],
        #         key = "toggle_{}_{}".format(category_id, non_material_parameter.id),
        #         label_visibility="collapsed",
        #         disabled = False
        #         )

        #     check_col.text(" ")
        #     if tog:
        #         disabled = False
        #         state[i]=True
                
                
        #     else:
        #         disabled = True
        #         state[i]=False
        #     print("i=",i)
        #     print("state=", state)

        #     if state[0]==True and state[1]==True and ac == 3:
        #         print("1")
        #         state[i]=False
        #         activated = False
        #         #tog_disabled = True
        #     elif state[0]==False and state[1]==True and ac == 3:
        #         state[i]=True
        #         activated = True
        #         #tog_disabled = False
        #     elif state[1]==True and state[2]==True and ac == 1:
        #         print("2")

        #         state[i]=False
        #         activated = False
        #         #tog_disabled = True
        #     elif state[0]==True and state[2]==True and ac == 2:
        #         print("3")

        #         state[i]=False
        #         activated = False
        #         #tog_disabled = True
        #     else:
        #         print("4")

        #         state[i]=True
        #         activated = True
        # else:
        #     disabled = False
        
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
                        

                    #template_name = self.model_templates.get(category_name)
                    #template_id = db_helper.sql_template.get_id_from_name(template_name) if template_name else default_template_id

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
                        # parameter_sets_name_by_id = {}
                        # for id, name, _,_,_ in non_material_parameters_sets:
                        #     parameter_sets_name_by_id[id] = name




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
                                "@type": parameter.context_type_iri if parameter.context_type_iri else "None",
                                "value": formatted_value_dict
                            }
                            if isinstance(parameter, NumericalParameter):
                                parameter_details["unit"] = "emmo:"+parameter.unit_name if parameter.unit_name else parameter.unit
                            component_parameters.append(parameter_details)

                    # component_parameters = self.create_component_parameters_dict(component_parameters)       

                    # component_parameters["label"] = non_material_comp_display_name
                    # component_parameters["@type"] = non_material_comp_context_type_iri

                        category_parameters[category_context_type][self.has_quantitative_property] += component_parameters

    
    
        return category_parameters

                    # else:
                    #     tab_advanced_pe.write("component = {} doesn't obtain any advanced parameters".format(non_material_component_name))
                    #     print("component = {} doesn't obtain any advanced parameters".format(non_material_component_name))
                            #category_parameters.append(parameter_details)
                    

    def set_ne_advanced_tabs(self, tab, category_display_name,category_parameters):
        
        advanced_ne_input=tab.expander("Show '{}' advanced parameters".format(category_display_name))
        all_advanced_tabs = advanced_ne_input.tabs(db_helper.get_ne_advanced_tab_display_names(self.model_id))
        db_tab_ids_advanced = db_helper.get_ne_advanced_db_tab_id(self.model_id)
        index_advanced = 0
        for tab_advanced in all_advanced_tabs:
            #tab_index_advanced = db_helper.get_tab_index_from_st_tab(tab_advanced)
            db_tab_id_advanced = db_tab_ids_advanced[index_advanced][0]
            
            print("id=", db_tab_id_advanced)

            tab_context_type, tab_context_type_iri = db_helper.get_context_type_and_iri_by_id(db_tab_id_advanced)
            tab_parameters = {
                "label": db_helper.get_advanced_tabs_display_names(self.model_id)[index_advanced],
                "@type": tab_context_type_iri
            }
                # get tab's categories
            categories_advanced = db_helper.get_advanced_categories_from_tab_id(db_tab_id_advanced)
            print("categories=", categories_advanced)

            if len(categories_advanced) > 1:  # create one sub tab per category

                all_category_display_names = [a[8] for a in categories_advanced]
                all_sub_tabs = tab_advanced.tabs(all_category_display_names)
                i = 0

                for category in categories_advanced:
                    component_parameters = []
                    category_id, category_name,_,_,_, category_context_type, category_context_type_iri, emmo_relation, category_display_name, _, default_template_id, _ = category

                    
                    tab_advanced = all_sub_tabs[i]

                    
                    i += 1

                    print("cat_name=",category_name)
                    print("id=",category_id)
                    non_material_component = tuple(db_helper.get_advanced_components_from_category_id(category_id))     
                    print("comp=",non_material_component)

                    non_material_component_id, non_material_component_name, _,_,_,_,_,non_material_comp_display_name,_,_,_,non_material_comp_default_template_id,non_material_comp_context_type,non_material_comp_context_type_iri,_ = non_material_component
                        
                    print("def_id=",non_material_component_name)
                    #template_name = self.model_templates.get(category_name)
                    #template_id = db_helper.sql_template.get_id_from_name(template_name) if template_name else default_template_id

                    raw_template_parameters = db_helper.get_advanced_template_by_template_id(default_template_id)
                    print(raw_template_parameters)

                    if raw_template_parameters:
                        print(".........")
                        non_material_parameters_sets = np.squeeze(db_helper.get_non_material_set_id_by_component_id(non_material_component_id))
                        non_material_parameter_set_id, non_material_parameters_set_name, _ ,_,_ = non_material_parameters_sets
                        
                        non_material_parameters_raw = []
                        for non_material_parameter_raw_template in raw_template_parameters:

                            non_material_parameter_id,name,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_ = non_material_parameter_raw_template
                            print("name =", name)
                            print("name =", non_material_parameters_set_name)
                        
                            non_material_parameter = db_helper.get_advanced_parameters_by_parameter_set_id(non_material_parameter_id, non_material_parameter_set_id)
                            print("par=",raw_template_parameters)
                            non_material_parameters_raw.append(non_material_parameter)
                            

                        
                        non_material_parameters_raw = tuple(np.squeeze(non_material_parameters_raw))
                        # parameter_sets_name_by_id = {}
                        # for id, name, _,_,_ in non_material_parameters_sets:
                        #     parameter_sets_name_by_id[id] = name




                        formatted_parameters = self.formatter.format_parameters(non_material_parameters_raw, raw_template_parameters, non_material_parameters_set_name)
                        print(formatted_parameters)
                        
                        for parameter_id in formatted_parameters:
                            print(parameter_id)
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
                                "@type": parameter.context_type_iri if parameter.context_type_iri else "None",
                                "value": formatted_value_dict
                            }
                            if isinstance(parameter, NumericalParameter):
                                parameter_details["unit"] = "emmo:"+parameter.unit_name if parameter.unit_name else parameter.unit
                            component_parameters.append(parameter_details)

                    #component_parameters = self.create_component_parameters_dict(component_parameters)    

                    #component_parameters["label"] = non_material_comp_display_name
                    #component_parameters["@type"] = non_material_comp_context_type_iri

                    category_parameters[category_context_type][self.has_quantitative_property] += component_parameters
                
                
                #pdb.set_trace()
                
                return category_parameters
                    # else:
                    #     tab_advanced.write("component = {} doesn't obtain any advanced parameters".format(non_material_component_name))
                    #     print("component = {} doesn't obtain any advanced parameters".format(non_material_component_name))
                            #category_parameters.append(parameter_details)
            # else:
            
            #     category_id, category_name,_,_,_, category_context_type, category_context_type_iri, emmo_relation, category_display_name, _, default_template_id, _= categories_advanced[0]

            #     # get tab's categories
            #     categories = db_helper.get_basis_categories_from_tab_id(db_tab_id_advanced)

                

            #     non_material_component = db_helper.get_non_material_components_from_category_id(category_id)      

            #     non_material_component_id, non_material_component_name, _,_,_,_,_,non_material_comp_display_name,_,_,_,non_material_comp_default_template_id,non_material_comp_context_type,non_material_comp_context_type_iri,_ = non_material_component
                    

            #     #template_name = self.model_templates.get(category_name)
            #     #template_id = db_helper.sql_template.get_id_from_name(template_name) if template_name else default_template_id

            #     raw_template_parameters = db_helper.get_advanced_template_by_template_id(default_template_id)

            #     if raw_template_parameters:
            #         non_material_parameters_sets = db_helper.get_non_material_set_id_by_component_id(non_material_component_id)
            #         non_material_parameter_set_id, non_material_parameters_set_name, _ ,_,_ = non_material_parameters_sets[0]
                    
            #         non_material_parameters_raw = []
            #         for non_material_parameter_raw_template in raw_template_parameters:

            #             non_material_parameter_id,name,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_ = non_material_parameter_raw_template

            #             non_material_parameter = db_helper.get_advanced_parameters_by_parameter_set_id(non_material_parameter_id, non_material_parameter_set_id)[0]
                        
            #             non_material_parameters_raw.append(non_material_parameter)
                    
            #         parameter_sets_name_by_id = {}
            #         for id, name, _,_,_ in non_material_parameters_sets:
            #             parameter_sets_name_by_id[id] = name




            #         formatted_parameters = self.formatter.format_parameters(non_material_parameters_raw, raw_template_parameters, parameter_sets_name_by_id)

            #         for parameter_id in formatted_parameters:
            #             parameter = formatted_parameters.get(parameter_id)
            #             if parameter.is_shown_to_user:
            #                 selected_parameter_id = db_helper.get_parameter_id_from_template_parameter_and_parameter_set(
            #                     template_parameter_id=parameter.id,
            #                     parameter_set_id=non_material_parameter_set_id
            #                 )
            #                 st_space(tab)
            #                 name_col, input_col = tab.columns([1, 2])

            #                 if isinstance(parameter, NumericalParameter):
            #                     name_col.write("[{}]({})".format(parameter.display_name, parameter.context_type_iri) + " (" + "[{}]({})".format(parameter.unit, parameter.unit_iri) + ")")

            #                     user_input = input_col.number_input(
            #                         label=parameter.name,
            #                         value=parameter.options.get(selected_parameter_id).value,
            #                         min_value=parameter.min_value,
            #                         max_value=parameter.max_value,
            #                         key="input_{}_{}".format(non_material_component_id, parameter_id),
            #                         format=parameter.format,
            #                         step=parameter.increment,
            #                         label_visibility="collapsed"
            #                     )
            #                 else:
            #                     name_col.write(parameter.display_name)
            #                     user_input = input_col.selectbox(
            #                         label=parameter.display_name,
            #                         options=[parameter.options.get(selected_parameter_id).value],
            #                         key="input_{}_{}".format(non_material_component_id, parameter_id),
            #                         label_visibility="collapsed",
            #                     )
            #                 parameter.set_selected_value(user_input)

            #             formatted_value_dict = parameter.selected_value

            #             if isinstance(parameter, NumericalParameter):
            #                 formatted_value_dict = {
            #                     "@type": "emmo:Numerical",
            #                     "hasNumericalData": parameter.selected_value
            #                 }

            #             elif isinstance(parameter, StrParameter):
            #                 formatted_value_dict = {
            #                     "@type": "emmo:String",
            #                     "hasStringData": parameter.selected_value
            #                 }

            #             elif isinstance(parameter, BooleanParameter):
            #                 formatted_value_dict = {
            #                     "@type": "emmo:Boolean",
            #                     "hasStringData": parameter.selected_value
            #                 }

            #             parameter_details = {
            #                 "label": parameter.name,
            #                 "@type": parameter.context_type_iri if parameter.context_type_iri else "None",
            #                 "value": formatted_value_dict
            #             }
            #             if isinstance(parameter, NumericalParameter):
            #                 parameter_details["unit"] = "emmo:"+parameter.unit_name if parameter.unit_name else parameter.unit

            #             index_advanced += 1
            #     else:
            #             st.write("component = {} doesn't obtain any advanced parameters".format(non_material_component_name))
            #             print("component = {} doesn't obtain any advanced parameters".format(non_material_component_name))
            #             #category_parameters.append(parameter_details)
                    

    def set_tabs(self):

        all_tabs = st.tabs(db_helper.get_basis_tabs_display_names(self.model_id))
        #all_tab_names = db_helper.get_basis_tab_names(self.model_id)
        db_tab_ids = db_helper.get_db_tab_id(self.model_id)
        index = 0
        for tab in all_tabs:
            #tab_index = db_helper.get_tab_index_from_st_tab(tab)
            db_tab_id = db_tab_ids[index][0]


            tab_context_type, tab_context_type_iri = db_helper.get_context_type_and_iri_by_id(db_tab_id)
            
            tab_parameters = {
                "label": db_helper.get_basis_tabs_display_names(self.model_id)[index],
                "@type": tab_context_type_iri
            }

        

            # logo and title
            self.set_logo_and_title(tab, index)
            

            # get tab's categories
            categories = db_helper.get_basis_categories_from_tab_id(db_tab_id)

            
            
            
            #category_parameters = []
            if len(categories) > 1:  # create one sub tab per category

                all_category_display_names = [a[8] for a in categories]
                all_sub_tabs = tab.tabs(all_category_display_names)
                i = 0
                mass_loadings = {}

                for category in categories:
                    category_id, category_name,_,_,_, category_context_type, category_context_type_iri, emmo_relation, category_display_name, _, default_template_id, _ = category
                    state_count= "state_count_" + str(category_id)
                    states = "states_" + str(category_id)
                    

                    if state_count not in st.session_state:
                        st.session_state[state_count] = 0

                    if states not in st.session_state:
                        st.session_state[states] = {"coating_thickness": False, "coating_porosity": False, "mass_loading": False}

                 
                    


                for category in categories:

                    category_parameters = {
                        "label": db_helper.get_basis_categories_display_names(db_tab_id)[i],
                        "@type": db_helper.get_categories_context_type_iri(db_tab_id)[i]
                    }

                    
                    category_id, category_name,_,_,_, category_context_type, category_context_type_iri, emmo_relation, category_display_name, _, default_template_id, _ = category

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
                    
                    
                    # category_parameters["label"] = category_display_name
                    # category_parameters["@type"] = category_context_type_iri

                    if emmo_relation is None:
                        tab_parameters[category_context_type] = category_parameters

                        

                    else:
                        # emmo relations are used to define the json ld structure.
                        # This can be changed, nothing important here, it's just the json file rendering.
                        tab_parameters[emmo_relation] = [category_parameters]

                    
                    

                with tab:
                    
                    st.divider()


                    category_parameters, emmo_relation = self.fill_electrode_tab_comp( db_tab_id ,mass_loadings,category_id,emmo_relation = None)


                    
                    tab_display_name = db_helper.get_tabs_display_name_from_id(db_tab_id)
                    

                    if emmo_relation is None:
                        tab_parameters[tab_context_type] = category_parameters

                    else:
                        # emmo relations are used to define the json ld structure.
                        # This can be changed, nothing important here, it's just the json file rendering.
                        tab_parameters[emmo_relation] = [category_parameters]

                    

                    all_parameters = {
                        tab_context_type: tab_parameters
                    }
                    #tab_parameters["Electrode"]["Electrode"] = category_parameters


                    
                   

                    

            else:  # no sub tab is needed

                category_parameters = {
                        "label": db_helper.get_basis_categories_display_names(db_tab_id),
                        "@type": db_helper.get_categories_context_type_iri(db_tab_id)
                    }
                
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
                    # category_parameters["label"] = category_display_name
                    # category_parameters["@type"] = category_context_type_iri

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
                    
                    
                    # category_parameters["label"] = category_display_name
                    # category_parameters["@type"] = category_context_type_iri

                tab_parameters[category_context_type] = category_parameters

                

                all_parameters = {
                            tab_context_type: tab_parameters
                        }
            
            
            

            # tab is fully defined, its parameters are saved in the user_input dict
            self.user_input[tab_context_type] = all_parameters

            index +=1

        st.divider()

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
        print("vf_temp=", volume_fraction_raw_template)  
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
                        "hasNumericalData": vf_parameter.selected_value
                    }

                elif isinstance(vf_parameter, StrParameter):
                    formatted_value_dict = {
                        "@type": "emmo:String",
                        "hasStringData": vf_parameter.selected_value
                    }

                elif isinstance(vf_parameter, BooleanParameter):
                    formatted_value_dict = {
                        "@type": "emmo:Boolean",
                        "hasStringData": vf_parameter.selected_value
                    }

                elif isinstance(vf_parameter, FunctionParameter):
                    formatted_value_dict = {
                        "@type": "emmo:Function",
                        "hasStringData": vf_parameter.selected_value
                    }

                parameter_details = {
                    "label": vf_parameter.name,
                    "@type": vf_parameter.context_type_iri if vf_parameter.context_type_iri else "None",
                    "value": formatted_value_dict
                }
                if isinstance(vf_parameter, NumericalParameter):
                    parameter_details["unit"] = "emmo:"+vf_parameter.unit_name if vf_parameter.unit_name else vf_parameter.unit

                component_parameters.append(parameter_details)
                vf_sum[material_component_id] = vf_parameter.selected_value 
        
        return vf_parameter, user_input, component_parameters, emmo_relation, vf_sum
            
    def fill_material_column(self,component_name,material_comp_default_template_id,material_component_id,material_col,material_comp_display_name,material_comp_context_type_iri,material_component,category_parameters, density, emmo_relation = None):
        
        component_parameters = []
        # get corresponding template parameters from db
        material_raw_template_parameters = db_helper.get_all_material_by_template_id(material_comp_default_template_id)

        materials = tuple(db_helper.get_material_from_component_id(material_component_id))
        # get parameter sets corresponding to component, then parameters from each set
        material_parameter_sets = tuple(db_helper.get_all_material_by_component_id(material_component_id))

        
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
        
        #print("options=",formatted_materials.options


        selected_value_id = material_col.selectbox(
            label="[{}]({})".format(formatted_component.name, formatted_component.context_type_iri),
            options=formatted_component.options,
            key="select_{}".format(material_component_id),
            label_visibility="collapsed",
            format_func=lambda x: formatted_component.options.get(x).display_name,
            # on_change=reset_func,
            # args=(material_component_id, material_parameter_set_id, formatted_component)
        )

        print("comp_name2=", component_name)

        
       
        if formatted_component:
            material_choice = formatted_component.options.get(selected_value_id)

            material_parameter_set_id = material_choice.parameter_set_id

            parameter_ids = material_choice.parameter_ids
            parameters = material_choice.parameters

            
            for parameter_id in parameters:
                #print(parameter_id)
                #print(material_formatted_parameters.get(str(i)))
                #material_par = material_formatted_parameters.get(str(i))
                # print(material_par)
                # parameter = material_par.options.get(parameter_id)
                # i +=1
                
                
                parameter = parameters.get(parameter_id)
                #print(parameters_sets)
                #parameter = parameters_sets.options.get(material_parameter_set_id)
                #if np.ndim(parameter.options) > 1:
                set_parameter = parameter.options.get(material_parameter_set_id)

                # else:
                #     print("set_id2=", material_parameter_set_id)
                    #set_parameter = parameter.options
                #value = parameter.value

                #parameter.set_selected_value(value)
                formatted_value_dict = set_parameter.value
                if isinstance(parameter, NumericalParameter):
                    formatted_value_dict = {
                        "@type": "emmo:Numerical",
                        "hasNumericalData": set_parameter.value
                    }

                elif isinstance(parameter, StrParameter):
                    formatted_value_dict = {
                        "@type": "emmo:String",
                        "hasStringData": set_parameter.value
                    }

                elif isinstance(parameter, BooleanParameter):
                    formatted_value_dict = {
                        "@type": "emmo:Boolean",
                        "hasStringData": set_parameter.value
                    }

                # elif isinstance(parameter, FunctionParameter):
                #     formatted_value_dict = {
                #         "@type": "emmo:Function",
                #         "hasStringData": parameter.value
                #     }

                parameter_details = {
                    "label": parameter.name,
                    "@type": parameter.context_type_iri if parameter.context_type_iri else "None",
                    "value": formatted_value_dict
                }
                if isinstance(parameter, NumericalParameter):
                    parameter_details["unit"] = "emmo:"+parameter.unit_name if parameter.unit_name else parameter.unit

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
        
        
        

        def custom_toggle(labels,id, values, key,quantity, limit, on_change, args):
            
            

            if type(values) == dict:
                states = values
                values = []
                for label,value in states.items():
                    values.append(value)

                print("args1=", values)
            return st_toggle_component(labels=labels,id =id, initial_values= values, key = key, quantity=quantity,limit=limit, on_change = on_change, args= args)
        
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

            #if non_material_parameter_name == "mass_loading":

            if checkbox_key not in st.session_state:
                    st.session_state[checkbox_key] = False
            # else: 
            #     if checkbox_key not in st.session_state:
            #         st.session_state[checkbox_key] = True


            if input_value not in st.session_state:
                st.session_state[input_value] = None

            # if empty_key not in st.session_state:
            #     with value_col:
            #         st.session_state[empty_key] = st.empty()
                


            if state_key not in st.session_state:
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

            


            if check_col:
                with value_col:
                    if i == 0:
                        co_th_place = st.empty()
                    elif i == 1:
                        co_po_place = st.empty()
                    elif i == 2:
                        ml_place = st.empty()

                    
                print("key=", checkbox_key)

               
                with check_col:
                    state = st.toggle(label = checkbox_key, 
                                      key = checkbox_key, 
                                      value= st.session_state[checkbox_key], 
                                      on_change = checkbox_input_connect,
                                      args = (checkbox_key, tab, category_id, non_material_parameter.name,non_material_parameter),
                                      label_visibility="collapsed")
                    st.text(" ")  
                    print("staet=",state)
                    print("session2=", st.session_state[checkbox_key])
                    


            property_col.write("[{}]({})".format(non_material_parameter.display_name, non_material_parameter.context_type_iri)+ " (" + "[{}]({})".format(non_material_parameter.unit, non_material_parameter.unit_iri) + ")")

            property_col.text(" ")
            
            
            print("check =", st.session_state[state_key][non_material_parameter_id])
                
           


            if not st.session_state[input_value]:
                st.session_state[input_value] = non_material_parameter.default_value

                
            else:
                pass
                #user_input = st.session_state[input_value]
            
             
                
                    
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
                        "hasNumericalData": non_material_parameter.selected_value
                    }

                elif isinstance(non_material_parameter, StrParameter):
                    formatted_value_dict = {
                        "@type": "emmo:String",
                        "hasStringData": non_material_parameter.selected_value
                    }

                elif isinstance(non_material_parameter, BooleanParameter):
                    formatted_value_dict = {
                        "@type": "emmo:Boolean",
                        "hasStringData": non_material_parameter.selected_value
                    }
                
                # elif isinstance(non_material_parameter, FunctionParameter):
                #     formatted_value_dict = {
                #         "@type": "emmo:Function",
                #         "hasStringData": non_material_parameter.selected_value
                #     }

                

                parameter_details = {
                    "label": non_material_parameter.name,
                    "@type": non_material_parameter.context_type_iri if non_material_parameter.context_type_iri else "None",
                    "value": formatted_value_dict
                }
                if isinstance(non_material_parameter, NumericalParameter):
                    parameter_details["unit"] = "emmo:"+non_material_parameter.unit_name if non_material_parameter.unit_name else non_material_parameter.unit

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
            


            print("comp1= ", st.session_state[states])
            if st.session_state[states]["coating_thickness"] and st.session_state[states]["coating_porosity"]:
                for non_material_parameter_id in formatted_non_material_parameters:
                    non_material_parameter = formatted_non_material_parameters.get(non_material_parameter_id)
                    non_material_parameter_name = non_material_parameter.name
                    if non_material_parameter_name == "mass_loading":
                        par_value_ml = calc_mass_loading(density_mix, thickness, porosity)
                        par_index = 2
                        #print("par_value=", par_value)
                        mass_loadings[category_name]=par_value_ml
                        input_key = "input_key_{}_{}".format(category_id, "mass_loading")
                        empty_key = "empty_{}_{}".format(category_id,"mass_loading") 
                        input_value = "input_value_{}_{}".format(category_id, "mass_loading")
                        checkbox_key= "checkbox_{}_{}".format(category_id, "mass_loading")

                        st.session_state[input_value] = par_value_ml
                        tab.write("Mass loading has now a value of {}".format(par_value_ml))

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
                        par_value_co = calc_porosity(density_mix, thickness, mass_loading)
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
                    
                        tab.write("Coating porosity has now a value of {}".format(par_value_co))
                    


            elif st.session_state[states]["mass_loading"] and st.session_state[states]["coating_porosity"]:
                for non_material_parameter_id in formatted_non_material_parameters:
                    non_material_parameter = formatted_non_material_parameters.get(non_material_parameter_id)
                    non_material_parameter_name = non_material_parameter.name
                    if non_material_parameter_name == "coating_thickness":
                        par_value_th = calc_thickness(density_mix, mass_loading, porosity)
                        
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
                        tab.write("Coating thickness has now a value of {}".format(par_value_th))
                        


            else:
                st.session_state["input_value_{}_{}".format(category_id, "coating_thickness")] = None
                st.session_state["input_value_{}_{}".format(category_id, "coating_porosity")] = None
                st.session_state["input_value_{}_{}".format(category_id, "mass_loading")] = None
                st.experimental_rerun


            if st.session_state[input_value]:
                component_parameters[par_index]["value"]["hasNumericalData"]=st.session_state[input_value]
                st.experimental_rerun

        return non_material_parameter,user_input, {self.has_quantitative_property: component_parameters}, mass_loadings
    
    def fill_electrode_tab_comp(self, db_tab_id,mass_loadings,category_id ,emmo_relation):

        category_parameters = []
        n_to_p_parameter_col, empty, n_to_p_value_n, to, n_to_p_value_p, empty = st.columns([3,1,1.5,0.5,3,7])

        
        to.markdown("### " + "/")
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

        mass_loadings = [mass_load_n, mass_load_p] 
        mass_loadings = np.divide(mass_loadings,mass_load_n)
        mass_load = "mass_load_"+ str(category_id)
        

        #ratio = mass_loadings["negative_electrode"]/mass_loadings["positive_electrode"]

        


        

        columns = (n_to_p_value_n, n_to_p_value_p)
        ind = 0
        for parameter_id in formatted_n_to_p_parameters:
            n_to_p_parameter = formatted_n_to_p_parameters.get(parameter_id)
            input_key = "input_{}_{}".format(db_tab_id, n_to_p_parameter.id)
            column = columns[ind]
            st.session_state[input_key] = mass_loadings[ind]

            #mass_load = mass_loadings[ind]
            #st.write(mass_load)
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

            # user_input = column.number_input(
            #     label=n_to_p_parameter.name,
            #     value=st.session_state[input_key],
            #     min_value=n_to_p_parameter.min_value,
            #     max_value=n_to_p_parameter.max_value,
            #     key=input_key,
            #     format=n_to_p_parameter.format,
            #     step=n_to_p_parameter.increment,
            #     label_visibility="collapsed",
            #     disabled = True
            #     )
            ind += 1

            #n_to_p_parameter.set_selected_value(user_input)
            n_to_p_parameter.set_selected_value(st.session_state[input_key])
            formatted_value_dict = n_to_p_parameter.selected_value

            if isinstance(n_to_p_parameter, NumericalParameter):
                formatted_value_dict = {
                    "@type": "emmo:Numerical",
                    "hasNumericalData": n_to_p_parameter.selected_value
                }

            elif isinstance(n_to_p_parameter, StrParameter):
                formatted_value_dict = {
                    "@type": "emmo:String",
                    "hasStringData": n_to_p_parameter.selected_value
                }

            elif isinstance(n_to_p_parameter, BooleanParameter):
                formatted_value_dict = {
                    "@type": "emmo:Boolean",
                    "hasStringData": n_to_p_parameter.selected_value
                }

            # elif isinstance(n_to_p_parameter, FunctionParameter):
            #     formatted_value_dict = {
            #         "@type": "emmo:Function",
            #         "hasStringData": n_to_p_parameter.selected_value
            #     }

            parameter_details = {
                "label": n_to_p_parameter.name,
                "@type": n_to_p_parameter.context_type_iri if n_to_p_parameter.context_type_iri else "None",
                "value": formatted_value_dict
            }
            

            if isinstance(n_to_p_parameter, NumericalParameter):
                parameter_details["unit"] = "emmo:"+n_to_p_parameter.unit_name if n_to_p_parameter.unit_name else n_to_p_parameter.unit

            category_parameters.append(parameter_details)
        return {self.has_quantitative_property: category_parameters}, emmo_relation
        

    def fill_category(self, category_id, category_display_name,category_name, emmo_relation, default_template_id, tab, category_parameters,mass_loadings,selected_am_value_id=None):

        

        # get components associated with material parameter sets
        
        material_components = db_helper.get_material_components_from_category_id(category_id)
        
        
        if category_name == "negative_electrode" or category_name == "positive_electrode":
            
            # define streamlit columns
            #st_space(tab,space_width=2)
            component_col, material_col, vf_col = tab.columns(3)
            component_col.markdown("**Component**")
            material_col.markdown("**Material**")
            #vf_col.text("Volume Fraction []")
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
                
                
                print("comp_name1=", component_name)
                
                component_col.write("[{}]({})".format(material_comp_display_name, material_comp_context_type_iri))
                component_col.text(" ")
                
            
                material_formatted_parameters,formatted_materials, selected_value_id, component_parameter_mat, emmo_relation, density = self.fill_material_column(component_name,material_comp_default_template_id,material_component_id,material_col,material_comp_display_name,material_comp_context_type_iri,material_component,category_parameters,density)
                   

                component_parameters.extend(component_parameter_mat)


                
                component_parameters = self.create_component_parameters_dict(component_parameters)
                

                component_parameters["label"] = material_comp_display_name
                component_parameters["@type"] = material_comp_context_type_iri

                print("comp1 =", component_parameters)

                category_parameters[material_comp_context_type] = component_parameters


                material_choice = formatted_materials.options.get(selected_value_id).display_name
                print("mat_opt=", material_choice)
                material = formatted_materials.options.get(selected_value_id)
                parameters = material.parameters
                
                
                if material_choice == "User Defined":

                    component_parameters = []
                    ex = tab.expander("Fill in '%s' parameters" % material_comp_display_name)
                        
                    with ex:
                        for parameter_id in parameters:
                            parameter = parameters.get(parameter_id)
                            parameter_options =parameter.options.get(selected_value_id)
                            print(parameter)

                            if not isinstance(parameter, FunctionParameter):
                                property_col, value_col= ex.columns((1.5,2))


                                property_col.write("[{}]({})".format(parameter.display_name, parameter.context_type_iri)+ " (" + "[{}]({})".format(parameter.unit, parameter.unit_iri) + ")")

                                #property_col.text(" ")


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
                                
                            

                            if parameter:
                                if isinstance(parameter, FunctionParameter): 
                                    parameter.set_selected_value(parameter.default_value)
                                else:
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
                                
                                # elif isinstance(non_material_parameter, FunctionParameter):
                                #     formatted_value_dict = {
                                #         "@type": "emmo:Function",
                                #         "hasStringData": non_material_parameter.selected_value
                                #     }

                                parameter_details = {
                                    "label": parameter.name,
                                    "@type": parameter.context_type_iri if parameter.context_type_iri else "None",
                                    "value": formatted_value_dict
                                }
                                if isinstance(parameter, NumericalParameter):
                                    parameter_details["unit"] = "emmo:"+parameter.unit_name if parameter.unit_name else parameter.unit

                                component_parameters.append(parameter_details)
                                if parameter.name == "density":
                                    density[material_component_id] = parameter.selected_value
                                    
                        if component_name == "negative_electrode_active_material" or component_name == "positive_electrode_active_material":
                            
                            

                            

                            
                            input_text_key = "input_text_{}".format(material_component_id)
                            if input_text_key not in st.session_state:
                                st.session_state[input_text_key] = r'''U_2 - U_0 + R*T/F*(-0.00055*c + 8.1)'''

                            ex.text_input(
                                label = "Open circuit potential (fill in your equation)",
                                value = st.session_state[input_text_key],
                                key = input_text_key,
                                label_visibility= "visible"
                            )

                            equation_str = st.session_state[input_text_key]
                            
                            f = sp.symbols('c')
                            equation = sp.Eq(sp.sympify(equation_str),0)

                            equation_latex = sp.latex(equation)

                            ex.latex("OCP = " + equation_latex)

                            

                            info = ex.toggle(label="OCP guidelines", key = "toggle_{}".format(material_component_id))
                            if info:
                                parameters,language  = ex.columns(2)
                                language.markdown(r'''
                                         **Allowed language** 
                                         - Use '**' to indicate a power to
                                         - Use '*' to indicate a multiplication
                                        ''')
                                
                                parameters.markdown(r'''
                                         **Allowed parameters**
                                         - Surface concentration : c
        

                                         
                                         ''')
                                

                        component_parameters = self.create_component_parameters_dict(component_parameters)
                

                        component_parameters["label"] = material_comp_display_name
                        component_parameters["@type"] = material_comp_context_type_iri

                        
                        
                        category_parameters[material_comp_context_type] = component_parameters
                
                component_parameters = []
                vf_parameter, user_input, component_parameter,_,vf_sum = self.fill_vf_column(vf_col,category_id,material_comp_default_template_id,material_component_id,component_parameters,vf_sum,tab,emmo_relation=None)

                component_parameters = self.create_component_parameters_dict(component_parameters)

                component_parameters["label"] = material_comp_display_name
                component_parameters["@type"] = material_comp_context_type_iri

                        
                print(component_parameters)
                print(category_parameters)
                category_parameters[material_comp_context_type][self.has_quantitative_property] += (component_parameters[self.has_quantitative_property])
                
                
                #print(category_parameters[non_material_comp_context_type][self.has_quantitative_property])
                #print(component_parameters[self.has_quantitative_property])

            
                    


                        # # Load the JSON schema from a file
                        # schema_file_path = db_access.get_path_to_schema_dir() + "/user_defined_am.json"
                        # with open(schema_file_path, "r") as schema_file:
                        #     schema = json.load(schema_file)

                        # # Load the JSON schema from a file
                        # data_file_path = db_access.get_path_to_schema_dir() + "/user_defined_am_data.json"
                        # with open(data_file_path, "r") as data_file:
                        #     data = json.load(data_file)    
                        

                        # form_data = self.schema_to_form(ex,schema)
                        # ex.write(form_data)
      
            print("dens=", density)        
            self.validate_volume_fraction(vf_sum, category_display_name,tab)
            density_mix = self.calc_density_mix(vf_sum, density)  
            
            non_material_component = db_helper.get_non_material_components_from_category_id(category_id)      
            component_parameters = []
            non_material_component_id, non_material_component_name, _,_,_,_,_,non_material_comp_display_name,_,_,_,non_material_comp_default_template_id,non_material_comp_context_type,non_material_comp_context_type_iri,_ = non_material_component
            
            tab.markdown("**%s**" % non_material_comp_display_name)
            check_col, property_col, value_col= tab.columns((0.3,1,2))

            
            non_material_parameters_sets = np.squeeze(db_helper.get_non_material_set_id_by_component_id(non_material_component_id))
            
            non_material_parameter,user_input,component_parameters, mass_loadings = self.fill_non_material_component(category_id,category_name,non_material_comp_default_template_id,non_material_component_id,property_col,value_col,non_material_parameters_sets,self.model_id, component_parameters, check_col,non_material_component_name,tab, density_mix, mass_loadings)

            #pdb.set_trace()
            component_parameters["label"] = non_material_comp_display_name
            component_parameters["@type"] = non_material_comp_context_type_iri

            category_parameters[non_material_comp_context_type] = component_parameters
            
           

        if category_name == "negative_electrode":
            
            category_parameters = self.set_ne_advanced_tabs(tab, category_display_name, category_parameters)
            

        elif category_name == "positive_electrode":
            category_parameters = self.set_pe_advanced_tabs(tab,category_display_name,category_parameters)    
        

            
        # get custom template if it exists or default one
        #template_name = self.model_templates.get(category_name)
        #template_id = db_helper.sql_template.get_id_from_name(template_name) if template_name else default_template_id

    

                # selectbox for left column (parameter sets)
                # selected_value_id = select_box_col.selectbox(
                #     label="[{}]({})".format(parameter.display_name, parameter.context_type_iri),
                #     options=parameter.options,
                #     key="select_{}_{}".format(category_id, parameter_id),
                #     label_visibility="visible",
                #     format_func=lambda x: parameter.options.get(x).display_name,
                #     on_change=reset_func,
                #     args=(category_id, parameter_id, parameter)
                # )


                # number input / selectbox for right column, depending on the parameter type
                # if isinstance(parameter, NumericalParameter):

                #     user_input = input_col.number_input(
                #         label="[{}]({})".format(parameter.unit, parameter.unit_iri),
                #         value=parameter.options[selected_value_id].value,
                #         min_value=parameter.min_value,
                #         max_value=parameter.max_value,
                #         key="input_{}_{}".format(category_id, parameter_id),
                #         format=parameter.format,
                #         step=parameter.increment,
                #         label_visibility="visible"
                #     )
                # elif isinstance(parameter, FunctionParameter):
                #     user_input = input_col.selectbox(
                #         label=parameter.display_name,
                #         options=[parameter.options.get(selected_value_id).value.get("functionname")],
                #         key="input_{}_{}".format(category_id, parameter_id),
                #         label_visibility="hidden",
                #     )
                # else:
                #     user_input = input_col.selectbox(
                #         label=parameter.display_name,
                #         options=[parameter.options.get(selected_value_id).value],
                #         key="input_{}_{}".format(category_id, parameter_id),
                #         label_visibility="hidden",
                #     )
                

            

            
            # if isinstance(material, NumericalParameter):
            #     formatted_value_dict = {
            #         "@type": "emmo:Numerical",
            #         "hasNumericalData": parameter.selected_value
            #     }


                

            # elif isinstance(parameter, BooleanParameter):
            #     formatted_value_dict = {
            #         "@type": "emmo:Boolean",
            #         "hasStringData": parameter.selected_value
            #     }

            # elif isinstance(parameter, FunctionParameter):
            #     formatted_value_dict = {
            #         "@type": "emmo:String",
            #         "hasStringData": parameter.selected_value
            #     }

            
            # if isinstance(parameter, NumericalParameter):
            #     parameter_details["unit"] = "emmo:"+parameter.unit_name if parameter.unit_name else parameter.unit
        
        if category_name == "electrolyte" or category_name == "separator":
            
            
            component_col, material_col = tab.columns((1,2))
            component_parameters = []
            material_component_id, component_name, _,_,_,_,_,material_comp_display_name,_,_,_,material_comp_default_template_id,material_comp_context_type,material_comp_context_type_iri,_ = material_components[0]
                
                
            component_col.markdown("**%s**" % material_comp_display_name)
    
            material_formatted_parameters,formatted_materials,selected_value_id, component_parameters,_,_ = self.fill_material_column(component_name,material_comp_default_template_id,material_component_id,material_col,material_comp_display_name,material_comp_context_type_iri,material_components[0], category_parameters, density=None)
            
            #formatted_materials.set_selected_value(selected_value_id)

            
            # if formatted_materials:

            #     formatted_value_dict = formatted_materials.selected_value
            #     if isinstance(formatted_materials, NumericalParameter):
            #         formatted_value_dict = {
            #             "@type": "emmo:Numerical",
            #             "hasNumericalData": formatted_materials.selected_value
            #         }

            #     elif isinstance(formatted_materials, StrParameter):
            #         formatted_value_dict = {
            #             "@type": "emmo:String",
            #             "hasStringData": formatted_materials.selected_value
            #         }

            #     elif isinstance(formatted_materials, BooleanParameter):
            #         formatted_value_dict = {
            #             "@type": "emmo:Boolean",
            #             "hasStringData": formatted_materials.selected_value
            #         }

            #     parameter_details = {
            #         "label": formatted_materials.name,
            #         "@type": formatted_materials.context_type_iri if formatted_materials.context_type_iri else "None",
            #         "value": formatted_value_dict
            #     }
            #     if isinstance(formatted_materials, NumericalParameter):
            #         parameter_details["unit"] = "emmo:"+formatted_materials.unit_name if formatted_materials.unit_name else formatted_materials.unit

            

            component_parameters = self.create_component_parameters_dict(component_parameters)    

            component_parameters["label"] = material_comp_display_name
            component_parameters["@type"] = material_comp_context_type_iri

            category_parameters[material_comp_context_type] = component_parameters


            material_choice = formatted_materials.options.get(selected_value_id).display_name
            print("mat_opt=", material_choice)
            material = formatted_materials.options.get(selected_value_id)
            parameters = material.parameters
            
            
            if material_choice == "User Defined":

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
                        print(parameter)
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
                                # if parameter.name == "charge_carrier_transference_number" or parameter.name == "counter_ion_transference_number":
                                #     if parameter.name == "charge_carrier_transference_number":
                                #         place = cc_tr_place
                                #     elif parameter.name == "counter_ion_transference_number":
                                #         place = cion_tr_place
                                    
                                    
                                #     user_input = place.number_input(
                                #     label=parameter.name,
                                #     value=st.session_state[tr_value],
                                #     min_value=parameter.min_value,
                                #     max_value=parameter.max_value,
                                #     key=tr_value,
                                #     format=parameter.format,
                                #     step=parameter.increment,
                                #     label_visibility="collapsed"
                                #     )

                                # else:

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
                            #property_col.text(" ")


                            
                        

                        if parameter:
                            if isinstance(parameter, FunctionParameter): 
                                parameter.set_selected_value(parameter.default_value)
                            else:
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
                            
                            # elif isinstance(non_material_parameter, FunctionParameter):
                            #     formatted_value_dict = {
                            #         "@type": "emmo:Function",
                            #         "hasStringData": non_material_parameter.selected_value
                            #     }

                            parameter_details = {
                                "label": parameter.name,
                                "@type": parameter.context_type_iri if parameter.context_type_iri else "None",
                                "value": formatted_value_dict
                            }
                            if isinstance(parameter, NumericalParameter):
                                parameter_details["unit"] = "emmo:"+parameter.unit_name if parameter.unit_name else parameter.unit

                            # if parameter.name == "charge_carrier_transference_number":
                            #     tr_value = "tr_value_{}_{}".format(category_id, parameter.name)
                            #     index_key= "index_{}_{}".format(category_id, parameter.name)
                            #     tr_number = parameter.selected_value
                            #     st.session_state[index_key] = par_indexes

                            #     if "input_{}_{}".format(category_id, "charge_carrier_transference_number"):
                            #         st.session_state[tr_value] = 1 - tr_number

                            #         # user_input = cion_tr_place.number_input(
                            #         #     label=parameter.name,
                            #         #     value=st.session_state[tr_value],
                            #         #     min_value=parameter.min_value,
                            #         #     max_value=parameter.max_value,
                            #         #     key="input_{}_{}_{}".format(category_id, parameter.name, np.random.rand(100)),
                            #         #     format=parameter.format,
                            #         #     step=parameter.increment,
                            #         #     label_visibility="collapsed")
                            # elif parameter.name == "counter_ion_transference_number":
                            #     tr_value = "tr_value_{}_{}".format(category_id, parameter.name)
                            #     index_key= "index_{}_{}".format(category_id, parameter.name)
                            #     st.session_state[index_key] = par_indexes
                            #     tr_number = parameter.selected_value

                            #     if "input_{}_{}".format(category_id, "counter_ion_transference_number"):
                            #         st.session_state[tr_value] = 1 - tr_number


                            #         # user_input = cc_tr_place.number_input(
                            #         #     label=parameter.name,
                            #         #     value=st.session_state[tr_value],
                            #         #     min_value=parameter.min_value,
                            #         #     max_value=parameter.max_value,
                            #         #     key="input_{}_{}".format(category_id, parameter.name, np.random.rand(100)),
                            #         #     format=parameter.format,
                            #         #     step=parameter.increment,
                            #         #     label_visibility="collapsed"
                            #         #     )


                            
                            
                            

                            component_parameters.append(parameter_details)
                            # if parameter.name == "charge_carrier_transference_number" or parameter.name == "counter_ion_transference_number":
                            #     if st.session_state[tr_value]:
                            #         component_parameters[st.session_state[index_key]]["value"]["hasNumericalData"]=st.session_state[tr_value]
                        par_indexes +=1


                    component_parameters = self.create_component_parameters_dict(component_parameters)
            

                    component_parameters["label"] = material_comp_display_name
                    component_parameters["@type"] = material_comp_context_type_iri

                    
                    
                    category_parameters[material_comp_context_type] = component_parameters

            
            
        
        
        non_material_component = db_helper.get_non_material_components_from_category_id(category_id)      

        non_material_component_id, non_material_component_name, _,_,_,_,_,non_material_comp_display_name,_,_,_,non_material_comp_default_template_id,non_material_comp_context_type,non_material_comp_context_type_iri,_ = non_material_component
        
        if category_name == "separator" or category_name == "boundary_conditions":
            component_parameters = []
            tab.markdown("**%s**" % non_material_comp_display_name)
            property_col, value_col= tab.columns((1,2))
            non_material_parameters_sets = db_helper.get_non_material_set_id_by_component_id(non_material_component_id)[0]
            
            non_material_parameter,user_input, component_parameters,_ = self.fill_non_material_component(category_id,category_name,non_material_comp_default_template_id,non_material_component_id,property_col,value_col,non_material_parameters_sets,self.model_id,component_parameters, check_col = None,non_material_component_name = None, tab = None, density_mix = None, mass_loadings = None)
            
            #component_parameters = self.create_component_parameters_dict(component_parameters)
            component_parameters["label"] = non_material_comp_display_name
            component_parameters["@type"] = non_material_comp_context_type_iri

            category_parameters[non_material_comp_context_type] = component_parameters

            


    #category_parameters.append(material_details)


            adv_input =tab.expander("Show '{}' advanced parameters".format(category_display_name))
            
            component_parameters = []
            non_material_component = db_helper.get_advanced_components_from_category_id(category_id)      

            non_material_component_id, non_material_component_name, _,_,_,_,_,non_material_comp_display_name,_,_,_,non_material_comp_default_template_id,non_material_comp_context_type,non_material_comp_context_type_iri,_ = non_material_component
                

            #template_name = self.model_templates.get(category_name)
            #template_id = db_helper.sql_template.get_id_from_name(template_name) if template_name else default_template_id
            print("model=",self.model_id)
            raw_template_parameters = tuple(np.squeeze(db_helper.get_advanced_template_by_template_id(default_template_id)))
            print("temp=",raw_template_parameters)
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
                print("id=",non_material_parameter_id, name, non_material_parameter_set_id,non_material_parameters_set_name,default_template_id)
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

                # elif isinstance(parameter, FunctionParameter):
                #     formatted_value_dict = {
                #         "@type": "emmo:Boolean",
                #         "hasStringData": parameter.selected_value
                #     }
                

                parameter_details = {
                    "label": parameter.name,
                    "@type": parameter.context_type_iri if parameter.context_type_iri else "None",
                    "value": formatted_value_dict
                }
                if isinstance(parameter, NumericalParameter):
                    parameter_details["unit"] = "emmo:"+parameter.unit_name if parameter.unit_name else parameter.unit


                component_parameters.append(parameter_details)

                
            #component_parameters = self.create_component_parameters_dict(component_parameters)
            # component_parameters["label"] = non_material_comp_display_name
            # component_parameters["@type"] = non_material_comp_context_type_iri
            # print(category_parameters)
            # print(category_parameters[non_material_comp_context_type][self.has_quantitative_property])
            # print(component_parameters[self.has_quantitative_property])
            

            category_parameters[non_material_comp_context_type][self.has_quantitative_property] += component_parameters

            
        return category_parameters, emmo_relation, mass_loadings

    def fill_category_protocol(self, category_id,category_display_name, category_name, emmo_relation, default_template_id, tab,category_parameters):
        """
        same idea as fill category, just choosing a Protocol to set all params
        """

        component_parameters = []
        non_material_component = db_helper.get_non_material_components_from_category_id(category_id)      

        non_material_component_id, non_material_component_name, _,_,_,_,_,non_material_comp_display_name,_,_,_,non_material_comp_default_template_id,non_material_comp_context_type,non_material_comp_context_type_iri,_ = non_material_component
            

        #template_name = self.model_templates.get(category_name)
        #template_id = db_helper.sql_template.get_id_from_name(template_name) if template_name else default_template_id

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

            elif isinstance(parameter, FunctionParameter):
                    formatted_value_dict = {
                        "@type": "emmo:Boolean",
                        "hasStringData": parameter.selected_value
                    }

            parameter_details = {
                "label": parameter.name,
                "@type": parameter.context_type_iri if parameter.context_type_iri else "None",
                "value": formatted_value_dict
            }
            if isinstance(parameter, NumericalParameter):
                parameter_details["unit"] = "emmo:"+parameter.unit_name if parameter.unit_name else parameter.unit

            component_parameters.append(parameter_details)
        component_parameters = self.create_component_parameters_dict(component_parameters)
        component_parameters["label"] = non_material_comp_display_name
        component_parameters["@type"] = non_material_comp_context_type_iri

        category_parameters[non_material_comp_context_type] = component_parameters

        adv_input =tab.expander("Show '{}' advanced parameters".format(category_display_name))
        component_parameters = []
        non_material_component = db_helper.get_advanced_components_from_category_id(category_id)      

        non_material_component_id, non_material_component_name, _,_,_,_,_,non_material_comp_display_name,_,_,_,non_material_comp_default_template_id,non_material_comp_context_type,non_material_comp_context_type_iri,_ = non_material_component
            

        #template_name = self.model_templates.get(category_name)
        #template_id = db_helper.sql_template.get_id_from_name(template_name) if template_name else default_template_id
        print("model=",self.model_id)
        raw_template_parameters = tuple(np.squeeze(db_helper.get_advanced_template_by_template_id(default_template_id)))
        print("temp=",raw_template_parameters)
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
            print("id=",non_material_parameter_id, name, non_material_parameter_set_id,non_material_parameters_set_name,default_template_id)
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

            # elif isinstance(parameter, FunctionParameter):
            #     formatted_value_dict = {
            #         "@type": "emmo:Boolean",
            #         "hasStringData": parameter.selected_value
            #     }
            

            parameter_details = {
                "label": parameter.name,
                "@type": parameter.context_type_iri if parameter.context_type_iri else "None",
                "value": formatted_value_dict
            }
            if isinstance(parameter, NumericalParameter):
                parameter_details["unit"] = "emmo:"+parameter.unit_name if parameter.unit_name else parameter.unit


            component_parameters.append(parameter_details)

            
        #component_parameters = self.create_component_parameters_dict(component_parameters)
        # component_parameters["label"] = non_material_comp_display_name
        # component_parameters["@type"] = non_material_comp_context_type_iri
        # print(category_parameters)
        # print(category_parameters[non_material_comp_context_type][self.has_quantitative_property])
        # print(component_parameters[self.has_quantitative_property])
        

        category_parameters[non_material_comp_context_type][self.has_quantitative_property] += component_parameters


        

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


class SaveParameters:
    """
    Rendering of Save Parameters section in Define Parameters tab

    Can be improved, to make it more obvious that it is needed to save before running simulation
    """
    def __init__(self, gui_parameters):
        self.header = "Run simulation"

        self.download_button_label = "Download parameters - Json LD format"
        self.json_file = os.path.join(db_access.get_path_to_BattMoJulia_dir(),"battmo_formatted_input.json")

        self.gui_parameters = gui_parameters
        self.gui_file_data = json.dumps(gui_parameters, indent=2)
        self.gui_file_name = "gui_output_parameters.json"
        self.file_mime_type = "application/json"

        self.set_submit_button()

    def set_submit_button(self):
        #set header
        st.markdown("### " + self.header)
        st.text(" ")

        # set download button
        # st.download_button(
        #     label=self.download_button_label,
        #     data=self.gui_file_data,
        #     file_name=self.gui_file_name,
        #     mime=self.file_mime_type
        # )
        empty,save,run = st.columns((0.3,1,1))
        m = st.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: #e1e7f2;
                
                
                height:3em;
                width:10em;
                font-size:20px;
                        
                border-radius:10px 10px 10px 10px;
            }
            </style>""", unsafe_allow_html=True)

        save.button(
            label="UPDATE",
            on_click=self.on_click_save_file
        )

        # set RUN button
        run.button(
            label="RUN",
            on_click= octave_on_click,
            args = ( self.json_file, )
            
        )

    def on_click_save_file(self):
        path_to_battmo_input = db_access.get_path_to_battmo_input()
        # save parameters in json file
        with open(path_to_battmo_input, "w") as new_file:
            json.dump(
                self.gui_parameters,
                new_file,
                indent=3)

        # Format parameters from json-LD to needed format
        path_to_battmo_formatted_input = db_access.get_path_to_battmo_formatted_input()
        # save formatted parameters in json file
        with open(path_to_battmo_formatted_input, "w") as new_file:
            json.dump(
                match_json.get_batt_mo_dict_from_gui_dict(self.gui_parameters),
                new_file,
                indent=3
            )

        st.success("Your parameters are saved! Run the simulation to get your results.")





def octave_on_click(json_file):

    ##############################
    # Remember user changed values
    for k, v in st.session_state.items():
        st.session_state[k] = v
    ##############################

    ##############################
    # Set page directory to base level to allow for module import from different folder

    sys.path.insert(0, db_access.get_path_to_gui_dir())
    
    ##############################


    #print(sys.path)
    print(db_access.get_path_to_gui_dir())
    uuids = requests.get(url ='http://127.0.0.1:5000/run_simulation', data={'InputFolder': 'BattMoJulia', 
                                                                            'InputFile':'battmo_formatted_input.json',
                                                                            'JuliaModelFolder':'BattMoJulia',
                                                                            'JuliaModel': 'runP2DBattery.jl'}).json()



    with open(os.path.join(db_access.get_path_to_gui_dir(),"results", uuids), "rb") as pickle_result:
        result = pickle.load(pickle_result)

    with open(os.path.join(db_access.get_path_to_python_dir(), "battmo_result"), "wb") as new_pickle_file:
                pickle.dump(result, new_pickle_file)


    st.success("Simulation finished successfully! Check the results by clicking 'Plot latest results'.")



    # clear cache to get new data in hdf5 file (cf Plot_latest_results)
    st.cache_data.clear()



class RunSimulation:
    """
    Rendering of Run Simulation tab
    """
    def __init__(self):
        self.run_header = "Run Simulation"
        self.run_info = """ The BattMo toolbox used for running the simulations is Julia based. Julia is a compiled language and because of this, the first 
                            simulation will be slow, but next simulations will be very quick."""
        

        self.gui_button_label = "Save GUI output parameters"
        self.battmo_button_label = "Save BattMo input parameters"
                
        # retrieve saved parameters from json file
        with open(db_access.get_path_to_battmo_input()) as json_gui_parameters:
            self.gui_parameters = json.load(json_gui_parameters)

        self.download_header = "Download parameters"
        self.download_label = "Json LD format"
        self.gui_file_data = json.dumps(self.gui_parameters, indent=2)
        self.gui_file_name = "json_ld_parameters.json"
        self.file_mime_type = "application/json"

        # retrieve saved formatted parameters from json file
        with open(db_access.get_path_to_battmo_formatted_input()) as json_formatted_gui_parameters:
            self.formatted_gui_parameters = json.load(json_formatted_gui_parameters)

        self.download_label_formatted_parameters = "BattMo format"
        self.formatted_parameters_file_data = json.dumps(self.formatted_gui_parameters, indent=2)
        self.formatted_parameters_file_name = "battmo_formatted_parameters.json"

        #self.push_battmo_folder = 'push!(LOAD_PATH, "BattMoJulia")'
        self.runP2DBattery_path = db_access.get_path_to_runp2dbattery()

        #self.set_init_button()        
        self.set_submit_button()


    def set_submit_button(self):

        

        # set Download header
        st.markdown("### " + self.download_header)

        # set download button
        st.download_button(
            label=self.download_label,
            data=self.gui_file_data,
            file_name=self.gui_file_name,
            mime=self.file_mime_type
        )

        st.download_button(
            label=self.download_label_formatted_parameters,
            data=self.formatted_parameters_file_data,
            file_name=self.formatted_parameters_file_name,
            mime=self.file_mime_type
        )


        # set RUN header
        #st.markdown("### " + self.run_header)

        #st.info(self.run_info)

        
      




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

