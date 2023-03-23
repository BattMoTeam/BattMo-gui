#############################
# app_parameter_model all the parameter objects corresponding to the different parameter types existing in db.
# handled parameter_types : {'str', 'bool', 'int', 'float', 'function'}
#
# When running app.py,
# the db_handler ParameterHandler checks if this list of handled parameters covers all the existing types
#############################
from math import ceil


class TemplateParameter(object):

    def __init__(self, id, name, template_id, type, is_shown_to_user, description, display_name=None, selected_value=None):
        self.id = id
        self.name = name
        self.template_id = template_id
        self.type = type
        self.is_shown_to_user = is_shown_to_user
        self.description = description

        self.display_name = display_name
        self.set_display_name()

        self.options = {}
        self.default_value = None

        self.selected_value = selected_value

    def set_display_name(self):
        words = self.name.split("_")
        first_word = words[0]
        words[0] = first_word[0].upper() + first_word[1:]
        self.display_name = " ".join(words)

    def add_option(self, option_id, option_details):
        self.options[option_id] = option_details
        if self.default_value is None:
            self.default_value = option_details.value

    def set_selected_value(self, value):
        self.selected_value = value


class NumericalParameter(TemplateParameter):
    def __init__(
            self,
            id, name, template_id, type, is_shown_to_user, description,
            min_value, max_value, unit_name, unit_dimension
    ):

        self.min_value = float(min_value) if type == float.__name__ else int(min_value)
        self.max_value = float(max_value) if type == float.__name__ else int(max_value)
        self.unit = unit_dimension

        self.type = type
        self.format = None
        self.set_format()

        self.increment = None
        self.set_increment()

        super().__init__(id, name, template_id, self.type, is_shown_to_user, description)

    def set_format(self):
        if self.type == int.__name__:
            self.format = "%d"

        else:
            max_readable_value = 10000
            min_readable_value = 0.001
            is_readable = self.max_value < max_readable_value and self.min_value > min_readable_value
            self.format = "%g" if is_readable else "%.2e"

    def set_increment(self):

        if self.type == float.__name__:
            average_value = 0.5*(self.min_value + self.max_value)
            five_percent_of_value = "%e" % (0.05 * average_value)

            decimal, exponential = five_percent_of_value.split("e")

            self.increment = round(
                float(ceil(float(decimal)) * 10 ** int(exponential)),
                2
            )

        else:
            self.increment = 1


class StrParameter(TemplateParameter):
    def __init__(self, id, name, template_id, is_shown_to_user, description, type=str.__name__):
        super().__init__(id, name, template_id, type, is_shown_to_user, description)


class BooleanParameter(TemplateParameter):
    def __init__(self, id, name, template_id, is_shown_to_user, description, type=bool.__name__):
        super().__init__(id, name, template_id, type, is_shown_to_user, description)


class FunctionParameter(TemplateParameter):
    def __init__(self, id, name, template_id, type, is_shown_to_user, description):
        super().__init__(id, name, template_id, type, is_shown_to_user, description)


USER_DEFINED = "User defined"


class Option(object):
    def __init__(self, formatted_value=None, parameter_set=None, display_name=None):
        self.value = formatted_value
        self.parameter_set = parameter_set

        self.display_name = display_name
        self.set_display_name()

    def set_display_name(self):
        if self.display_name is None:
            self.display_name = self.parameter_set


class UserDefined(Option):
    def __init__(self):
        super().__init__(display_name=USER_DEFINED)


class FormatParameters:

    def __init__(self):
        self.type_function = "function"
        self.user_defined_id = 0

    def format_parameters(self, raw_parameters, raw_template_parameters, parameter_sets_name_by_id):
        formatted_parameters = self.initialize_parameters(raw_template_parameters)

        for parameter in raw_parameters:
            parameter_id, \
                name, \
                parameter_set_id, \
                template_parameter_id, \
                value = parameter

            template_parameter = formatted_parameters.get(template_parameter_id)

            if isinstance(template_parameter, NumericalParameter):
                formatted_value = int(value) if template_parameter.type == "int" else float(value)
            elif isinstance(template_parameter, StrParameter):
                formatted_value = value
            elif isinstance(template_parameter, BooleanParameter):
                formatted_value = bool(value)
            elif isinstance(template_parameter, FunctionParameter):
                formatted_value = eval(value)
                template_parameter.set_selected_value(formatted_value)
            else:
                assert False, "Unexpected template_parameter. parameter_id={}".format(parameter_id)

            new_option = Option(
                formatted_value=formatted_value,
                parameter_set=parameter_sets_name_by_id.get(parameter_set_id)
            )
            template_parameter.add_option(parameter_id, new_option)

        return formatted_parameters

    def initialize_parameters(self, raw_template_parameters):
        initialized_parameters = {}

        for template_parameter in raw_template_parameters:
            parameter_id, \
                name, \
                template_id, \
                parameter_type, \
                unit_name, \
                unit_dimension, \
                max_value, \
                min_value, \
                is_shown_to_user, \
                description = template_parameter  # according to db_model

            if parameter_type in [int.__name__, float.__name__]:

                initialized_parameters[parameter_id] = NumericalParameter(
                    id=parameter_id,
                    name=name,
                    template_id=template_id,
                    type=parameter_type,
                    is_shown_to_user=is_shown_to_user,
                    description=description,
                    min_value=min_value,
                    max_value=max_value,
                    unit_name=unit_name,
                    unit_dimension=unit_dimension
                )

            elif parameter_type == bool.__name__:
                initialized_parameters[parameter_id] = BooleanParameter(
                    id=parameter_id,
                    name=name,
                    template_id=template_id,
                    type=parameter_type,
                    is_shown_to_user=is_shown_to_user,
                    description=description
                )

            elif parameter_type == str.__name__:
                initialized_parameters[parameter_id] = StrParameter(
                    id=parameter_id,
                    name=name,
                    template_id=template_id,
                    type=parameter_type,
                    is_shown_to_user=is_shown_to_user,
                    description=description
                )

            elif parameter_type == self.type_function:
                initialized_parameters[parameter_id] = FunctionParameter(
                    id=parameter_id,
                    name=name,
                    template_id=template_id,
                    type=parameter_type,
                    is_shown_to_user=False,
                    description=description
                )

            else:
                assert False, "parameter_type={} is not handled. parameter_id={}".format(parameter_type, parameter_id)

        return initialized_parameters
