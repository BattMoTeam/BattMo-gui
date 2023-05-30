import streamlit as st
from . import db_handler

"""
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
def get_tabs_display_names():
    res = sql_tab().select(
        values='display_name'
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


def get_tab_index_from_st_tab(st_tab):
    # according to st.tabs container structure
    return st_tab._provided_cursor._parent_path[1]


#####################################
# CATEGORY
#####################################
@st.cache_data
def get_categories_from_tab_id(tab_id):
    res = sql_category().get_all_by_tab_id(tab_id)
    return res


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
def extract_parameters_by_parameter_set_id(parameter_set_id):
    return sql_parameter().get_all_by_parameter_set_id(parameter_set_id)


#####################################
# MODEL
#####################################
@st.cache_data
def get_models_as_dict():
    models = sql_model().select_all()
    models_as_dict = {}

    for model in models:
        model_id, model_name, _, _ = model

        models_as_dict[model_id] = model_name

    return models_as_dict


@st.cache_data
def get_templates_by_id(model_id):
    res = sql_model().select_one(
        values="templates",
        where="id=%d" % model_id
    )
    return eval(res[0]) if res else None


@st.cache_data
def get_model_parameters_as_dict(model_id):
    parameters = sql_model_parameter().get_all_by_model_id(model_id)
    res = {}
    for parameter in parameters:
        _, name, _, value, value_type, _ = parameter
        if value_type == "bool":
            res[name] = bool(int(value))
        elif value_type == "str":
            res[name] = value
        elif value_type == "float":
            res[name] = float(value)
        else:
            assert False, "model parameter type={} not handled. name={}".format(value_type, name)

    return res


#####################################
# TEMPLATE
#####################################
@st.cache_data
def get_template_parameters_from_template_id(template_id):
    return sql_template_parameter().get_all_by_template_id(template_id)


all_tab_display_names = get_tabs_display_names()
all_tab_names = get_tabs_names()
all_tab_id = st_tab_id_to_db_tab_id()
