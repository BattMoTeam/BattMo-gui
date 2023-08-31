import streamlit as st
from . import db_handler
import numpy as np

"""
Functions called from GUI code to access db.

@st.cache_data is used for every db query to optimize software's performance
"""


@st.cache_data
def sql_parameter():
    return db_handler.ParameterHandler()


@st.cache_data
def sql_parameter_set():
    return db_handler.ParameterSetHandler()


@st.cache_data
def sql_category():
    return db_handler.CategoryHandler()


@st.cache_data
def sql_component():
    return db_handler.ComponentHandler()

@st.cache_data
def sql_material():
    return db_handler.MaterialHandler()

@st.cache_data
def sql_tab():
    return db_handler.TabHandler()


@st.cache_data
def sql_model():
    return db_handler.ModelHandler()


@st.cache_data
def sql_model_parameter():
    return db_handler.ModelParameterHandler()


@st.cache_data
def sql_template():
    return db_handler.TemplateHandler()


@st.cache_data
def sql_template_parameter():
    return db_handler.TemplateParameterHandler()


#####################################
# TAB
#####################################

@st.cache_data
def get_basis_tabs_display_names():
    res = sql_tab().select(
        values='display_name'
    )
    return [a[0] for a in res]

@st.cache_data
def get_tabs_display_names(model_id):
    res = sql_tab().select(
        values='display_name',
        where = "model_id = %s" % model_id
    )
    return [a[0] for a in res]

@st.cache_data
def get_basis_tabs_display_names(model_id):
    res = sql_tab().select(
        values='display_name',
        where="model_id='%d' and difficulty= 'basis' or model_id='%d' and difficulty= 'basis_advanced'" % (model_id, model_id)
    )
    return [a[0] for a in res]

@st.cache_data
def get_advanced_tabs_display_names(model_id):
    res = sql_tab().select(
        values='display_name',
        where="model_id='%d' and difficulty= 'advanced' or model_id='%d' and difficulty= 'basis_advanced'" % (model_id, model_id)
    )
    return [a[0] for a in res]


@st.cache_data
def get_tabs_names():
    res = sql_tab().select(
        values='name'
    )
    return [a[0] for a in res]


@st.cache_data
def get_context_type_and_iri_by_id(id):
    res = sql_tab().select_one(
        values='context_type, context_type_iri',
        where='id=%d' % id
    )
    return res[0], res[1] if res else None


@st.cache_data
def st_tab_id_to_db_tab_id():
    res = sql_tab().select(
        values='id'
    )
    return [a[0] for a in res]

@st.cache_data
def get_db_tab_id(tab_index):
    res = sql_tab().select(
        values='id',
    )
    return res[tab_index]



def get_tab_index_from_st_tab(st_tab):
    # according to st.tabs container structure
    return st_tab._provided_cursor._parent_path[1]


#####################################
# CATEGORY
#####################################
@st.cache_data
def get_basis_categories_from_tab_id(tab_id):
    res = sql_category().select(
        values = '*',
        where="tab_id=%d and (difficulty = 'basis' or difficulty = 'basis_advanced')" % tab_id
    )
    return res

#####################################
# COMPONENT
#####################################
@st.cache_data
def get_material_components_from_category_id(category_id):
    res = sql_component().select(
        values = '*',
        where="category_id=%d AND material = %d AND (difficulty = 'basis' OR difficulty = 'basis_advanced')" % (category_id,1)
    )
    return res

@st.cache_data
def get_non_material_components_from_category_id(category_id):
    res = sql_component().select(
        values = '*',
        where="category_id=%d AND material = %d AND (difficulty = 'basis' OR difficulty = 'basis_advanced')" % (category_id,0)
    )
    return np.squeeze(res)


@st.cache_data
def get_n_to_p_component_by_tab_id(tab_id):
    res = sql_component().select(
        values = '*',
        where="tab_id=%d AND material = 0 AND (difficulty = 'basis' OR difficulty = 'basis_advanced')" % tab_id
    )
    return np.squeeze(res)

#####################################
# MATERIAL
#####################################
@st.cache_data
def get_material_from_component_id(component_id):
    res = sql_material().select(
        values = '*',
        where="component_id_1=%d or component_id_2=%d " % (component_id,component_id)
    )
    return res

@st.cache_data
def get_material_names_from_component_id(component_id):
    res = sql_material().select(
        values = 'display_name',
        where="component_id_1=%d or component_id_2=%d " % (component_id,component_id)
    )
    return [a[0] for a in res]

@st.cache_data
def get_material_id_by_parameter_set_name(name):
        res = sql_material().select(
            values='id',
            where="name='%s'" % name
        )
        return [a[0] for a in res]

@st.cache_data
def get_display_name_from_material_id(material_id):
        res = sql_material().select(
            values='display_name',
            where="id=%d " % material_id
        )
        return [a[0] for a in res]

#####################################
# PARAMETER
#####################################
@st.cache_data
def get_parameter_id_from_template_parameter_and_parameter_set(template_parameter_id, parameter_set_id):
    return sql_parameter().get_id_from_template_parameter_id_and_parameter_set_id(template_parameter_id, parameter_set_id)


#####################################
# PARAMETER SET
#####################################
@st.cache_data
def get_all_parameter_sets_by_category_id(category_id):
    return sql_parameter_set().get_all_by_category_id(category_id)

@st.cache_data
def get_all_parameter_sets_by_component_id(component_id):
    return sql_parameter_set().get_all_by_component_id(component_id)

@st.cache_data
def get_all_material_parameter_sets_by_component_id(component_id):
    return sql_parameter_set().get_all_material_by_component_id(component_id)


@st.cache_data
def extract_parameters_by_parameter_set_id(parameter_set_id):
    return sql_parameter().get_all_by_parameter_set_id(parameter_set_id)

def get_all_material_by_component_id(component_id):
        return sql_parameter_set().select(
            values='*',
            where="component_id=%d AND material = %d"  % (component_id,1)
        )

def get_vf_parameter_set_id_by_component_id(component_id):
    res = np.squeeze(sql_parameter_set().select(
        values = 'id, name',
        where="component_id=%d AND material = %d" % (component_id,0)
    )).astype(str)
    return res

def get_n_p_parameter_set_id_by_component_id(component_id):
    res = np.squeeze(sql_parameter_set().select(
        values = 'id,name',
        where="component_id=%d AND material = %d" % (component_id,0)
    )).astype(str)
    return res

def get_non_material_set_id_by_component_id(component_id):
    res = sql_parameter_set().select(
        values = '*',
        where="component_id=%d AND material = %d" % (component_id,0)
    )
    return res

def get_vf_raw_parameter_by_parameter_set_id(parameter_set_id):
    res = sql_parameter().select(
        values = '*',
        where="parameter_set_id=%d AND name = 'volume_fraction'" % parameter_set_id
    )
    return res

def get_n_p_parameter_by_template_id(parameter_set_id):
    res = sql_parameter().select(
        values = '*',
        where="parameter_set_id=%d" % parameter_set_id
    )
    return res

def get_non_material_raw_parameter_by_template_parameter_id_and_parameter_set_id(template_parameter_id,parameter_set_id):
    res = sql_parameter().select(
        values = '*',
        where="template_parameter_id=%d AND parameter_set_id=%d" % (template_parameter_id,parameter_set_id)
    )
    return res


#####################################
# MODEL
#####################################
@st.cache_data
def get_models_as_dict():
    models = sql_model().select_all()
    models_as_dict = {}

    for model in models:
        model_id, model_name, _ = model

        models_as_dict[model_id] = model_name

    return models_as_dict


# @st.cache_data
# def get_templates_by_id(model_id):
#     res = sql_model().select_one(
#         values="templates",
#         where="id=%d" % model_id
#     )
#     return eval(res[0]) if res else None


@st.cache_data
def get_model_parameters_as_dict(model_id):
    parameters = sql_model_parameter().get_all_by_model_id(model_id)
    model_quantitative_properties = []

    for parameter in parameters:
        _, name, _, value, value_type, _, unit_name, _, _ = parameter

        parameter_details = {
            "label": name
        }

        if value_type == "bool":
            print("value=",value)
            formatted_value_dict = {
                "@type": "emmo:Boolean",
                "hasStringData": bool(value)
            }
        elif value_type == "str":
            formatted_value_dict = {
                "@type": "emmo:String",
                "hasStringData": value
            }
        elif value_type == "float":
            formatted_value_dict = {
                "@type": "emmo:Numerical",
                "hasNumericalData": float(value)
            }
            parameter_details["unit"] = "emmo:"+unit_name
        else:
            assert False, "model parameter type={} not handled. name={}".format(value_type, name)

        parameter_details["value"] = formatted_value_dict
        model_quantitative_properties.append(parameter_details)

    return model_quantitative_properties


#####################################
# TEMPLATE
#####################################
@st.cache_data
def get_material_template_parameters_from_template_id(template_id):
    return sql_template_parameter().get_all_material_by_template_id(template_id)

def get_all_material_by_template_id(template_id):
        return sql_template_parameter().select(
            values='*',
            where="template_id=%d AND par_class = '%s'" % (template_id,"material")
        )

def get_vf_template_by_template_id(template_id):
    return sql_template_parameter().select(
            values='*',
            where="template_id=%d AND name = '%s'" % (template_id,"volume_fraction")
        )

def get_non_material_template_by_template_id(template_id, model_id):
    return sql_template_parameter().select(
            values='*',
            where="template_id=%d AND par_class = '%s' AND model_id = %d AND (difficulty = 'basis' OR difficulty = 'basis_advanced')" % (template_id,"non_material",model_id)
        )

def get_n_p_template_by_template_id(template_id):
    return sql_template_parameter().select(
            values='*',
            where="template_id=%d AND par_class = '%s' AND (difficulty = 'basis' OR difficulty = 'basis_advanced')" % (template_id,"non_material")
        )

#all_basis_tab_display_names = get_basis_tabs_display_names(model_id)
#all_advanced_tab_display_names = get_advanced_tabs_display_names()
# all_tab_display_names = get_tabs_display_names()
# all_tab_names = get_tabs_names()
all_tab_id = st_tab_id_to_db_tab_id()
