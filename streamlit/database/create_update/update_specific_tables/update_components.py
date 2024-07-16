import os
import sys

##############################
# Set page directory to base level to allow for module import from different folder
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
)
##############################

from database import db_handler
from app_scripts import app_access


class UpdateComponents:

    def __init__(self):
        self.sql_component = db_handler.ComponentHandler()
        self.sql_category = db_handler.CategoryHandler()
        self.sql_tab = db_handler.TabHandler()
        self.sql_template = db_handler.TemplateHandler()
        self.sql_model = db_handler.ModelHandler()

    def get_resource_as_json(self):
        return app_access.get_json_from_path(app_access.get_path_to_components())

    def update_component_from_json(self, resource_file):
        """
        resource_file: {
            "components": {
                "component_name_1": {
                    "category_name": "category_1",
                    "description": "this new category is used for this type of electrode,
                                    which will be displayed on category_1"
                },
                "component_name_2": {
                    "category_name": "category_2",
                    "display_name": "component 2",
                    "description": "this component exists but has new description"
                }
            }
        }
        """
        components = resource_file.get("components")
        assert components is not None, "This input format is not handled"

        new_types = []
        updated_types = []
        # every item which is not updated will be deleted, so we don't keep useless items in db
        existing_ids_to_be_deleted = self.sql_component.get_all_ids()

        for component_name in components:
            details = components.get(component_name)
            model_names = details.get("model_name")
            for model_name in model_names:
                category_name = details.get("category_name")
                tab_name = details.get("tab_name")

                category_id = self.sql_category.get_id_from_name(category_name)
                tab_id = self.sql_tab.get_id_from_name(tab_name)

                if category_id or tab_id:

                    # if model_name == "p2d_p3d_p4d":
                    #     model = "P2D"
                    #     model_id = self.sql_model.get_model_id_from_model_name(model)
                    # if model_name == "p3d_p4d":
                    #     model = "P3D"
                    #     model_id = self.sql_model.get_model_id_from_model_name(model)
                    # if model_name == "p4d":
                    #     model = "P4D"
                    #     model_id = self.sql_model.get_model_id_from_model_name(model)

                    material = int(details.get("material"))
                    difficulty = details.get("difficulty")
                    context_type = details.get("context_type")
                    context_type_iri = details.get("context_type_iri")
                    emmo_relation = details.get("emmo_relation")
                    description = details.get("description")
                    display_name = details.get("display_name")
                    default_template = details.get("default_template")

                    default_template_id = self.sql_template.get_id_from_name(default_template)
                    assert (
                        default_template_id is not None
                    ), "invalid default_template={} for component {}".format(
                        default_template, component_name
                    )

                    component_id = self.sql_component.get_id_from_name_and_model(
                        component_name, model_name
                    )
                    if component_id:  # existing type
                        self.sql_component.update_by_id(
                            id=component_id,
                            columns_and_values={
                                "category_id": category_id,
                                "tab_id": tab_id,
                                "model_name": model_name,
                                "difficulty": difficulty,
                                "material": material,
                                "context_type": context_type,
                                "context_type_iri": context_type_iri,
                                "emmo_relation": emmo_relation,
                                "display_name": display_name,
                                "description": description,
                                "default_template_id": default_template_id,
                            },
                        )
                        updated_types.append(component_name)
                        if existing_ids_to_be_deleted:
                            existing_ids_to_be_deleted.remove(component_id)

                    else:  # non-existing type, create it
                        self.sql_component.insert_value(
                            name=component_name,
                            category_id=category_id,
                            tab_id=tab_id,
                            model_name=model_name,
                            difficulty=difficulty,
                            material=material,
                            context_type=context_type,
                            context_type_iri=context_type_iri,
                            emmo_relation=emmo_relation,
                            display_name=display_name,
                            description=description,
                            default_template_id=default_template_id,
                        )
                        new_types.append(component_name)

                else:
                    print(
                        "category name = {} is not specified in the SQL table category".format(
                            category_name
                        )
                    )
                    print(
                        "component {} has not be saved in db since category_name {} is not in db".format(
                            component_name, category_name
                        )
                    )

        # Delete unused types which remain in the sql table
        deleted_types = []
        if existing_ids_to_be_deleted:
            for id_to_delete in existing_ids_to_be_deleted:
                deleted_types.append(self.sql_component.get_name_from_id(id_to_delete))
                self.sql_component.delete_by_id(id_to_delete)

            print(
                "\n SQL table category is up to date according to the resource file components.json"
            )
            if updated_types:
                print(" Updated components : ", updated_types)
            if new_types:
                print(" New components: ", new_types)
            if deleted_types:
                print(" Deleted components: ", deleted_types)

    def execute_script(self):
        return self.update_component_from_json(self.get_resource_as_json())


if __name__ == "__main__":
    UpdateComponents().execute_script()
