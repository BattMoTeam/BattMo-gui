# use fileinput to handle files
# use glob to list documents with certain extensions
# here link https://towardsdatascience.com/the-best-practice-of-reading-text-files-in-python-509b1d4f5a4

from db import db_handler


def get_tree(d, indent=0):
    
    tree = ""
    for key, value in d.items():
        tree += " " * indent + str(key) + "\n"
        if isinstance(value, dict):
            tree += get_tree(value, indent+2)
        else:
            tree += " " * (indent+2) + str(value) + "\n"
    return tree

#############################
# HIERARCHY OF APP MODEL ####
# Parameter objects -> ParameterSet -> Model
# Enables an API in this way: app_model.positive_electrode["parameter_set_name"].set_value("param_name", param_value)
#############################


class NumericalParameter:

    def __init__(self, default: float, val_min: float = None, val_max: float = None):
        self.default = default
        self.val_min = val_min
        self.val_max = val_max


class OptionsParameter:

    def __init__(self, default: str, options: list, multiple: bool = False):
        self.default = default
        self.options = options
        self.multiple = multiple
        self.input = None


class BooleanParameter:
    def __init__(self, default: bool = True):
        self.default = default


class ParameterSet:

    def __init__(self, key_param_pairs: dict):
        self.key_param_pairs = key_param_pairs

    @property
    def parameters(self):
        return self.key_param_pairs

    @property
    def parameter_names(self):
        return list(self.key_param_pairs.keys())

    def get_value(self, parameter_name: str):

        assert parameter_name in self.key_param_pairs.keys(), f"{parameter_name} not a parameter in this set. Try the .parameter_names property to see which parameters are available"
        return self.key_param_pairs[parameter_name].default


class AppModel:

    def __init__(self):

        self.positive_electrode = {}
        self.negative_electrode = {}
        self.electrolyte = {}
        self.cell = {}
        self.separator = {}
        self.cycling = {}


class LoaderJsons:

    def __init__(self):
        self.parameters_dict = {}
        self.sql_parameter = db_handler.ParameterHandler()
        self.sql_parameter_set = db_handler.ParameterSetHandler()
        self.sql_category = db_handler.CategoryHandler()
        self.load_parameters()

    def load_parameters(self):
        all_categories = self.sql_category.select_all()
        for category in all_categories:
            category_id, category_name, _ = category
            parameter_sets = {}

            all_parameter_sets = self.sql_parameter_set.get_all_by_category_id(category_id)
            for parameter_set in all_parameter_sets:
                parameter_set_id, parameter_set_name, _, _ = parameter_set
                parameters = {}

                all_parameters = self.sql_parameter.get_all_by_parameter_set_id(parameter_set_id)

                for parameter in all_parameters:
                    _, name, value, value_type, _, is_shown_to_user = parameter
                    if is_shown_to_user:
                        formatted_value = value if value_type == "str" else eval(value)
                        parameters[name] = formatted_value

                parameter_sets[parameter_set_name] = parameters

            self.parameters_dict[category_name] = parameter_sets

    def from_values_to_param_objects(self, value):

        if isinstance(value, (int, float)):
            app_parameter = NumericalParameter(default=value)

        elif (isinstance(value, tuple)) & (len(value) == 3):
            app_parameter = NumericalParameter(default=value[0], val_min=value[1], val_max=value[2])

        elif isinstance(value, str):
            app_parameter = OptionsParameter(default=value, options=[value])

        elif isinstance(value, list):
            app_parameter = OptionsParameter(default=value[0], options=value)

        elif isinstance(value, bool):
            app_parameter = BooleanParameter(default=value)

        else:
            assert False, "this value type is not handled"

        return app_parameter

    def conform_params_to_app_model(self):

        app_model = AppModel()
        for category, parameter_sets in self.parameters_dict.items():

            for parameter_set, key_value_pairs in parameter_sets.items():

                key_param_pairs = {}

                for key, value in key_value_pairs.items():

                    app_parameter = self.from_values_to_param_objects(value)

                    key_param_pairs.update({key: app_parameter})

                if category == "cell":
                    app_model.cell.update({parameter_set: key_param_pairs})

                if category == "electrolyte":
                    app_model.electrolyte.update({parameter_set: key_param_pairs})

                if category == "negative_electrode":
                    app_model.negative_electrode.update({parameter_set: key_param_pairs})

                if category == "positive_electrode":
                    app_model.positive_electrode.update({parameter_set: key_param_pairs})

                if category == "separator":
                    app_model.separator.update({parameter_set: key_param_pairs})

                if category == "cycling":
                    app_model.cycling.update({parameter_set: key_param_pairs})

        return app_model
