#############################
# HIERARCHY OF APP MODEL ####
# Parameter objects -> ParameterSet -> Model
# Enables an API in this way: app_model.positive_electrode["parameter_set_name"].set_value("param_name", param_value)
#############################

class Parameter(object):

    def __init__(self, id, name, parameter_set_id, value, type, is_shown_to_user, description):
        self.id = id
        self.name = name
        self.parameter_set_id = parameter_set_id
        self.value = value
        self.type = type
        self.is_shown_to_user = is_shown_to_user
        self.description = description


class NumericalParameter(Parameter):
    def __init__(
            self,
            id, name, parameter_set_id, value, type, is_shown_to_user, description,
            min_value, max_value, unit_name, unit_dimension
    ):
        self.min_value = float(min_value) if type == float.__name__ else int(min_value)
        self.max_value = float(max_value) if type == float.__name__ else int(max_value)
        self.unit_name = unit_name
        self.unit_dimension = unit_dimension
        formatted_value = float(value) if type == float.__name__ else int(value)
        super().__init__(id, name, parameter_set_id, formatted_value, type, is_shown_to_user, description)


class StrParameter(Parameter):
    def __init__(self, id, name, parameter_set_id, value, is_shown_to_user, description, type=str.__name__):
        super().__init__(id, name, parameter_set_id, value, type, is_shown_to_user, description)


class BooleanParameter(Parameter):
    def __init__(self, id, name, parameter_set_id, value, is_shown_to_user, description, type=bool.__name__):
        super().__init__(id, name, parameter_set_id, bool(value), type, is_shown_to_user, description)


class FunctionParameter(Parameter):
    def __init__(self, id, name, parameter_set_id, value, type, is_shown_to_user, description):
        super().__init__(id, name, parameter_set_id, eval(value), type, is_shown_to_user, description)


class FormatParameters:

    def __init__(self):
        self.type_function = "function"

    def format_parameters(self, raw_parameters):
        formatted_parameters = []

        for parameter in raw_parameters:
            parameter_id, \
                name, \
                parameter_set_id, \
                value, \
                parameter_type, \
                unit_name, \
                unit_dimension,\
                max_value, \
                min_value,  \
                is_shown_to_user, \
                description = parameter  # according to db_initialize

            if parameter_type in [int.__name__, float.__name__]:
                if value is not None:  # TBD : what to do when not included in data source
                    formatted_parameters.append(NumericalParameter(
                        id=parameter_id,
                        name=name,
                        parameter_set_id=parameter_set_id,
                        value=value,
                        type=parameter_type,
                        is_shown_to_user=is_shown_to_user,
                        description=description,
                        min_value=min_value,
                        max_value=max_value,
                        unit_name=unit_name,
                        unit_dimension=unit_dimension
                    ))

            elif parameter_type == bool.__name__:
                formatted_parameters.append(BooleanParameter(
                    id=parameter_id,
                    name=name,
                    parameter_set_id=parameter_set_id,
                    value=value,
                    type=parameter_type,
                    is_shown_to_user=is_shown_to_user,
                    description=description
                ))

            elif parameter_type == str.__name__:
                formatted_parameters.append(StrParameter(
                    id=parameter_id,
                    name=name,
                    parameter_set_id=parameter_set_id,
                    value=value,
                    type=parameter_type,
                    is_shown_to_user=is_shown_to_user,
                    description=description
                ))

            elif parameter_type == self.type_function:
                formatted_parameters.append(FunctionParameter(
                    id=parameter_id,
                    name=name,
                    parameter_set_id=parameter_set_id,
                    value=value,
                    type=parameter_type,
                    is_shown_to_user=is_shown_to_user,
                    description=description
                ))

            else:
                assert False, "parameter_type={} is not handled. parameter_id={}".format(parameter_type, parameter_id)

        return formatted_parameters
