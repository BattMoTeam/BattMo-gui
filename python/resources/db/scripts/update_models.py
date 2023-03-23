from python.resources.db import db_handler, db_access


class UpdateModels:

    def __init__(self):
        self.sql_model = db_handler.ModelHandler()
        self.sql_model_parameter = db_handler.ModelParameterHandler()

    def get_resource_as_json(self):
        return db_access.get_json_from_path(
            db_access.get_path_to_models()
        )

    def update_model_from_json(self, resource_file):
        """
        resource_file: {
            "models": {
                "model_name_1": {
                    "description": "this is a new model",
                    "parameters": {
                        "include_current_collector": {
                             "value": false,
                             "description": "",
                             "type": "bool"
                          },
                          "use_solid_diffusion_model": {
                             "value": true,
                             "description": "",
                             "type": "bool"
                          }
                    }
                },
                "model_name_2": {
                    "description": "this model exists but has new description",
                    "parameters": {
                        ...
                    }
                }
            }
        }
        """
        models = resource_file.get("models")
        assert models is not None, "This input format is not handled"

        new_types = []
        updated_types = []
        existing_ids_to_be_deleted = self.sql_model.get_all_ids()

        for model_name in models:
            details = models.get(model_name)
            parameters = details.get("parameters")
            description = details.get("description")
            model_id = self.sql_model.get_id_from_name(model_name)

            if model_id:  # existing type
                self.sql_model.update_by_id(
                    id=model_id,
                    columns_and_values={
                        "description": description
                    }
                )
                updated_types.append(model_name)
                existing_ids_to_be_deleted.remove(model_id)

            else:  # non-existing type, create it
                model_id = self.sql_model.insert_value(
                    name=model_name,
                    description=description
                )
                new_types.append(model_name)

            self.create_or_update_parameters(model_id, parameters)

        # Delete unused models which remain in the sql table
        deleted_types = []
        for id_to_delete in existing_ids_to_be_deleted:
            deleted_types.append(self.sql_model.get_name_from_id(id_to_delete))
            self.sql_model.delete_by_id(id_to_delete)
            self.create_or_update_parameters(id_to_delete, {})  # trick to delete corresponding parameters

        print("\n SQL tables model and model_parameters are up to date according to the resource file models.json")
        if updated_types:
            print(" Updated models : ", updated_types)
        if new_types:
            print(" New models: ", new_types)
        if deleted_types:
            print(" Deleted models: ", deleted_types)

    def create_or_update_parameters(self, model_id, parameters):
        existing_ids_to_be_deleted = self.sql_model_parameter.get_all_ids_by_model_id(model_id)

        for parameter_name in parameters:
            details = parameters.get(parameter_name)
            value = details.get("value")
            value_type = details.get("type")
            description = details.get("description")
            parameter_id = self.sql_model_parameter.get_id_from_name_and_model_id(parameter_name, model_id)

            if parameter_id:  # existing parameter
                self.sql_model_parameter.update_by_id(
                    id=parameter_id,
                    columns_and_values={
                        "value": value,
                        "type": value_type,
                        "description": description
                    }
                )
                existing_ids_to_be_deleted.remove(parameter_id)

            else:  # non-existing parameter, create it
                self.sql_model_parameter.insert_value(
                    name=parameter_name,
                    model_id=model_id,
                    value=value,
                    type=value_type,
                    description=description
                )

        for id_to_delete in existing_ids_to_be_deleted:
            self.sql_model_parameter.delete_by_id(id_to_delete)

    def execute_script(self):
        return self.update_model_from_json(self.get_resource_as_json())


if __name__ == "__main__":
    UpdateModels().execute_script()
