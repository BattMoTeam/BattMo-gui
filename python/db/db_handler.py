from .db_BaseHandler import BaseHandler


class ParameterHandler(BaseHandler):
    def __init__(self):
        self._table_name = "parameter"
        self._columns = "name, value, value_type, parameter_set_id, is_shown_to_user"

    def insert_value(self, name, value, value_type, parameter_set_id, is_shown_to_user=True):
        return self._insert_value_query(
            values=(name, value, value_type, parameter_set_id, is_shown_to_user)
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


class ParameterSetHandler(BaseHandler):
    def __init__(self):
        self._table_name = "parameter_set"
        self._columns = "name, category_id, header_id"

    def insert_value(self, name, category_id, headers_id):
        return self._insert_value_query(
            values=(name, category_id, headers_id)
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
        self._columns = "name, description"

    def insert_value(self, name, description):
        assert name is not None, "Category's name can't be None"

        if description:
            return self._insert_value_query(
                values=(name, description)
            )
        else:
            return self._insert_value_query(
                values=(name, "")
            )


class ParameterSetHeaderHandler(BaseHandler):
    def __init__(self):
        self._table_name = "parameter_set_header"
        self._columns = "doi, description"

    def insert_value(self, doi, description):
        return self._insert_value_query(
            values=(doi, description)
        )

    def get_id_from_doi(self, doi):
        res = self.select_one(
            values="id",
            where="doi='%s'" % doi
        )
        return res[0] if res else None
