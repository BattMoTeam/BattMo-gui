from . import db_handler


class DBHelper:

    def __init__(self):
        self.sql_parameter = db_handler.ParameterHandler()
        self.sql_parameter_set = db_handler.ParameterSetHandler()
        self.sql_category = db_handler.CategoryHandler()
        self.sql_tab = db_handler.TabHandler()
        self.sql_model = db_handler.ModelHandler()
        self.sql_model_parameter = db_handler.ModelParameterHandler()
        self.sql_template = db_handler.TemplateHandler()
        self.sql_template_parameter = db_handler.TemplateParameterHandler()

        self.all_tab_display_names = self.get_tabs_display_names()
        self.all_tab_names = self.get_tabs_names()
        self.all_tab_id = self.st_tab_id_to_db_tab_id()

    #####################################
    # TAB
    #####################################
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

    #####################################
    # CATEGORY
    #####################################
    def get_categories_from_tab_id(self, tab_id):
        res = self.sql_category.get_all_by_tab_id(tab_id)
        return res

    #####################################
    # PARAMETER SET
    #####################################
    def get_all_parameter_sets_by_category_id(self, category_id):
        return self.sql_parameter_set.get_all_by_category_id(category_id)

    def extract_parameters_by_parameter_set_id(self, parameter_set_id):
        return self.sql_parameter.get_all_by_parameter_set_id(parameter_set_id)

    #####################################
    # MODEL
    #####################################
    def get_models_as_dict(self):
        models = self.sql_model.select_all()
        models_as_dict = {}

        for model in models:
            model_id, model_name, _, _ = model

            models_as_dict[model_id] = model_name

        return models_as_dict

    def get_templates_by_id(self, model_id):
        res = self.sql_model.select_one(
            values="templates",
            where="id=%d" % model_id
        )
        return eval(res[0]) if res else None

    def get_model_parameters_as_dict(self, model_id):
        parameters = self.sql_model_parameter.get_all_by_model_id(model_id)
        res = {}
        for parameter in parameters:
            _, name, _, value, value_type, _ = parameter
            if value_type == "bool":
                res[name] = bool(value)
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
    def get_template_parameters_from_template_id(self, template_id):
        return self.sql_template_parameter.get_all_by_template_id(template_id)


