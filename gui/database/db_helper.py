import streamlit as st
import numpy as np
import sys
import os
import ast

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import db_handler


"""
Functions called from GUI code to access db.

@st.cache_data is used for every db query to optimize software's performance
"""


@st.cache_resource
def sql_parameter():
    return db_handler.ParameterHandler()


@st.cache_resource
def sql_parameter_set():
    return db_handler.ParameterSetHandler()


@st.cache_resource
def sql_category():
    return db_handler.CategoryHandler()


@st.cache_resource
def sql_component():
    return db_handler.ComponentHandler()


@st.cache_resource
def sql_material():
    return db_handler.MaterialHandler()


@st.cache_resource
def sql_tab():
    return db_handler.TabHandler()


@st.cache_resource
def sql_model():
    return db_handler.ModelHandler()


@st.cache_resource
def sql_model_parameter():
    return db_handler.ModelParameterHandler()


@st.cache_resource
def sql_template():
    return db_handler.TemplateHandler()


@st.cache_resource
def sql_template_parameter():
    return db_handler.TemplateParameterHandler()


#####################################
# TAB
#####################################

# @st.cache_data
# def get_basis_tabs_display_names():
#     res = sql_tab().select(
#         values='display_name'
#     )
#     return [a[0] for a in res]


@st.cache_data
def get_tabs_display_names(model_id):
    res = sql_tab().select(values="display_name", where="model_id = %s" % model_id)
    return [a[0] for a in res]


@st.cache_data
def get_tabs_display_name_from_id(tab_id):
    res = sql_tab().select(values="display_name", where="id = %d" % tab_id)
    return [a[0] for a in res]


@st.cache_data
def get_basis_tabs_display_names(model_name):
    res = sql_tab().select(
        values="display_name",
        where="model_name = '{}' and difficulty= 'basis' or model_name = '{}' and difficulty= 'basis_advanced'".format(
            model_name, model_name
        ),
    )
    return [a[0] for a in res]


@st.cache_data
def get_basis_tab_names(model_name):
    res = sql_tab().select(
        values="name",
        where="model_name = '{}' and difficulty= 'basis' or model_name = '{}' and difficulty= 'basis_advanced'".format(
            model_name, model_name
        ),
    )
    return [a[0] for a in res]


@st.cache_data
def get_advanced_tabs_display_names(model_name):
    res = sql_tab().select(
        values="display_name",
        where="model_name = '{}' and difficulty= 'basis' or model_name = '{}' and difficulty= 'basis_advanced'".format(
            model_name, model_name
        ),
    )
    return [a[0] for a in res]


@st.cache_data
def get_advanced_tab_display_names(model_name, category_name):
    res = sql_tab().select(
        values="display_name",
        where="model_name = '{}' AND name = '{}'".format(model_name, category_name),
    )
    return [a[0] for a in res]


@st.cache_data
def get_tabs_names():
    res = sql_tab().select(values="name")
    return [a[0] for a in res]


@st.cache_data
def get_tab_name_by_id(id):
    tab = sql_tab().select(values="name", where="id=%d" % id)
    return tab[0][0]


@st.cache_data
def get_context_type_and_iri_by_id(id):
    res = sql_tab().select_one(values="context_type", where="id=%d" % id)
    return np.array(res)[0]


@st.cache_data
def st_tab_id_to_db_tab_id():
    res = sql_tab().select(values="id")
    return [a[0] for a in res]


@st.cache_data
def get_db_tab_id(model_name):
    res = sql_tab().select(
        values="id",
        where="model_name = '{}' and difficulty= 'basis' or model_name = '{}' and difficulty= 'basis_advanced'".format(
            model_name, model_name
        ),
    )
    return res


@st.cache_data
def get_advanced_db_tab_id(model_name, category_name):
    res = sql_tab().select(
        values="id",
        where="model_name = '{}' AND name = '{}'".format(model_name, category_name),
    )
    return res


@st.cache_data
def get_tab_index_from_st_tab(st_tab):
    # according to st.tabs container structure
    return st_tab._provided_cursor._parent_path[1]


#####################################
# CATEGORY
#####################################
@st.cache_data
def get_basis_categories_from_tab_id(tab_id):
    res = sql_category().select(
        values="*",
        where="tab_id=%d AND (difficulty = 'basis' OR difficulty = 'basis_advanced')" % tab_id,
    )
    return res


@st.cache_data
def get_basis_categories_display_names(tab_id):
    res = sql_category().select(
        values="display_name",
        where="tab_id=%d AND (difficulty = 'basis' OR difficulty = 'basis_advanced')" % tab_id,
    )
    return res


@st.cache_data
def get_categories_context_type_iri(tab_id):
    res = sql_category().select(
        values="context_type_iri",
        where="tab_id=%d AND (difficulty = 'basis' OR difficulty = 'basis_advanced')" % tab_id,
    )
    return res


@st.cache_data
def get_categories_context_type(tab_id):
    res = sql_category().select(
        values="context_type",
        where="tab_id=%d AND (difficulty = 'basis' OR difficulty = 'basis_advanced')" % tab_id,
    )
    return res


@st.cache_data
def get_categories_context_type_from_id(id):
    res = sql_category().select(values="context_type", where="id=%d " % id)

    return res[0][0]


@st.cache_data
def get_advanced_categories_from_tab_id(tab_id):
    res = sql_category().select(
        values="*",
        where="tab_id=%d AND (difficulty = 'advanced' or difficulty = 'basis_advanced')" % tab_id,
    )
    return res


#####################################
# COMPONENT
#####################################
@st.cache_data
def get_material_components_from_category_id(category_id, model_name):
    res = sql_component().select(
        values="*",
        where="category_id=%d AND material = %d and model_name = '%s' AND (difficulty = 'basis' OR difficulty = 'basis_advanced')"
        % (category_id, 1, model_name),
    )
    return res


@st.cache_data
def get_non_material_components_from_category_id(category_id, model_name):
    res = sql_component().select(
        values="*",
        where="category_id=%d AND material = %d AND model_name = '%s' AND (difficulty = 'basis' OR difficulty = 'basis_advanced')"
        % (category_id, 0, model_name),
    )
    return np.squeeze(res)


@st.cache_data
def get_advanced_components_from_category_id(category_id, model_name):
    res = sql_component().select(
        values="*",
        where="category_id=%d AND model_name = '%s' AND (difficulty = 'advanced' OR difficulty = 'basis_advanced')"
        % (category_id, model_name),
    )
    return np.squeeze(res)


@st.cache_data
def get_n_to_p_component_by_tab_id(tab_id):
    res = sql_component().select(
        values="*",
        where="tab_id=%d AND material = 0 AND (difficulty = 'basis' OR difficulty = 'basis_advanced')"
        % tab_id,
    )
    return np.squeeze(res)


@st.cache_data
def get_components_context_type_from_id(id):
    res = sql_component().select(values="context_type", where="id=%d " % id)
    return res[0][0]


#####################################
# MATERIAL
#####################################
@st.cache_data
def get_material_from_component_id(model_name, component_id):
    res = sql_material().select(
        values="*",
        where="""model_name = '{}' AND is_shown_to_user = 'True' AND (component_id_1={} or component_id_2={}) AND id IN (
            SELECT MIN(id)  
            FROM material
            GROUP BY name
        )""".format(
            model_name, component_id, component_id
        ),
    )
    return res


@st.cache_data
def get_material_names_from_component_id(component_id):
    res = sql_material().select(
        values="display_name",
        where="component_id_1=%d or component_id_2=%d " % (component_id, component_id),
    )
    return [a[0] for a in res]


@st.cache_data
def get_material_id_by_parameter_set_name_and_model_name(name, model_name):
    res = sql_material().select(
        values="id", where="name='%s' and model_name = '%s'" % (name, model_name)
    )
    print("parameter_set_name = ", name)
    print("material_id = ", res)
    return [a[0] for a in res]


@st.cache_data
def get_material_display_name_from_name(name, model_name):
    res = sql_material().select(
        values="display_name",
        where="name='%s' and model_name = '%s'" % (name, model_name),
    )
    return res


@st.cache_data
def get_material_id_by_display_name(name):
    res = sql_material().select(values="id", where="display_name='%s'" % name)
    return [a[0] for a in res]


@st.cache_data
def get_display_name_from_material_id(material_id):
    res = sql_material().select(values="display_name", where="id=%d " % material_id)
    return [a[0] for a in res]
    res = sql_material().select(values="display_name, reference_url", where="id=%d " % material_id)
    return tuple(res[0])


@st.cache_data
def get_all_default_material():
    res = sql_material().select(
        values="*",
        where="""default_material= '%s' AND context_type IS NOT NULL AND id IN (
            SELECT MIN(id)  
            FROM material
            GROUP BY name
        )"""
        % "True",
    )
    return res  # [a[0] for a in res]


@st.cache_data
def get_reference_url_from_parameter_set(parameter_set_name):
    res = sql_material().select_one(
        values='reference_url', where="display_name='%s'" % parameter_set_name
    )
    return res


#####################################
# PARAMETER
#####################################
@st.cache_data
def get_parameter_id_from_template_parameter_and_parameter_set(
    template_parameter_id, parameter_set_id
):
    return sql_parameter().get_id_from_template_parameter_id_and_parameter_set_id(
        template_parameter_id, parameter_set_id
    )


@st.cache_data
def get_parameter_id_from_template_parameters_and_parameter_set(
    template_parameter_ids, parameter_set_id
):
    return sql_parameter().get_id_from_template_parameter_ids_and_parameter_set_id(
        template_parameter_ids, parameter_set_id
    )


@st.cache_data
def get_parameter_from_template_parameter_id(template_parameter_id):
    res = sql_parameter().select(
        values="*", where="template_parameter_id = '%d'" % int(template_parameter_id)
    )
    return res


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


@st.cache_data
def extract_parameters_by_parameter_set_ids(parameter_set_ids):
    parameters = sql_parameter().get_all_by_parameter_set_ids(parameter_set_ids)
    parameter_dict = {}
    for param in parameters:
        id, _, set_id, *_ = param
        if set_id not in parameter_dict:
            parameter_dict[set_id] = []
        parameter_dict[set_id].append(param)
    return parameter_dict


@st.cache_data
def get_parameter_set_name_from_id(id):
    res = sql_parameter_set().select(values="name", where="id = %d" % id)
    return res[0]


@st.cache_data
def get_parameter_set_id_by_name(name):
    res = sql_parameter_set().select(values="id", where="name = '%s'" % name)
    return res[0][0]


@st.cache_data
def get_all_material_by_component_id(component_id):
    return sql_parameter_set().select(
        values="*", where="component_id=%d AND material = %d" % (component_id, 1)
    )


@st.cache_data
def get_parameter_sets_by_material_ids(material_ids):
    ids_str = ",".join(map(str, material_ids))
    return sql_parameter_set().select(
        values="*",
        where="""material_id IN (%s) AND id IN (
            SELECT MIN(id)  
            FROM parameter_set
            GROUP BY name
        )"""
        % ids_str,
    )


@st.cache_data
def get_mf_parameter_set_id_by_component_id(component_id):
    res = sql_parameter_set().select(
        values="id, name", where="component_id=%d AND material = %d" % (component_id, 0)
    )
    return res[0] if res else [None, None]


@st.cache_data
def get_n_p_parameter_set_id_by_component_id(component_id):
    res = np.squeeze(
        sql_parameter_set().select(
            values="id,name",
            where="component_id=%d AND material = %d" % (component_id, 0),
        )
    ).astype(str)

    return res[0], res[1] if res[0] else None


@st.cache_data
def get_non_material_set_id_by_component_id(component_id):
    res = sql_parameter_set().select(
        values="*", where="component_id=%d AND material = %d" % (component_id, 0)
    )
    return res[0]


@st.cache_data
def get_mf_raw_parameter_by_parameter_set_id(parameter_set_id):
    res = sql_parameter().select(
        values="*",
        where="parameter_set_id=%d AND name = 'mass_fraction'" % parameter_set_id,
    )
    return res


@st.cache_data
def get_n_p_parameter_by_template_id(parameter_set_id):
    res = sql_parameter().select(values="*", where="parameter_set_id=%d" % parameter_set_id)
    return res


@st.cache_data
def get_non_material_raw_parameters_by_template_parameter_ids_and_parameter_set_id(
    template_parameter_ids, parameter_set_id
):
    ids_str = ",".join(map(str, template_parameter_ids))
    res = sql_parameter().select(
        values="*",
        where="template_parameter_id IN ({}) AND parameter_set_id={}".format(
            ids_str, parameter_set_id
        ),
    )
    return res


@st.cache_data
def get_non_material_raw_parameter_by_template_parameter_id_and_parameter_set_id(
    template_parameter_id, parameter_set_id
):
    res = sql_parameter().select(
        values="*",
        where="template_parameter_id=%d AND parameter_set_id=%d"
        % (template_parameter_id, parameter_set_id),
    )
    return res


@st.cache_data
def get_advanced_parameters_by_parameter_set_id(template_parameter_id, parameter_set_id):
    res = sql_parameter().select(
        values="*",
        where="template_parameter_id=%d AND parameter_set_id=%d"
        % (int(template_parameter_id), int(parameter_set_id)),
    )
    return res[0] if res else None


@st.cache_data
def get_advanced_parameters_by_parameter_set_ids(template_parameter_ids, parameter_set_id):

    ids_str = ",".join(map(str, template_parameter_ids))
    # Ensure template_parameter_ids is a list or tuple
    if not isinstance(template_parameter_ids, (list, tuple)):
        raise ValueError("template_parameter_ids must be a list or tuple")

    # Convert parameter_set_id to int for safety
    parameter_set_id = int(parameter_set_id)

    # Execute the query with parameter values
    res = sql_parameter().select(
        values="*",
        where="template_parameter_id IN ({}) AND parameter_set_id = {}".format(
            ids_str, parameter_set_id
        ),
    )
    return res


#####################################
# MODEL
#####################################


def get_models_as_dict():

    models = sql_model().select(values="*", where="is_shown_to_user = '1'")
    models_as_dict = {}

    for model in models:
        model_id, model_name, _, _, _, _ = model

        models_as_dict[model_id] = model_name

    return models_as_dict


def get_model_name_from_id(model_id):
    model = sql_model().select(values="name", where="id = '{}'".format(model_id))

    return model[0][0]


# @st.cache_data
# def get_templates_by_id(model_id):
#     res = sql_model().select_one(
#         values="templates",
#         where="id=%d" % model_id
#     )
#     return eval(res[0]) if res else None


@st.cache_data
def get_model_parameters_as_dict(model_name):

    parameter_set_id = sql_parameter_set().get_id_from_name_and_model(model_name, model_name)
    parameters = sql_parameter().get_all_by_parameter_set_id(parameter_set_id)

    model_quantitative_properties = []

    for parameter in parameters:
        _, name, _, _, value = parameter

        template_parameter = sql_template_parameter().get_all_by_name(name)

        (
            _,
            _,
            _,
            _,
            _,
            _,
            context_type,
            context_type_iri,
            value_type,
            unit,
            unit_name,
            unit_iri,
            _,
            _,
            _,
            _,
            _,
        ) = template_parameter

        parameter_details = {"rdfs:label": name, "@type": context_type}
        if value_type == "bool":

            formatted_value_dict = {
                "@type": "Boolean",
                "hasNumericalValue": int(ast.literal_eval(value)),
            }
            parameter_details["hasNumericalPart"] = formatted_value_dict
        elif value_type == "str":
            formatted_value_dict = {"@type": "String", "hasStringValue": value}
            parameter_details["hasStringPart"] = formatted_value_dict

        elif value_type == "float":
            formatted_value_dict = {"@type": "Real", "hasNumericalValue": float(value)}
            parameter_details["hasNumericalPart"] = formatted_value_dict

            parameter_details["hasMeasurementUnit"] = {
                "hasSymbolValue": unit,
                "@type": unit_iri if unit_iri else None,
            }

        else:
            assert False, "model parameter type={} not handled. name={}".format(value_type, name)

        model_quantitative_properties.append(parameter_details)

    return model_quantitative_properties


@st.cache_data
def get_model_description(model_name):

    return sql_model().select(values="description", where="name='%s'" % model_name)


#####################################
# TEMPLATE
#####################################
@st.cache_data
def get_material_template_parameters_from_template_id(template_id):
    return sql_template_parameter().get_all_material_by_template_id(template_id)


@st.cache_data
def get_template_from_name(name):
    res = sql_template_parameter().select(values="*", where="name ='%s'" % name)
    return res[0]


@st.cache_data
def get_parameters_by_template_parameter_ids(template_parameter_ids, model_name):
    ids_str = ",".join(map(str, template_parameter_ids))
    res = sql_template_parameter().select(
        values="*",
        where="id IN (%s) AND model_name = '%s'" % (ids_str, model_name),
    )
    return res


@st.cache_data
def get_parameter_by_template_parameter_id(template_parameter_id, model_name):
    res = sql_template_parameter().select(
        values="*",
        where="id = '%s' AND model_name = '%s'" % (template_parameter_id, model_name),
    )
    return res[0]


def reset_material_template_parameters(template_id):
    sql_template_parameter().update(
        set="difficulty = 'advanced'",
        where="par_class ='material' AND template_id = {}".format(int(template_id)),
    )


def set_material_template_parameters_to_basis_by_id(template_parameter_id):
    sql_template_parameter().update(
        set="difficulty = 'basis'", where="id = {}".format(int(template_parameter_id))
    )


@st.cache_data
def get_all_material_by_template_id(template_id, model_name):
    return sql_template_parameter().select(
        values="*",
        where="template_id={} AND par_class = '{}' AND model_name = '{}'".format(
            template_id, "material", model_name
        ),
    )


@st.cache_data
def get_all_basis_material_by_template_id(template_id, model_name):
    return sql_template_parameter().select(
        values="*",
        where="template_id={} AND par_class = '{}' AND model_name = '{}' AND difficulty = 'basis'".format(
            template_id, "material", model_name
        ),
    )


def get_mf_template_by_template_id(template_id, model_name):
    return sql_template_parameter().select(
        values="*",
        where="template_id=%d AND name = '%s' and model_name = '%s'"
        % (template_id, "mass_fraction", model_name),
    )


@st.cache_data
def get_non_material_template_by_template_id(template_id, model_name):
    return sql_template_parameter().select(
        values="*",
        where="template_id={} AND par_class = '{}' AND model_name = '{}' AND difficulty = 'basis' AND is_shown_to_user = 'True'".format(
            template_id, "non_material", model_name
        ),
    )


def get_advanced_template_by_template_id(template_id, model_name):
    res = sql_template_parameter().select(
        values="*",
        where="template_id={} AND model_name = '{}' AND difficulty = 'advanced' AND is_shown_to_user = 'True'".format(
            template_id, model_name
        ),
    )
    return res


@st.cache_data
def get_n_p_template_by_template_id(template_id):
    return sql_template_parameter().select(
        values="*",
        where="template_id=%d AND par_class = '%s' AND (difficulty = 'basis' OR difficulty = 'basis_advanced')"
        % (template_id, "non_material"),
    )


@st.cache_data
def get_template_parameter_by_parameter_name(parameter_name, model_name):
    return sql_template_parameter().select(
        values="*",
        where="name='%s' and model_name = '%s'" % (parameter_name, model_name),
    )


# all_basis_tab_display_names = get_basis_tabs_display_names(model_id)
# all_advanced_tab_display_names = get_advanced_tabs_display_names()
# all_tab_display_names = get_tabs_display_names()
# all_tab_names = get_tabs_names()
# all_tab_id = st_tab_id_to_db_tab_id()
