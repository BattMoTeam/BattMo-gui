from .db_BaseHandler import BaseHandler


class ParameterHandler(BaseHandler):
    def __init__(self):
        self._table_name = "parameter"
        self._columns = "name, value, type, unit_name, unit_dimension, max_value, min_value, parameter_set_id, is_shown_to_user, description"
        self.types_handled = {'str', 'bool', 'int', 'float', 'function'}
        self.assert_all_types_are_handled()

    def insert_value(
            self,
            name,
            parameter_set_id,
            value=None,
            type=None,
            unit_name=None,
            unit_dimension=None,
            max_value=None,
            min_value=None,
            is_shown_to_user=True,
            description=None
    ):
        assert name is not None, "parameter's name can't be None"
        assert parameter_set_id is not None, "parameter's name can't be None"

        return self._insert_value_query(
            values=None,
            specify_columns=True,
            columns_and_values={
                "name": name,
                "value": value,
                "type": type,
                "unit_name": unit_name,
                "unit_dimension": unit_dimension,
                "max_value": max_value,
                "min_value": min_value,
                "parameter_set_id": parameter_set_id,
                "is_shown_to_user": is_shown_to_user,
                "description": description
            }
        )

    def get_id_from_name_and_parameter_set_id(self, name, parameter_set_id):
        res = self.select_one(
            values="id",
            where="name='%s' and parameter_set_id=%d" % (name,parameter_set_id)
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

    def get_all_types(self):
        res = self.select(values="type")
        return set([a[0] for a in res])

    def assert_all_types_are_handled(self):
        """
        Parameters are formatted in app_parameter_model.py
        Its code has to handle all the parameter types existing in db
        """
        all_types = self.get_all_types()
        assert all_types == self.types_handled, \
            "\n Not all parameter types are handled. Please handle missing type in app_parameter_model.py" \
            "\n types_handled={} \n all_types={}".format(self.types_handled, all_types)


class ParameterSetHandler(BaseHandler):
    def __init__(self):
        self._table_name = "parameter_set"
        self._columns = "name, category_id, header_id"

    def insert_value(self, name, category_id, header_id):
        assert name is not None, "parameter_set's name can't be None"
        assert category_id is not None, "parameter_set's category_id can't be None"
        assert header_id is not None, "parameter_set's header_id can't be None"

        return self._insert_value_query(
            values=(name, category_id, header_id)
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


class CategoryHandler(BaseHandler):
    def __init__(self):
        self._table_name = "category"
        self._columns = "name, display_name, tab_id, description"

    def insert_value(self, name, tab_id, display_name=None, description=""):
        assert name is not None, "Category's name can't be None"
        assert tab_id is not None, "Category's tab_id can't be None"

        return self._insert_value_query(
            values=None,
            specify_columns=True,
            columns_and_values={
                "name": name,
                "display_name": display_name,
                "tab_id": tab_id,
                "description": description
            }
        )

    def get_all_by_tab_id(self, tab_id):
        return self.select(
            values='*',
            where='tab_id=%d' % tab_id
        )


class TabHandler(BaseHandler):
    def __init__(self):
        self._table_name = "tab"
        self._columns = "name, display_name, description"

    def insert_value(self, name, display_name, description=""):
        assert name is not None, "Tab's name can't be None"
        assert display_name is not None, "Tab's name can't be None"

        return self._insert_value_query(
            values=(name, display_name, description)
        )


class ParameterSetHeaderHandler(BaseHandler):
    def __init__(self):
        self._table_name = "parameter_set_header"
        self._columns = "doi, description"

    def insert_value(self, doi, description=""):
        assert doi is not None, "parameter_set_header's doi can't be None"
        return self._insert_value_query(
            values=None,
            specify_columns=True,
            columns_and_values={
                "doi": doi,
                "description": description
            }
        )

    def get_id_from_doi(self, doi):
        res = self.select_one(
            values="id",
            where="doi='%s'" % doi
        )
        return res[0] if res else None
