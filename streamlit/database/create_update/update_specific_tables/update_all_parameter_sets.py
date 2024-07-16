import os
import sys
import numpy as np

##############################
# Set page directory to base level to allow for module import from different folder
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
)
##############################

from database import db_handler, db_helper
from app_scripts import app_access


#####################################
#    UPDATE PARAMETER SET
#####################################
class Parameter(object):
    def __init__(
        self,
        name,
        model_name,
        parameter_set_id,
        template_parameter_id,
        display_name,
        value=None,
    ):
        self.name = name
        self.model_name = model_name
        self.parameter_set_id = parameter_set_id
        self.template_parameter_id = template_parameter_id
        self.value = value
        self.display_name = display_name


class UpdateParameterSets:

    def __init__(self, print_details=False):
        self.template_type = "template"
        self.sql_parameter = db_handler.ParameterHandler()
        self.sql_parameter_set = db_handler.ParameterSetHandler()
        # self.sql_component = db_handler.componentHandler()
        self.sql_component = db_handler.ComponentHandler()
        self.sql_materials = db_handler.MaterialHandler()
        self.sql_template = db_handler.TemplateHandler()
        self.sql_template_parameter = db_handler.TemplateParameterHandler()
        self.sql_model = db_handler.ModelHandler()
        self.print_details = print_details

    def update_parameter_set_from_json(self, parameter_set, path, component=None):
        """
        parameter_set: {
            "Name": "file_name",
            "component": "electrolyte",
            "Parameters": {
                "specific_heat_capacity": 1518.0,
                "thermal_conductivity": 0.099,
                "density": 1210,
                "conductivity": {
                    "functionname": "updateElectrolyteConductivityFunc_Xu",
                    "argument_list": [
                    "concentration",
                    "temperature"
                    ]
                },
                "charge_carrier_name": "Li",
                "charge_carrier_charge_number": 1,
                "charge_carrier_transference_number": 0.399
                "etc": "etc"
            }
        }
        """
        name = parameter_set.get("Name")
        type = parameter_set.get("Type")

        component = parameter_set.get("component")

        material = int(parameter_set.get("material"))
        parameters = parameter_set.get("Parameters")

        if type == self.template_type:
            return None, False

        assert name is not None, "Name of parameter_set {} must have a name".format(path)
        # assert component is not None, "component of parameter_set {} is not defined".format(name)
        assert parameters is not None, "Parameters of parameter_set {} is not defined".format(name)

        if isinstance(component, list):
            component_id = []
            for component_name in component:
                print("name = ", component_name)

                component_id.append(self.sql_component.get_id_from_name(component_name))
        else:
            component_id = self.sql_component.get_id_from_name(component)

        display_name = parameter_set.get("display_name")
        model_names = parameter_set.get("model_name")
        # assert component_id is not None, "component = {} is not specified in components.json. path={}".format(component, path)

        # test = self.sql_materials.get_material_id_by_parameter_set_name(component_id)
        # print("test=", test)
        # material = int(self.sql_parameter_set.get_material_from_name(name))

        for model_name in model_names:

            if material == True:

                print("name = ", name)
                material_id = np.squeeze(
                    db_helper.get_material_id_by_parameter_set_name_and_model_name(name, model_name)
                ).astype(str)

                if isinstance(component, list):
                    for id in component_id:

                        parameter_set_id, parameter_set_already_exists = (
                            self.create_or_update_parameter_set(
                                name=name,
                                component_id=id,
                                material=material,
                                model_name=model_name,
                                material_id=material_id,
                            )
                        )

                        formatted_parameters = self.format_parameters(
                            parameters=parameters,
                            parameter_set_id=parameter_set_id,
                            component_id=id,
                            display_name=display_name,
                            parameter_set_name=name,
                            model_name=model_name,
                        )

                    if parameter_set_already_exists:
                        if self.print_details:
                            print("\n Updating {}".format(name))
                        self.update_parameters(parameters=formatted_parameters)

                    else:
                        if self.print_details:
                            print("\n Creating {}".format(name))
                        self.add_parameters(parameters=formatted_parameters)

                    return parameter_set_id, parameter_set_already_exists, name
                else:
                    parameter_set_id, parameter_set_already_exists = (
                        self.create_or_update_parameter_set(
                            name=name,
                            component_id=component_id,
                            material=material,
                            model_name=model_name,
                            material_id=material_id,
                        )
                    )

            else:

                parameter_set_id, parameter_set_already_exists = (
                    self.create_or_update_parameter_set(
                        name=name,
                        component_id=component_id,
                        material=material,
                        model_name=model_name,
                        material_id=None,
                    )
                )

            formatted_parameters = self.format_parameters(
                parameters=parameters,
                parameter_set_id=parameter_set_id,
                component_id=component_id,
                display_name=display_name,
                parameter_set_name=name,
                model_name=model_name,
            )

            if parameter_set_already_exists:
                if self.print_details:
                    print("\n Updating {}".format(name))
                self.update_parameters(parameters=formatted_parameters)

            else:
                if self.print_details:
                    print("\n Creating {}".format(name))
                self.add_parameters(parameters=formatted_parameters)

            return parameter_set_id, parameter_set_already_exists, name

    def create_or_update_parameter_set(self, name, component_id, material, model_name, material_id):

        if name == "P2D":
            parameter_set_id = self.sql_parameter_set.get_id_from_name(name)
        else:
            parameter_set_id = self.sql_parameter_set.get_id_by_name_and_category_and_model_name(
                name, component_id, model_name
            )

        if parameter_set_id:
            return parameter_set_id, True
        else:
            return (
                self.sql_parameter_set.insert_value(
                    name=name,
                    component_id=component_id,
                    material=material,
                    model_name=model_name,
                    material_id=material_id,
                ),
                False,
            )

    def format_parameters(
        self,
        parameters,
        parameter_set_id,
        component_id,
        display_name,
        parameter_set_name,
        model_name,
    ):
        try:
            template_id = self.sql_component.get_default_template_id_by_id(component_id)
        except:
            template_name = self.sql_model.get_default_template_name_by_name_and_model_name(
                parameter_set_name, model_name
            )
            template_id = self.sql_template.get_id_from_name(template_name)

        raw_template_parameters = self.sql_template_parameter.get_id_name_and_type_by_template_id(
            template_id, model_name
        )
        template_parameters = {}
        template_parameters_types = {}
        for tp_id, tp_name, tp_type in raw_template_parameters:
            template_parameters[tp_name + model_name] = tp_id
            template_parameters_types[tp_name + model_name] = tp_type

        formatted_parameters = []
        for parameter_name in parameters:

            template_parameter_id = template_parameters.get(parameter_name + model_name)
            if template_parameter_id is None:
                print(
                    "Warning !! parameter {} has no corresponding template parameter".format(
                        parameter_name
                    )
                )
                formatted_value = None

            else:
                value = parameters.get(parameter_name)
                value_type = template_parameters_types.get(parameter_name + model_name)
                formatted_value = self.format_value(value, value_type)

            if formatted_value:

                formatted_parameters.append(
                    Parameter(
                        name=parameter_name,
                        model_name=model_name,
                        parameter_set_id=parameter_set_id,
                        template_parameter_id=template_parameter_id,
                        value=formatted_value,
                        display_name=display_name,
                    )
                )

        return formatted_parameters

    def format_value(self, value, value_type):
        """
        Values are stored as string: if it's already a string, str(value) will fail
        """
        if value is None:
            return None

        elif value_type == "str":
            return value

        else:
            return str(value)

    def add_parameters(self, parameters):
        added_parameters = []
        for parameter in parameters:
            self.sql_parameter.insert_value(
                name=parameter.name,
                parameter_set_id=parameter.parameter_set_id,
                template_parameter_id=parameter.template_parameter_id,
                value=parameter.value,
            )
            added_parameters.append(parameter.name)

        if self.print_details:
            print("  Added parameters: ", added_parameters)

    def update_parameters(self, parameters):
        if not parameters:
            return
        parameter_set_id = parameters[0].parameter_set_id
        new_parameters = []
        # every item which is not updated will be deleted, so we don't keep useless items in db
        existing_ids_to_be_deleted = self.sql_parameter.get_all_ids_by_parameter_set_id(
            parameter_set_id
        )

        for parameter in parameters:
            parameter_id = self.sql_parameter.get_id_from_name_and_parameter_set_id(
                name=parameter.name, parameter_set_id=parameter_set_id
            )
            if parameter_id:  # existing parameter, update fields
                try:
                    self.sql_parameter.update_by_id(
                        id=parameter_id,
                        columns_and_values={
                            "name": parameter.name,
                            "model_name": parameter.model_name,
                            "parameter_set_id": parameter.parameter_set_id,
                            "template_parameter_id": parameter.template_parameter_id,
                            "value": parameter.value,
                        },
                    )
                    existing_ids_to_be_deleted.remove(parameter_id)
                except:
                    # SQL query in update_by_id could fail, for example for str containing quotes
                    # In that case, we delete and recreate the parameter instead of updating it
                    new_parameters.append(parameter)

            else:  # non-existing parameter, create it
                new_parameters.append(parameter)

        # add new params and delete unused ones
        self.add_parameters(new_parameters)

        deleted_parameters = []
        for id_to_delete in existing_ids_to_be_deleted:
            deleted_parameters.append(self.sql_parameter.get_name_from_id(id_to_delete))
            self.sql_parameter.delete_by_id(id_to_delete)

        if self.print_details:
            print("  Deleted parameters: ", deleted_parameters)

    #####################################
    #    DELETE PARAMETER SET
    #####################################
    def delete_parameter_set_by_id(self, parameter_set_id):
        parameter_set = self.sql_parameter_set.select_by_id(parameter_set_id)
        if parameter_set:
            _, name, component_id, _, _ = parameter_set
            component_id = int(component_id)
            parameter_ids = self.sql_parameter.get_all_ids_by_parameter_set_id(parameter_set_id)

            self.sql_parameter_set.delete_by_id(parameter_set_id)
            for parameter_id in parameter_ids:
                self.sql_parameter.delete_by_id(parameter_id)
            print(
                "\n Parameter_set(name = {}, type={}) has been deleted.".format(
                    name, self.sql_component.get_name_from_id(component_id)
                )
            )
            return name

    #####################################
    #    RUN SCRIPT
    #####################################
    def get_all_resources(self):
        return app_access.get_all_parameter_sets_experimental_data_files_path()

    def execute_script(self):
        all_file_path = self.get_all_resources()
        existing_ids_to_be_deleted = self.sql_parameter_set.get_all_ids()

        new_or_updated = []
        deleted = []

        for file_path in all_file_path:
            file_as_json = app_access.get_json_from_path(file_path)
            print("file = ", file_as_json)
            parameter_set_id, parameter_set_already_exists, name = (
                self.update_parameter_set_from_json(file_as_json, file_path)
            )
            new_or_updated.append(name)
            if parameter_set_already_exists:
                existing_ids_to_be_deleted.remove(parameter_set_id)

        if existing_ids_to_be_deleted:
            for id_to_be_deleted in existing_ids_to_be_deleted:
                deleted.append(self.delete_parameter_set_by_id(id_to_be_deleted))

            print(
                "\n SQL tables parameter and parameter_set are up to date according to the templates resource files"
            )
            if new_or_updated:
                print(" Created or updated parameter_set : ", new_or_updated)
            if deleted:
                print(" Deleted parameter_set: ", deleted)


if __name__ == "__main__":
    UpdateParameterSets(print_details=True).execute_script()
