from . import db_handler


class DBHelper:

    def __init__(self):
        self.sql_parameter = db_handler.ParameterHandler()
        self.sql_parameter_set = db_handler.ParameterSetHandler()
        self.sql_category = db_handler.CategoryHandler()
        self.sql_tab = db_handler.TabHandler()
        self.sql_parameter_set_header = db_handler.ParameterSetHeaderHandler()
        self.all_tab_display_names = self.get_tabs_display_names()
        self.all_tab_names = self.get_tabs_names()
        self.all_tab_id = self.st_tab_id_to_db_tab_id()

    def get_tabs_display_names(self):
        res = self.sql_tab.select(
            values='display_name'
        )
        return [a[0] for a in res]

    def get_tabs_names(self):
        res = self.sql_tab.select(
            values='name'
        )
        return [a[0] for a in res]

    def st_tab_id_to_db_tab_id(self):
        res = self.sql_tab.select(
            values='id'
        )
        return [a[0] for a in res]

    def get_tab_index_from_st_tab(self, st_tab):
        # according to st.tabs container structure
        return st_tab._provided_cursor._parent_path[1]

    def get_categories_from_tab_id(self, tab_id):
        res = self.sql_category.get_all_by_tab_id(tab_id)
        return res

    def get_all_parameter_sets_by_category_id(self, category_id):
        res = self.sql_parameter_set.get_all_by_category_id(category_id)
        return [a[1] for a in res]

    def extract_parameters_by_parameter_set_name(self, parameter_set_name):
        parameter_set_id = self.sql_parameter_set.get_id_from_name(parameter_set_name)
        return self.sql_parameter.get_all_by_parameter_set_id(parameter_set_id)
