import streamlit as st
import numpy as np
import os
import sys
import html 
from streamlit_toggle_component.src.st_toggle_component import st_toggle_component

##############################
# Remember user changed values
for k, v in st.session_state.items():
    st.session_state[k] = v
##############################

# set config is done before import to avoid streamlit error
path_to_python_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, path_to_python_dir)

from resources.db import db_access, db_helper


models_as_dict = db_helper.get_models_as_dict()
P2D_model= db_helper.get_model_parameters_as_dict(1)
P2D_model_description = db_helper.get_model_description("P2D")[0][0]
materials = db_helper.get_all_default_material()




st.title("The available models")

model = st.expander("P2D")

with model:
    
    st.markdown("""**Includes** """)
    st.markdown("- Thermal effects = <span style='color: blue;'>" + str(P2D_model[0]["value"]["hasStringData"]) + "</span>", unsafe_allow_html=True)
    st.markdown("- Current collector = <span style='color: blue;'>" + str(P2D_model[1]["value"]["hasStringData"]) + "</span>", unsafe_allow_html=True)
    st.markdown("- Solid Diffusion model = <span style='color: blue;'>" + str(P2D_model[2]["value"]["hasStringData"]) + "</span>", unsafe_allow_html=True)
    st.markdown("- Solid Diffusion model type = <span style='color: blue;'>" + str(P2D_model[3]["value"]["hasStringData"]) + "</span>", unsafe_allow_html=True)
    st.markdown(" ")
    st.markdown("**Description**")
    #st.markdown(" ")
    st.markdown(P2D_model_description)

st.title("The available materials")



display_names = []
for material_values in materials:
    
    material = material_values
    id,name,_,_,_,_,display_name,number_of_components,component_name_1,component_name_2,_,context_type,_,_,context_type_iri,_ = material
    display_names.append(display_name)


select = st.multiselect(label = "Materials",options = display_names, label_visibility="collapsed")

for material_values in materials:
    
    material = material_values
    id,name,_,_,_,_,display_name,number_of_components,component_name_1,component_name_2,_,context_type,_,_,context_type_iri,_ = material

    reference_link = None
    for choice in select:
        if choice == display_name:

            with st.expander("{} information".format(display_name)):
                context_type_encoded = context_type.replace(":", "&colon;")
                st.markdown("**Context**:")
                st.write("[{}]({})".format(context_type_encoded + " ", context_type_iri))
                if reference_link:
                    st.write("[{}]({})".format("Reference", reference_link))
                st.markdown("**Parameter values**:")
            
                parameter_set_id = db_helper.get_parameter_set_id_by_name(name)
                
                parameter_values = tuple(db_helper.extract_parameters_by_parameter_set_id(parameter_set_id))
                
                for parameter in parameter_values:
                    
                    id,parameter_name,_,template_parameter_id,value = parameter

                    template_parameter = db_helper.get_template_from_name(parameter_name)
                    
                    template_parameter_id, template_parameter_name,_,_,_,_,_,template_context_type, template_context_type_iri,_,unit,unit_name,unit_iri,_,_,_,_,parameter_display_name = template_parameter
                    st.write("[{}]({}) = ".format(parameter_display_name, template_context_type_iri)+ 
                                value + " (" + "[{}]({})".format(unit, unit_iri) + ")")
                    
                
