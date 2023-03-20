from .db_BaseHandler import BaseHandler


#####################################
# PARAMETER
#####################################
class ParameterHandler(BaseHandler):
    def __init__(self):
        self._table_name = "parameter"
        self._columns = "name, parameter_set_id, template_parameter_id, value"

    def insert_value(
            self,
            name,
            parameter_set_id,
            template_parameter_id,
            value=None
    ):
        assert name is not None, "parameter's name can't be None"
        assert parameter_set_id is not None, "parameter's parameter_set_id can't be None"
        assert template_parameter_id is not None, "parameter's template_parameter_id can't be None"

        return self._insert_value_query(
            values=None,
            specify_columns=True,
            columns_and_values={
                "name": name,
                "value": value,
                "parameter_set_id": parameter_set_id,
                "template_parameter_id": template_parameter_id
            }
        )

    def get_id_from_name_and_parameter_set_id(self, name, parameter_set_id):
        res = self.select_one(
            values="id",
            where="name='%s' and parameter_set_id=%d" % (name, parameter_set_id)
        )
        return res[0] if res else None

    def get_all_ids_by_parameter_set_id(self, parameter_set_id):
        res = self.select(
            values='id',
            where='parameter_set_id=%d' % parameter_set_id
        )
        return [a[0] for a in res]

    def get_all_by_parameter_set_id(self, parameter_set_id):
        return self.select(
            values='*',
            where='parameter_set_id=%d' % parameter_set_id
        )


#####################################
# PARAMETER SET
#####################################
class ParameterSetHandler(BaseHandler):
    def __init__(self):
        self._table_name = "parameter_set"
        self._columns = "name, category_id"

    def insert_value(self, name, category_id):
        assert name is not None, "parameter_set's name can't be None"
        assert category_id is not None, "parameter_set's category_id can't be None"

        return self._insert_value_query(
            values=(name, category_id)
        )

    def get_id_by_name_and_category(self, name, category_id):
        res = self.select_one(
            values="*",
            where="name = '%s' and category_id = %d" % (name, category_id)
        )
        return res[0] if res else None

    def get_all_by_category_id(self, category_id):
        return self.select(
            values='*',
            where='category_id=%d' % category_id
        )


#####################################
# TEMPLATE
#####################################
class TemplateHandler(BaseHandler):
    def __init__(self):
        self._table_name = "template"
        self._columns = "name"
        self.full_template = "full_template"

    def insert_value(self, name):
        assert name is not None, "parameter_set's name can't be None"

        return self._insert_value_query(
            values=("'{}'".format(name),)
        )


#####################################
# TEMPLATE PARAMETER
#####################################
class TemplateParameterHandler(BaseHandler):
    def __init__(self):
        self._table_name = "template_parameter"
        self._columns = "name, template_id, type, unit_name, unit_dimension, max_value, min_value, is_shown_to_user, description"
        self.types_handled = {'str', 'bool', 'int', 'float', 'function'}
        self.assert_all_types_are_handled()

    def insert_value(
            self,
            name,
            template_id,
            type=None,
            unit_name=None,
            unit_dimension=None,
            max_value=None,
            min_value=None,
            is_shown_to_user=True,
            description=None
    ):
        assert name is not None, "template parameter's name can't be None"
        assert template_id is not None, "template parameter's template_id can't be None"

        return self._insert_value_query(
            values=None,
            specify_columns=True,
            columns_and_values={
                "name": name,
                "template_id": template_id,
                "type": type,
                "unit_name": unit_name,
                "unit_dimension": unit_dimension,
                "max_value": max_value,
                "min_value": min_value,
                "is_shown_to_user": is_shown_to_user,
                "description": description
            }
        )

    def get_id_from_name_and_template_id(self, name, template_id):
        res = self.select_one(
            values="id",
            where="name='%s' and template_id=%d" % (name, template_id)
        )
        return res[0] if res else None

    def get_all_ids_by_template_id(self, template_id):
        res = self.select(
            values='id',
            where='template_id=%d' % template_id
        )
        return [a[0] for a in res]

    def get_all_by_template_id(self, template_id):
        return self.select(
            values='*',
            where='template_id=%d' % template_id
        )

    def get_id_name_and_type_by_template_id(self, template_id):
        return self.select(
            values='id, name, type',
            where='template_id=%d' % template_id
        )

    def get_all_types(self):
        res = self.select(values="type")
        return set([a[0] for a in res])

    def assert_all_types_are_handled(self):
        """
        Parameters are formatted in app_parameter_model.py
        Its code has to handle all the parameter types existing in db
        """
        all_types = self.get_all_types()
        assert all_types.issubset(self.types_handled), \
            "\n Not all parameter types are handled. Please handle missing type in app_parameter_model.py" \
            "\n types_handled={} \n all_types={}".format(self.types_handled, all_types)


#####################################
# MODEL
#####################################
class ModelHandler(BaseHandler):
    def __init__(self):
        self._table_name = "model"
        self._columns = "name, templates, description"

    def insert_value(self, name, templates="{}", description=""):
        assert name is not None, "Model's name can't be None"

        return self._insert_value_query(
            values=None,
            specify_columns=True,
            columns_and_values={
                "name": name,
                "templates": templates,
                "description": description
            }
        )


#####################################
# MODEL PARAMETER
#####################################
class ModelParameterHandler(BaseHandler):
    def __init__(self):
        self._table_name = "model_parameter"
        self._columns = "name, model_id, value, type, description"

    def insert_value(self, name, model_id, value=None, type=None, description=""):
        assert name is not None, "Model parameter's name can't be None"
        assert model_id is not None, "Model parameter's model_id can't be None"

        return self._insert_value_query(
            values=None,
            specify_columns=True,
            columns_and_values={
                "name": name,
                "model_id": model_id,
                "value": value,
                "type": type,
                "description": description
            }
        )

    def get_id_from_name_and_model_id(self, name, model_id):
        res = self.select_one(
            values="id",
            where="name='%s' and model_id=%d" % (name, model_id)
        )
        return res[0] if res else None

    def get_all_ids_by_model_id(self, model_id):
        res = self.select(
            values='id',
            where='model_id=%d' % model_id
        )
        return [a[0] for a in res]

    def get_all_by_model_id(self, model_id):
        return self.select(
            values='*',
            where='model_id=%d' % model_id
        )


#####################################
# TAB
#####################################
class TabHandler(BaseHandler):
    def __init__(self):
        self._table_name = "tab"
        self._columns = "name, display_name, description"

    def insert_value(self, name, display_name, description=""):
        assert name is not None, "Tab's name can't be None"
        assert display_name is not None, "Tab's display_name can't be None"

        return self._insert_value_query(
            values=(name, display_name, description)
        )


#####################################
# CATEGORY
#####################################
class CategoryHandler(BaseHandler):
    def __init__(self):
        self._table_name = "category"
        self._columns = "name, display_name, tab_id, default_template_id, description"

    def insert_value(self, name, tab_id, default_template_id, display_name=None, description=""):
        assert name is not None, "Category's name can't be None"
        assert tab_id is not None, "Category's tab_id can't be None"
        assert default_template_id is not None, "Category's default_template_id can't be None"

        return self._insert_value_query(
            values=None,
            specify_columns=True,
            columns_and_values={
                "name": name,
                "display_name": display_name,
                "tab_id": tab_id,
                "default_template_id": default_template_id,
                "description": description
            }
        )

    def get_all_by_tab_id(self, tab_id):
        return self.select(
            values='*',
            where='tab_id=%d' % tab_id
        )

    def get_default_template_id_by_id(self, id):
        res = self.select_one(
            values="default_template_id",
            where="id={}".format(id)
        )
        return res[0] if res else None
