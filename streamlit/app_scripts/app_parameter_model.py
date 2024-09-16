#############################
# app_parameter_model all the parameter objects corresponding to the different parameter types existing in db.
# handled parameter_types : {'str', 'bool', 'int', 'float', 'function'}
#
# When running app.py,
# the db_handler ParameterHandler checks if this list of handled parameters covers all the existing types
#############################
from math import ceil
import numpy as np
import os
import sys
import streamlit as st
import math

##############################
# Set page directory to base level to allow for module import from different folder
path_to_streamlit_module = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, path_to_streamlit_module)
##############################

from database import db_helper


class Materials(object):
    def __init__(
        self,
        id,
        name,
        display_name,
        context_type,
        context_type_iri,
        description,
        selected_value=None,
    ):

        self.id = id
        self.name = name
        self.display_name = display_name
        self.context_type = context_type
        self.context_type_iri = context_type_iri
        self.description = description

        self.options = {}
        self.default_value = None

        self.selected_value = selected_value

    def add_option(self, option_id, option_details):

        self.options[option_id] = option_details
        if self.default_value is None:
            self.default_value = option_details.display_name
        self.name = option_details.name

    def set_selected_value(self, value):
        self.selected_value = value

    def set_reference_url(self, reference_url):
        self.reference_url = reference_url


class TemplateParameter(object):
    """
    Base object containing basic information, common to all parameter types
    """

    def __init__(
        self,
        id,
        name,
        template_id,
        type,
        is_shown_to_user,
        description,
        context_type=None,
        context_type_iri=None,
        display_name=None,
        selected_value=None,
    ):
        self.id = id
        self.name = name
        self.template_id = template_id
        self.context_type = context_type
        self.context_type_iri = context_type_iri
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


class Material(Materials):
    def __init__(
        self,
        id,
        name,
        model_name,
        difficulty,
        material,
        default_template,
        display_name,
        emmo_relation,
        category_id,
        tab_id,
        default_template_id,
        context_type,
        context_type_iri,
        description,
    ):

        super().__init__(
            id=id,
            name=name,
            display_name=display_name,
            context_type=context_type,
            context_type_iri=context_type_iri,
            description=description,
        )


class NumericalParameter(TemplateParameter):
    def __init__(
        self,
        id,
        name,
        model_name,
        par_class,
        difficulty,
        template_id,
        context_type,
        context_type_iri,
        type,
        is_shown_to_user,
        description,
        min_value,
        max_value,
        unit,
        unit_name,
        unit_iri,
        display_name,
    ):

        self.min_value = float(min_value) if type == float.__name__ else int(min_value)
        self.max_value = float(max_value) if type == float.__name__ else int(max_value)
        self.unit = unit
        self.unit_name = unit_name
        self.unit_iri = unit_iri

        self.type = type
        self.format = None
        self.set_format()

        self.increment = None
        self.set_increment()

        super().__init__(
            id=id,
            name=name,
            template_id=template_id,
            context_type=context_type,
            context_type_iri=context_type_iri,
            type=self.type,
            is_shown_to_user=is_shown_to_user,
            description=description,
        )

    def set_reference_url(self, url):
        self.reference_url = url

    def set_format(self):
        if self.type == int.__name__:
            self.format = "%d"

        else:
            max_readable_value = 10000
            min_readable_value = 0.0001
            is_readable = (
                self.max_value < max_readable_value and self.min_value > min_readable_value
            )
            self.format = "%g" if is_readable else "%.2e"

    def set_increment(self):
        """
        Calculates increment from min and max values.
        Increment is used to define the number input widget.
        """

        if self.type == float.__name__:
            average_value = 0.5 * (self.min_value + self.max_value)
            if average_value == 0:
                self.increment = 1e-17
                return

            # Calculate the order of magnitude
            order_of_magnitude = math.floor(math.log10(abs(average_value)))

            # Determine a base increment which is a power of 10
            base_increment = 10**order_of_magnitude

            # Adjust the increment to be more user-friendly
            if average_value < 1:
                self.increment = base_increment / 10
            else:
                self.increment = base_increment / 2

            # Further refinement for very small values
            if abs(self.increment) < 1e-10:
                self.increment = 1e-10

        else:
            self.increment = 1


class StrParameter(TemplateParameter):
    def __init__(
        self,
        id,
        name,
        template_id,
        context_type,
        context_type_iri,
        is_shown_to_user,
        description,
        display_name,
        type=str.__name__,
    ):
        super().__init__(
            id=id,
            name=name,
            template_id=template_id,
            context_type=context_type,
            context_type_iri=context_type_iri,
            type=type,
            is_shown_to_user=is_shown_to_user,
            description=description,
        )

    def set_reference_url(self, url):
        self.reference_url = url


class BooleanParameter(TemplateParameter):
    def __init__(
        self,
        id,
        name,
        template_id,
        context_type,
        context_type_iri,
        is_shown_to_user,
        description,
        display_name,
        type=bool.__name__,
    ):
        super().__init__(
            id=id,
            name=name,
            template_id=template_id,
            context_type=context_type,
            context_type_iri=context_type_iri,
            type=type,
            is_shown_to_user=is_shown_to_user,
            description=description,
        )


class FunctionParameter(TemplateParameter):
    def __init__(
        self,
        id,
        name,
        template_id,
        context_type,
        context_type_iri,
        type,
        is_shown_to_user,
        description,
        unit,
        unit_name,
        unit_iri,
        display_name,
    ):

        self.unit = unit
        self.unit_name = unit_name
        self.unit_iri = unit_iri
        super().__init__(
            id=id,
            name=name,
            template_id=template_id,
            context_type=context_type,
            context_type_iri=context_type_iri,
            type=type,
            is_shown_to_user=is_shown_to_user,
            description=description,
            display_name=display_name,
        )

    def set_reference_url(self, url):
        self.reference_url = url

    #     self.set_display_name()

    # def set_display_name(self):
    #     if self.display_name is None:
    #         self.display_name = self.parameter_set


class Option_material(object):
    def __init__(
        self,
        parameter_set_name=None,
        parameter_set_display_name=None,
        parameters=None,
        parameter_ids=None,
        parameter_names=None,
        parameter_values=None,
        parameter_display_names=None,
        parameter_set_id=None,
        reference_url=None,
        context_type=None,
    ):
        self.display_name = parameter_set_display_name
        self.name = parameter_set_name
        self.reference_url = reference_url
        self.parameter_set_id = parameter_set_id
        self.parameters = parameters
        self.parameter_ids = parameter_ids
        self.parameter_names = parameter_names
        self.parameter_values = parameter_values
        self.parameter_display_names = parameter_display_names
        self.context_type = context_type


class Option_parameter(object):
    def __init__(
        self,
        formatted_value=None,
        parameter_set=None,
        parameter_display_name=None,
        parameter_name=None,
    ):
        self.value = formatted_value
        self.parameter_set = parameter_set
        self.parameter_display_name = parameter_display_name
        self.parameter_name = parameter_name


class FormatParameters:

    def __init__(self):
        self.type_function = "function"
        self.user_defined_id = 0

    def get_index(self, list, id):

        for list_index, value in enumerate(list):
            if value == id:
                index = list_index
                break

        assert index is not None, "id={} not found in list".format(id)
        return index

    def format_parameter_sets(
        self,
        material_component,
        materials,
        material_display_names,
        reference_urls,
        context_types,
        parameter_sets,
        material_parameter_sets_name_by_id,
        raw_template_parameters,
        raw_parameters,
        material_component_id,
    ):
        # initialize from template parameters
        formatted_materials = self.initialize_parameter_set(material_component)
        formatted_parameters = self.initialize_parameters(raw_template_parameters)

        index_set = 0

        for parameter_set in parameter_sets:
            (
                parameter_set_id,
                parameter_set_name,
                *_,
            ) = parameter_set

            material_display_name = material_display_names[parameter_set_id]
            reference_url = reference_urls[parameter_set_id]
            material_context_type = context_types[parameter_set_id]

            raw_parameters_set = raw_parameters[parameter_set_id]

            # Create list with parameter set ids

            raw_parameters_set_ids = np.array([sub_list[2] for sub_list in raw_parameters_set])

            parameter_ids = []
            parameter_names = []
            template_parameter_ids = []
            parameter_values = []
            parameter_display_names = []

            index_set += 1
            index_parameter = 0

            for parameter in raw_parameters_set:
                # get index of id
                # parameter_set_id_index = self.get_index(raw_parameters_set_ids, parameter_set_id)
                if raw_parameters_set_ids[index_parameter] == parameter_set_id:

                    (
                        parameter_id,
                        parameter_name,
                        _,
                        template_parameter_id,
                        parameter_value,
                    ) = parameter

                    parameter_ids.append(parameter_id)
                    parameter_names.append(parameter_name)
                    template_parameter_ids.append(template_parameter_id)
                    parameter_values.append(parameter_value)

                index_parameter += 1

            values = []
            for i, value in enumerate(parameter_values):

                template_parameter_id = template_parameter_ids[i]
                parameter_id = parameter_ids[i]

                template_parameter = formatted_parameters.get(str(template_parameter_id))

                if template_parameter:
                    if isinstance(template_parameter, NumericalParameter):
                        if template_parameter.type == "int":
                            formatted_value = int(value)
                        elif template_parameter.type == "float":
                            formatted_value = float(value)
                            # formatted_value = self.custom_number_input(formatted_value)
                        else:
                            assert (
                                False
                            ), "Unexpected NumericalParameter. parameter_id={} type={}".format(
                                parameter_id, template_parameter.type
                            )
                    elif isinstance(template_parameter, StrParameter):
                        formatted_value = value
                    elif isinstance(template_parameter, BooleanParameter):
                        formatted_value = bool(value)
                    elif isinstance(template_parameter, FunctionParameter):
                        formatted_value = eval(value)

                    else:

                        assert False, "Unexpected template_parameter. parameter_id={}".format(
                            parameter_id
                        )

                    values.append(formatted_value)
                    parameter_display_name = template_parameter.display_name
                    parameter_display_names.append(parameter_display_name)
                    parameter_name = template_parameter.name

                    # each parameter has metadata from the "template", to which we add the options containing value and origin
                    if type(parameter_sets) == str:
                        new_option = Option_parameter(
                            formatted_value=formatted_value,
                            parameter_set=parameter_sets,
                            parameter_display_name=parameter_display_name,
                            parameter_name=parameter_name,
                        )
                    else:
                        new_option = Option_parameter(
                            formatted_value=formatted_value,
                            parameter_set=material_parameter_sets_name_by_id.get(parameter_set_id),
                            parameter_display_name=parameter_display_name,
                            parameter_name=parameter_name,
                        )
                    template_parameter.add_option(parameter_set_id, new_option)

            formatted_material = formatted_materials.get(str(material_component_id))

            if isinstance(formatted_material, Material):
                formatted_display_name = str(material_display_name)
                formatted_material.set_selected_value(formatted_display_name)
                formatted_material.set_reference_url(reference_url)

            # each parameter has metadata from the "template", to which we add the options containing value and origin
            new_option = Option_material(
                parameter_set_name=parameter_set,
                parameter_set_display_name=formatted_display_name,
                parameter_set_id=parameter_set_id,
                parameters=formatted_parameters,
                parameter_ids=parameter_ids,
                parameter_names=parameter_names,
                parameter_values=values,
                parameter_display_names=parameter_display_names,
                reference_url=reference_url,
                context_type=material_context_type,
            )
            # template_parameter.set_selected_value(formatted_value)
            formatted_material.add_option(parameter_set_id, new_option)

        return formatted_parameters, formatted_material, formatted_materials

    @st.cache_data
    def custom_number_input(_self, value):
        if value != 0 and (abs(value) < 1e-3 or abs(value) >= 1e4):
            format_str = "{:.2e}"  # Scientific notation with 2 decimal places
        else:
            format_str = "{:.2f}"  # Normal notation with 2 decimal places
        return format_str.format(value)

    def format_parameters(self, raw_parameters, raw_template_parameters, parameter_sets_name_by_id):

        if np.ndim(raw_parameters) > 1:

            # initialize from template parameters
            formatted_parameters = self.initialize_parameters(raw_template_parameters)

            for parameter in raw_parameters:
                parameter_id, name, parameter_set_id, template_parameter_id, value = parameter

                template_parameter = formatted_parameters.get(str(template_parameter_id))

                if template_parameter:
                    if isinstance(template_parameter, NumericalParameter):
                        if template_parameter.type == "int":
                            formatted_value = int(value)
                        elif template_parameter.type == "float":
                            formatted_value = float(value)
                            # formatted_value = self.custom_number_input(formatted_value)
                        else:
                            assert (
                                False
                            ), "Unexpected NumericalParameter. parameter_id={} type={}".format(
                                parameter_id, template_parameter.type
                            )
                    elif isinstance(template_parameter, StrParameter):
                        formatted_value = value
                    elif isinstance(template_parameter, BooleanParameter):
                        formatted_value = bool(value)
                    elif isinstance(template_parameter, FunctionParameter):
                        formatted_value = eval(value)
                        template_parameter.set_selected_value(formatted_value)
                    else:

                        assert False, "Unexpected template_parameter. parameter_id={}".format(
                            parameter_id
                        )

                    parameter_display_name = template_parameter.display_name

                    # each parameter has metadata from the "template", to which we add the options containing value and origin
                    if type(parameter_sets_name_by_id) == str:
                        new_option = Option_parameter(
                            formatted_value=formatted_value,
                            parameter_set=parameter_sets_name_by_id,
                            parameter_display_name=parameter_display_name,
                        )
                    else:
                        new_option = Option_parameter(
                            formatted_value=formatted_value,
                            parameter_set=parameter_sets_name_by_id.get(parameter_set_id),
                            parameter_display_name=parameter_display_name,
                        )

                    template_parameter.add_option(parameter_id, new_option)

        else:
            # initialize from template parameters
            formatted_parameters = self.initialize_parameters(raw_template_parameters)

            parameter_id, name, parameter_set_id, template_parameter_id, value = raw_parameters

            template_parameter = formatted_parameters.get(str(template_parameter_id))

            if isinstance(template_parameter, NumericalParameter):
                if template_parameter.type == "int":
                    formatted_value = int(value)
                elif template_parameter.type == "float":
                    formatted_value = float(value)
                    # formatted_value = self.custom_number_input(formatted_value)
                else:
                    assert False, "Unexpected NumericalParameter. parameter_id={} type={}".format(
                        parameter_id, template_parameter.type
                    )
            elif isinstance(template_parameter, StrParameter):
                formatted_value = value
            elif isinstance(template_parameter, BooleanParameter):
                formatted_value = bool(value)
            elif isinstance(template_parameter, FunctionParameter):
                formatted_value = eval(value)
                template_parameter.set_selected_value(formatted_value)
            else:

                assert False, "Unexpected template_parameter. parameter_id={}".format(parameter_id)

            parameter_display_name = template_parameter.display_name

            # each parameter has metadata from the "template", to which we add the options containing value and origin
            if type(parameter_sets_name_by_id) == str:

                new_option = Option_parameter(
                    formatted_value=formatted_value,
                    parameter_set=parameter_sets_name_by_id,
                    parameter_display_name=parameter_display_name,
                )

            else:

                new_option = Option_parameter(
                    formatted_value=formatted_value,
                    parameter_set=parameter_sets_name_by_id.get(parameter_set_id),
                    parameter_display_name=parameter_display_name,
                )

            template_parameter.add_option(parameter_id, new_option)

        return formatted_parameters

    def initialize_parameter_set(_self, materials):
        initialized_materials = {}

        if np.ndim(materials) > 1:

            material_display_names = []
            for material in materials:
                (
                    material_id,
                    material_name,
                    model_name,
                    difficulty,
                    default_template,
                    display_name,
                    category_id,
                    tab_id,
                    default_template_id,
                    context_type,
                    context_type_iri,
                    description,
                ) = material

                initialized_materials["%d" % int(material_id)] = Material(
                    id=material_id,
                    name=material_name,
                    model_name=model_name,
                    difficulty=difficulty,
                    default_template=default_template,
                    display_name=display_name,
                    category_id=category_id,
                    tab_id=tab_id,
                    default_template_id=default_template_id,
                    context_type=context_type,
                    context_type_iri=context_type_iri,
                    description=description,
                )

        else:
            (
                material_id,
                material_name,
                model_name,
                difficulty,
                material,
                default_template,
                display_name,
                emmo_relation,
                category_id,
                tab_id,
                default_template_id,
                context_type,
                context_type_iri,
                description,
            ) = tuple(np.squeeze(materials))

            initialized_materials["%d" % int(material_id)] = Material(
                id=material_id,
                name=material_name,
                model_name=model_name,
                difficulty=difficulty,
                material=material,
                default_template=default_template,
                display_name=display_name,
                emmo_relation=emmo_relation,
                category_id=category_id,
                tab_id=tab_id,
                default_template_id=default_template_id,
                context_type=context_type,
                context_type_iri=context_type_iri,
                description=description,
            )
        return initialized_materials

    def initialize_parameters(_self, raw_template_parameters):
        initialized_parameters = {}
        if np.ndim(raw_template_parameters) > 1:

            for template_parameter in raw_template_parameters:
                (
                    parameter_id,
                    name,
                    model_name,
                    par_class,
                    difficulty,
                    template_id,
                    context_type,
                    context_type_iri,
                    parameter_type,
                    unit,
                    unit_name,
                    unit_iri,
                    max_value,
                    min_value,
                    is_shown_to_user,
                    description,
                    display_name,
                ) = np.squeeze(template_parameter)

                parameter_id = int(parameter_id)

                if parameter_type in [int.__name__, float.__name__]:

                    initialized_parameters["%d" % parameter_id] = NumericalParameter(
                        id=parameter_id,
                        name=name,
                        model_name=model_name,
                        par_class=par_class,
                        difficulty=difficulty,
                        template_id=template_id,
                        context_type=context_type,
                        context_type_iri=context_type_iri,
                        type=parameter_type,
                        is_shown_to_user=is_shown_to_user,
                        description=description,
                        min_value=min_value,
                        max_value=max_value,
                        unit=unit,
                        unit_name=unit_name,
                        unit_iri=unit_iri,
                        display_name=display_name,
                    )

                elif parameter_type == bool.__name__:
                    initialized_parameters["%d" % parameter_id] = BooleanParameter(
                        id=parameter_id,
                        name=name,
                        template_id=template_id,
                        context_type=context_type,
                        context_type_iri=context_type_iri,
                        type=parameter_type,
                        is_shown_to_user=is_shown_to_user,
                        description=description,
                        display_name=display_name,
                    )

                elif parameter_type == str.__name__:
                    initialized_parameters["%d" % int(parameter_id)] = StrParameter(
                        id=parameter_id,
                        name=name,
                        template_id=template_id,
                        context_type=context_type,
                        context_type_iri=context_type_iri,
                        type=parameter_type,
                        is_shown_to_user=is_shown_to_user,
                        description=description,
                        display_name=display_name,
                    )

                elif parameter_type == _self.type_function:
                    # function parameters should be changed, using a more robust way to define them.
                    # for now functions are defined as string (ex: computeOCP_nmc111)
                    initialized_parameters["%d" % parameter_id] = FunctionParameter(
                        id=parameter_id,
                        name=name,
                        template_id=template_id,
                        context_type=context_type,
                        context_type_iri=context_type_iri,
                        type=parameter_type,
                        is_shown_to_user=True,
                        description=description,
                        unit=unit,
                        unit_name=unit_name,
                        unit_iri=unit_iri,
                        display_name=display_name,
                    )

                else:
                    assert False, "parameter_type={} is not handled. parameter_id={}".format(
                        parameter_type, parameter_id
                    )
        else:

            (
                parameter_id,
                name,
                model_name,
                par_class,
                difficulty,
                template_id,
                context_type,
                context_type_iri,
                parameter_type,
                unit,
                unit_name,
                unit_iri,
                max_value,
                min_value,
                is_shown_to_user,
                description,
                display_name,
            ) = tuple(np.squeeze(raw_template_parameters))
            parameter_id = int(parameter_id)

            if parameter_type in [int.__name__, float.__name__]:

                initialized_parameters["%d" % parameter_id] = NumericalParameter(
                    id=parameter_id,
                    name=name,
                    model_name=model_name,
                    par_class=par_class,
                    difficulty=difficulty,
                    template_id=template_id,
                    context_type=context_type,
                    context_type_iri=context_type_iri,
                    type=parameter_type,
                    is_shown_to_user=is_shown_to_user,
                    description=description,
                    min_value=min_value,
                    max_value=max_value,
                    unit=unit,
                    unit_name=unit_name,
                    unit_iri=unit_iri,
                    display_name=display_name,
                )

            elif parameter_type == bool.__name__:

                initialized_parameters["%d" % int(parameter_id)] = BooleanParameter(
                    id=parameter_id,
                    name=name,
                    template_id=template_id,
                    context_type=context_type,
                    context_type_iri=context_type_iri,
                    type=parameter_type,
                    is_shown_to_user=is_shown_to_user,
                    description=description,
                    display_name=display_name,
                )

            elif parameter_type == str.__name__:

                initialized_parameters["%d" % int(parameter_id)] = StrParameter(
                    id=parameter_id,
                    name=name,
                    template_id=template_id,
                    context_type=context_type,
                    context_type_iri=context_type_iri,
                    type=parameter_type,
                    is_shown_to_user=is_shown_to_user,
                    description=description,
                    display_name=display_name,
                )

            elif parameter_type == _self.type_function:
                # function parameters should be changed, using a more robust way to define them.
                # for now functions are defined as string (ex: computeOCP_nmc111)
                initialized_parameters["%d" % int(parameter_id)] = FunctionParameter(
                    id=parameter_id,
                    name=name,
                    template_id=template_id,
                    type=parameter_type,
                    is_shown_to_user=True,
                    description=description,
                    display_name=display_name,
                )

            else:
                assert False, "parameter_type={} is not handled. parameter_id={}".format(
                    parameter_type, parameter_id
                )

        return initialized_parameters
