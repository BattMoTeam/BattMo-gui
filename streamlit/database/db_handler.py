import numpy as np
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import db_BaseHandler as db


#####################################
# PARAMETER
#####################################
class ParameterHandler(db.BaseHandler):
    def __init__(self):
        self._table_name = "parameter"
        self._columns = "name, parameter_set_id, template_parameter_id, value"

    def insert_value(self, name, parameter_set_id, template_parameter_id, value=None):
        assert name is not None, "parameter's name can't be None"
        assert parameter_set_id is not None, "parameter's parameter_set_id can't be None"
        assert template_parameter_id is not None, "parameter's template_parameter_id can't be None"

        return self._insert_value_query(
            columns_and_values={
                "name": name,
                "value": value,
                "parameter_set_id": parameter_set_id,
                "template_parameter_id": template_parameter_id,
            }
        )

    def get_id_from_name_and_parameter_set_id(self, name, parameter_set_id):
        res = self.select_one(
            values="id",
            where="name='%s' and parameter_set_id=%d" % (name, parameter_set_id),
        )
        return res[0] if res else None

    def create_index(self, index_name, columns):
        return self._create_index(index_name, self._table_name, columns)

    def get_all_ids_by_parameter_set_id(self, parameter_set_id):
        res = self.select(values="id", where="parameter_set_id=%d" % parameter_set_id)
        return [a[0] for a in res]

    def get_all_by_parameter_set_id(self, parameter_set_id):
        res = self.select(
            values="*",
            where="parameter_set_id=%d  " % (parameter_set_id),
        )
        return res

    def get_all_by_parameter_set_ids(self, parameter_set_id):
        ids_str = ",".join(map(str, parameter_set_id))
        res = self.select(
            values="*",
            where="parameter_set_id IN (%s)" % ids_str,
        )
        return res

    def get_id_from_template_parameter_id_and_parameter_set_id(
        self, template_parameter_id, parameter_set_id
    ):
        res = self.select_one(
            values="id",
            where="template_parameter_id=%d and parameter_set_id=%d"
            % (int(template_parameter_id), int(parameter_set_id)),
        )
        return res[0] if res else None

    def get_id_from_template_parameter_ids_and_parameter_set_id(
        self, template_parameter_ids, parameter_set_id
    ):
        ids_str = ",".join(map(str, template_parameter_ids))
        res = self.select(
            values="id,template_parameter_id",
            where="template_parameter_id IN ({}) and parameter_set_id={}".format(
                ids_str, int(parameter_set_id)
            ),
        )
        return [sub_res for sub_res in res]


#####################################
# PARAMETER SET
#####################################
class ParameterSetHandler(db.BaseHandler):
    def __init__(self):
        self._table_name = "parameter_set"
        self._columns = "name, component_id, material"

    def insert_value(self, name, component_id, material, model_name, material_id):
        assert name is not None, "parameter_set's name can't be None"
        # assert component_id is not None, "parameter_set's component_id can't be None"
        # assert material is not None, "parameter_set's component_id can't be None"

        return self._insert_value_query(
            columns_and_values={
                "name": name,
                "component_id": component_id,
                "material": material,
                "model_name": model_name,
                "material_id": material_id,
            }
        )

    def get_id_by_name_and_category_and_model_name(self, name, component_id, model_name):
        res = self.select_one(
            values="*",
            where="name = '%s' and component_id Like %d and model_name = '%s'"
            % (name, component_id, model_name),
        )
        return res[0] if res else None

    def create_index(self, index_name, columns):
        return self._create_index(index_name, self._table_name, columns)

    def get_all_by_category_id(self, category_id):
        return self.select(values="*", where="category_id=%d" % category_id)

    def get_all_by_component_id(self, component_id):
        return self.select(values="*", where="component_id=%d" % component_id)

    def get_material_from_name(self, name):
        return self.select(values="material", where="name='%s'" % name)

    def get_id_from_name_and_model(self, name, model_name):
        return self.select_one(
            values="id", where="name = '%s' AND model_name='%s'" % (name, model_name)
        )

    def get_id_from_name(self, name):
        res = self.select_one(values="id", where="name='%s'" % name)
        return res[0] if res else None


#####################################
# TEMPLATE
#####################################
class TemplateHandler(db.BaseHandler):
    def __init__(self):
        self._table_name = "template"
        self._columns = "name"
        self.full_template = "full_template"

    def insert_value(self, name):
        assert name is not None, "parameter_set's name can't be None"

        return self._insert_value_query(columns_and_values={"name": "{}".format(name)})

    def get_id_from_name_and_model_name(self, name, model_name):
        res = self.select_one(
            values="id", where="name='%s' and model_name = '%s'" % (name, model_name)
        )
        return res[0] if res else None

    def get_id_from_name(self, name):
        res = self.select_one(values="id", where="name='%s'" % (name))
        return res[0] if res else None


#####################################
# TEMPLATE PARAMETER
#####################################
class TemplateParameterHandler(db.BaseHandler):
    def __init__(self):
        self._table_name = "template_parameter"
        self._columns = "name, template_id,model_name,par_class,difficulty, context_type, context_type_iri, type, unit, unit_name, unit_iri, max_value, min_value, is_shown_to_user, description, display_name"
        self.types_handled = {"str", "bool", "int", "float", "function"}
        self.assert_all_types_are_handled()

    def insert_value(
        self,
        name,
        template_id,
        model_name,
        par_class,
        difficulty,
        context_type=None,
        context_type_iri=None,
        type=None,
        unit=None,
        unit_name=None,
        unit_iri=None,
        max_value=None,
        min_value=None,
        is_shown_to_user=True,
        description=None,
        display_name=None,
    ):
        assert name is not None, "template parameter's name can't be None"
        assert template_id is not None, "template parameter's template_id can't be None"
        # assert model_id is not None, "template parameter's model_id can't be None"

        return self._insert_value_query(
            columns_and_values={
                "name": name,
                "template_id": template_id,
                "model_name": model_name,
                "par_class": par_class,
                "difficulty": difficulty,
                "context_type": context_type,
                "context_type_iri": context_type_iri,
                "type": type,
                "unit": unit,
                "unit_name": unit_name,
                "unit_iri": unit_iri,
                "max_value": max_value,
                "min_value": min_value,
                "is_shown_to_user": is_shown_to_user,
                "description": description,
                "display_name": display_name,
            }
        )

    def get_model_id_from_model_name(self, model_name):
        return self.select(values="id", where="model_name=%s" % model_name)

    def create_index(self, index_name, columns):
        return self._create_index(index_name, self._table_name, columns)

    def get_id_from_name_and_template_id(self, name, template_id, model_name):
        res = self.select_one(
            values="id",
            where="name='%s' and template_id=%d and model_name = '%s'"
            % (name, template_id, model_name),
        )
        return res[0] if res else None

    def get_all_ids_by_template_id(self, template_id):
        res = self.select(values="id", where="template_id=%d" % template_id)
        return [a[0] for a in res]

    def get_all_by_name(self, name):
        res = self.select(values="*", where="name='%s'" % name)
        return res[0]

    def get_all_by_template_id(self, template_id):
        return self.select(values="*", where="template_id=%d" % template_id)

    def get_id_name_and_type_by_template_id(self, template_id, model_name):
        return self.select(
            values="id, name, type",
            where="template_id=%d and model_name = '%s'" % (template_id, model_name),
        )

    def get_all_types(self):
        res = self.select(values="type")
        return set([a[0] for a in res]) if res else None

    def assert_all_types_are_handled(self):
        """
        Parameters are formatted in app_parameter_model.py
        Its code has to handle all the parameter types existing in db
        """
        all_types = self.get_all_types()
        if all_types:
            assert all_types.issubset(self.types_handled), (
                "\n Not all parameter types are handled. Please handle missing type in app_parameter_model.py"
                "\n types_handled={} \n all_types={}".format(self.types_handled, all_types)
            )


#####################################
# MODEL
#####################################
class ModelHandler(db.BaseHandler):
    def __init__(self):
        self._table_name = "model"
        self._columns = "name, show_to_user, description"

    def insert_value(
        self,
        name,
        model_name,
        is_shown_to_user,
        default_template,
        templates="{}",
        description="",
    ):
        assert name is not None, "Model's name can't be None"

        return self._insert_value_query(
            columns_and_values={
                "name": name,
                "model_name": model_name,
                "is_shown_to_user": is_shown_to_user,
                "default_template": default_template,
                "description": description,
            }
        )

    def get_model_id_from_model_name(self, name):
        res = self.select_one(values="id", where="name='%s'" % name)
        return res[0]

    def get_default_template_name_by_name_and_model_name(self, name, model_name):
        res = self.select_one(
            values="default_template",
            where="name='%s' and model_name = '%s'" % (name, model_name),
        )
        return res[0]


#####################################
# MODEL PARAMETER
#####################################
class ModelParameterHandler(db.BaseHandler):
    def __init__(self):
        self._table_name = "model_parameter"
        self._columns = "name, value, type, unit, unit_name, unit_iri, description"

    def insert_value(
        self,
        name,
        model_id,
        value=None,
        type=None,
        unit=None,
        unit_name=None,
        unit_iri=None,
        description="",
    ):
        assert name is not None, "Model parameter's name can't be None"
        assert model_id is not None, "Model parameter's model_id can't be None"

        return self._insert_value_query(
            columns_and_values={
                "name": name,
                "value": value,
                "type": type,
                "unit": unit,
                "unit_name": unit_name,
                "unit_iri": unit_iri,
                "description": description,
            }
        )

    def get_id_from_name_and_model_id(self, name, model_id):
        res = self.select_one(values="id", where="name='%s' and model_id=%d" % (name, model_id))
        return res[0] if res else None

    def get_all_ids_by_model_id(self, model_id):
        res = self.select(values="id", where="model_id=%d" % model_id)
        return [a[0] for a in res]

    @st.cache_data
    def get_all_by_model_id(_self, model_id):
        return _self.select(values="*", where="model_id=%d" % model_id)


#####################################
# TAB
#####################################
class TabHandler(db.BaseHandler):
    def __init__(self):
        self._table_name = "tab"
        self._columns = "name, model_name, difficulty, display_name, context_type, context_type_iri, description"

    def insert_value(
        self,
        name,
        model_name,
        difficulty,
        display_name,
        context_type=None,
        context_type_iri=None,
        description="",
    ):
        assert name is not None, "Tab's name can't be None"
        assert display_name is not None, "Tab's display_name can't be None"

        return self._insert_value_query(
            columns_and_values={
                "name": name,
                "model_name": model_name,
                "difficulty": difficulty,
                "context_type": context_type,
                "context_type_iri": context_type_iri,
                "display_name": display_name,
                "description": description,
            }
        )

    def get_model_id_from_model_name(self, model_name):
        return self.select(values="id", where="model_name=%s" % model_name)

    def get_id_from_name_and_model(self, name, model_name):
        res = self.select_one(
            values="id", where="name = '%s' AND model_name='%s'" % (name, model_name)
        )
        return res

    def create_index(self, index_name, columns):
        return self._create_index(index_name, self._table_name, columns)


#####################################
# CATEGORY
#####################################
class CategoryHandler(db.BaseHandler):
    def __init__(self):
        self._table_name = "category"
        self._columns = "name, model_name, difficulty, context_type, context_type_iri, emmo_relation, display_name, tab_id, default_template_id, description"

    def insert_value(
        self,
        name,
        tab_id,
        default_template_id,
        context_type=None,
        model_name=None,
        difficulty=None,
        context_type_iri=None,
        emmo_relation=None,
        display_name=None,
        description="",
    ):
        assert name is not None, "Category's name can't be None"
        assert tab_id is not None, "Category's tab_id can't be None"
        assert default_template_id is not None, "Category's default_template_id can't be None"
        print("model = ", model_name)
        return self._insert_value_query(
            columns_and_values={
                "name": name,
                "model_name": model_name,
                "difficulty": difficulty,
                "context_type": context_type,
                "context_type_iri": context_type_iri,
                "emmo_relation": emmo_relation,
                "display_name": display_name,
                "tab_id": tab_id,
                "default_template_id": default_template_id,
                "description": description,
            }
        )

    @st.cache_data
    def get_all_by_tab_id(_self, tab_id):
        return _self.select(values="*", where="tab_id=%d" % tab_id)

    def create_index(self, index_name, columns):
        return self._create_index(index_name, self._table_name, columns)

    def get_model_id_from_model_name(self, model_name):
        return self.select(values="id", where="model_name=%s" % model_name)

    def get_id_from_name_and_model(self, name, model_name):
        return self.select(
            values="id", where="name = '%s' AND model_name='%s'" % (name, model_name)
        )

    def get_default_template_id_by_id(self, id):
        res = self.select_one(values="default_template_id", where="id={}".format(id))
        return res[0] if res else None


#####################################
# COMPONENT
#####################################
class ComponentHandler(db.BaseHandler):
    def __init__(self):
        self._table_name = "component"
        self._columns = "name, model_name, difficulty,material, context_type, context_type_iri, emmo_relation, display_name, category_id, default_template_id, description"

    def insert_value(
        self,
        name,
        material,
        default_template_id,
        category_id=None,
        tab_id=None,
        model_name=None,
        difficulty=None,
        context_type=None,
        context_type_iri=None,
        emmo_relation=None,
        display_name=None,
        description="",
    ):
        assert name is not None, "Category's name can't be None"
        # assert category_id is not None, "Components's category_id can't be None"
        assert default_template_id is not None, "Category's default_template_id can't be None"

        return self._insert_value_query(
            columns_and_values={
                "name": name,
                "model_name": model_name,
                "difficulty": difficulty,
                "material": material,
                "context_type": context_type,
                "context_type_iri": context_type_iri,
                "emmo_relation": emmo_relation,
                "display_name": display_name,
                "category_id": category_id,
                "tab_id": tab_id,
                "default_template_id": default_template_id,
                "description": description,
            }
        )

    # def get_all_by_category_id(self, category_id):
    #     return self.select(
    #         values='*',
    #         where='category_id=%d' % category_id
    #     )
    def get_model_id_from_model_name(self, model_name):
        return self.select(values="id", where="model_name=%s" % model_name)

    def create_index(self, index_name, columns):
        return self._create_index(index_name, self._table_name, columns)

    @st.cache_data
    def get_all_by_category_id(_self, category_id):
        return _self.select(values="*", where="category_id=%d" % category_id)

    def get_id_from_name_and_model(self, name, model_name):
        return self.select(
            values="id", where="name = '%s' AND model_name='%s'" % (name, model_name)
        )

    def get_default_template_id_by_id(self, id):
        res = self.select_one(values="default_template_id", where="id={}".format(id))
        return res[0] if res else None


#####################################
# MATERIAL
#####################################
class MaterialHandler(db.BaseHandler):
    def __init__(self):
        self._table_name = "material"
        self._columns = "name, model_name, difficulty, is_shown_to_user, context_type, context_type_iri, emmo_relation, display_name, tab_id, default_template_id, description"

    def insert_value(
        self,
        name,
        component_id_1,
        component_name_1,
        is_shown_to_user,
        number_of_components,
        default_material,
        model_name=None,
        component_id_2=None,
        difficulty=None,
        reference_name=None,
        reference=None,
        reference_url=None,
        context_type=None,
        component_name_2=None,
        context_type_iri=None,
        emmo_relation=None,
        display_name=None,
        description="",
    ):
        assert name is not None, "Category's name can't be None"
        assert component_id_1 is not None, "Category's component_id_1 can't be None"
        assert default_material is not None, "Category's default_material can't be None"
        print(model_name)
        return self._insert_value_query(
            columns_and_values={
                "name": name,
                "model_name": model_name,
                "difficulty": difficulty,
                "is_shown_to_user": is_shown_to_user,
                "reference_name": reference_name,
                "reference": reference,
                "reference_url": reference_url,
                "context_type": context_type,
                "context_type_iri": context_type_iri,
                "emmo_relation": emmo_relation,
                "display_name": display_name,
                "component_id_1": component_id_1,
                "component_id_2": component_id_2,
                "default_material": default_material,
                "number_of_components": number_of_components,
                "component_name_1": component_name_1,
                "component_name_2": component_name_2,
                "description": description,
            }
        )

    # def get_all_by_tab_id(self, tab_id):
    #     return self.select(
    #         values='*',
    #         where='tab_id=%d' % tab_id
    #     )
    def get_model_id_from_model_name(self, model_name):
        return self.select(values="id", where="model_name=%s" % model_name)

    def create_index(self, index_name, columns):
        return self._create_index(index_name, self._table_name, columns)

    def get_id_from_name_and_model(self, name, model_name):
        return self.select(
            values="id", where="name = '%s' AND model_name='%s'" % (name, model_name)
        )

    @st.cache_data
    def get_all_by_component_id(_self, component_id):
        return _self.select(values="*", where="component_id=%d" % component_id)

    # def get_default_template_id_by_id(self, id):
    #     res = self.select_one(
    #         values="default_template_id",
    #         where="id={}".format(id)
    #     )
    #     return res[0] if res else None
