from python.resources.db import db_handler, db_access


class TemplateField(object):
    def __init__(self):
        self.type = "type"
        self.unit_name = "unit_name"
        self.unit_dimension = "unit_dimension"
        self.max_value = "max_value"
        self.min_value = "min_value"
        self.is_shown_to_user = "is_shown_to_user"
        self.description = "description"


class UpdateTemplates:

    def __init__(self, print_details=False):
        self.template_type = "template"
        self.sql_template = db_handler.TemplateHandler()
        self.sql_template_parameter = db_handler.TemplateParameterHandler()
        self.print_details = print_details

    def update_template_from_json(self, template, path):
        """
        template: {
            "Type": "template",
            "Name": "file_name",
            "Parameters":{
                "maximum_concentration": {
                    "max_value": 100000.0,
                    "min_value": 1000.0,
                    "description": "",
                    "is_shown_to_user": true,
                    "type": "float",
                    "unit_name": "mole.meter\u207b\u00b3",
                    "unit_dimension": "mol.m\u207b\u00b3"
                },
                "volume_fraction": {
                    "max_value": 0.99,
                    "min_value": 0.01,
                    "description": "",
                    "is_shown_to_user": true,
                    "type": "float",
                    "unit_name": "1",
                    "unit_dimension": "1"
                },
                "diffusion_coefficient": {
                    "type": "function"
                },
                "charge_carrier_name": {
                    "description": "",
                    "is_shown_to_user": true,
                    "type": "str"
                },
                "etc": "etc"
            }
        }
        """
        name = template.get("Name")
        type = template.get("Type")
        parameters = template.get("Parameters")

        if type != self.template_type:
            # not a template
            return None, False

        assert name is not None, "Name of template {} must have a name".format(path)
        assert parameters is not None, "Parameters of template {} is not defined".format(name)

        template_id, template_already_exists = self.create_or_update_parameter_set(
            name=name
        )
        fields = TemplateField()

        if template_already_exists:
            if self.print_details:
                print("\n Updating {}".format(name))

            self.update_parameters(
                parameters=parameters,
                template_id=template_id,
                fields=fields
            )
        else:
            if self.print_details:
                print("\n Creating {}".format(name))

            self.add_parameters(
                parameters=parameters,
                template_id=template_id,
                fields=fields
            )

        return template_id, template_already_exists, name

    def create_or_update_parameter_set(self, name):
        template_id = self.sql_template.get_id_from_name(name)
        return (template_id, True) if template_id else (self.sql_template.insert_value(name=name), False)

    def add_parameters(self, parameters, template_id, fields):
        added_parameters = []
        for parameter in parameters:
            details = parameters.get(parameter)

            self.sql_template_parameter.insert_value(
                name=parameter,
                template_id=template_id,
                type=details.get(fields.type),
                unit_name=details.get(fields.unit_name),
                unit_dimension=details.get(fields.unit_dimension),
                max_value=details.get(fields.max_value),
                min_value=details.get(fields.min_value),
                is_shown_to_user=details.get(fields.is_shown_to_user),
                description=details.get(fields.description)
            )
            added_parameters.append(parameter)
        if self.print_details:
            print('  Added parameters: ', added_parameters)

    def update_parameters(self, parameters, template_id, fields):
        new_parameters = {}
        existing_ids_to_be_deleted = self.sql_template_parameter.get_all_ids_by_template_id(template_id)

        for parameter in parameters:
            details = parameters.get(parameter)
            parameter_id = self.sql_template_parameter.get_id_from_name_and_template_id(
                name=parameter,
                template_id=template_id
            )
            if parameter_id:  # existing parameter, update fields
                try:
                    self.sql_template_parameter.update_by_id(
                        id=parameter_id,
                        columns_and_values={
                            "type": details.get(fields.type),
                            "unit_name": details.get(fields.unit_name),
                            "unit_dimension": details.get(fields.unit_dimension),
                            "max_value": details.get(fields.max_value),
                            "min_value": details.get(fields.min_value),
                            "is_shown_to_user": details.get(fields.is_shown_to_user),
                            "description": details.get(fields.description),
                        }
                    )
                    existing_ids_to_be_deleted.remove(parameter_id)
                except:
                    # SQL query in update_by_id could fail, for example for str containing quotes
                    # In that case, we delete and recreate the parameter instead of updating it
                    new_parameters[parameter] = details

            else:  # non-existing parameter, create it
                new_parameters[parameter] = details

        # add new params and delete unused ones
        self.add_parameters(new_parameters, template_id, fields)

        deleted_parameters = []
        for id_to_delete in existing_ids_to_be_deleted:
            deleted_parameters.append(self.sql_template_parameter.get_name_from_id(id_to_delete))
            self.sql_template_parameter.delete_by_id(id_to_delete)

        if self.print_details:
            print('  Deleted parameters: ', deleted_parameters)

    #####################################
    #    DELETE TEMPLATE
    #####################################
    def delete_template_by_id(self, template_id):
        template = self.sql_template.select_by_id(template_id)
        if template:
            _, name = template
            parameter_ids = self.sql_template_parameter.get_all_ids_by_template_id(template_id)

            self.sql_template.delete_by_id(template_id)
            for parameter_id in parameter_ids:
                self.sql_template_parameter.delete_by_id(parameter_id)

            return name

    #####################################
    #    RUN SCRIPT
    #####################################
    def get_all_resources(self):
        return db_access.get_all_template_files_path()

    def execute_script(self):
        all_file_path = self.get_all_resources()
        existing_ids_to_be_deleted = self.sql_template.get_all_ids()

        new_or_updated = []
        deleted = []

        for file_path in all_file_path:
            file_as_json = db_access.get_json_from_path(file_path)
            template_id, template_already_exists, name = self.update_template_from_json(file_as_json, file_path)
            new_or_updated.append(name)
            if template_already_exists:
                existing_ids_to_be_deleted.remove(template_id)

        for id_to_be_deleted in existing_ids_to_be_deleted:
            deleted.append(self.delete_template_by_id(id_to_be_deleted))

        print("\n SQL tables template and template_parameter are up to date according to the templates resource files")
        if new_or_updated:
            print(" Created or updated templates : ", new_or_updated)
        if deleted:
            print(" Deleted templates: ", deleted)


if __name__ == "__main__":
    UpdateTemplates(print_details=True).execute_script()
