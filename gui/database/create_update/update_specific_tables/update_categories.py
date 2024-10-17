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


class UpdateCategories:

    def __init__(self):
        self.sql_category = db_handler.CategoryHandler()
        self.sql_tab = db_handler.TabHandler()
        self.sql_template = db_handler.TemplateHandler()
        self.sql_model = db_handler.ModelHandler()

    def get_resource_as_json(self):
        return app_access.get_json_from_path(app_access.get_path_to_categories())

    def update_category_from_json(self, resource_file):
        """
        resource_file: {
            "categories": {
                "category_name_1": {
                    "tab_name": "tab_1",
                    "description": "this new category is used for this type of electrode,
                                    which will be displayed on tab_1"
                },
                "category_name_2": {
                    "tab_name": "tab_2",
                    "display_name": "Tab 2",
                    "description": "this category exists but has new description"
                }
            }
        }
        """
        categories = resource_file.get("categories")
        assert categories is not None, "This input format is not handled"

        new_types = []
        updated_types = []
        # every item which is not updated will be deleted, so we don't keep useless items in db
        existing_ids_to_be_deleted = self.sql_category.get_all_ids()

        for category_name in categories:
            details = categories.get(category_name)
            model_names = details.get("model_name")
            for model_name in model_names:
                tab_name = details.get("tab_name")
                tab_id = self.sql_tab.get_id_from_name_and_model(tab_name, model_name)

                if tab_id:

                    tab_id = tab_id[0]
                    difficulty = details.get("difficulty")
                    context_type = details.get("context_type")
                    context_type_iri = details.get("context_type_iri")
                    emmo_relation = details.get("emmo_relation")
                    description = details.get("description")
                    display_name = details.get("display_name")
                    default_template = details.get("default_template")
                    print(display_name)
                    default_template_id = self.sql_template.get_id_from_name(default_template)
                    assert (
                        default_template_id is not None
                    ), "invalid default_template={} for category {}".format(
                        default_template, category_name
                    )

                    category_id = self.sql_category.get_id_from_name_and_model(
                        category_name, model_name
                    )
                    if category_id:  # existing type
                        self.sql_category.update_by_id(
                            id=category_id,
                            columns_and_values={
                                "tab_id": tab_id,
                                "model_name": model_name,
                                "difficulty": difficulty,
                                "context_type": context_type,
                                "context_type_iri": context_type_iri,
                                "emmo_relation": emmo_relation,
                                "display_name": display_name,
                                "description": description,
                                "default_template_id": default_template_id,
                            },
                        )
                        updated_types.append(category_name)
                        if existing_ids_to_be_deleted:
                            existing_ids_to_be_deleted.remove(category_id)

                    else:  # non-existing type, create it
                        self.sql_category.insert_value(
                            name=category_name,
                            tab_id=tab_id,
                            model_name=model_name,
                            difficulty=difficulty,
                            context_type=context_type,
                            context_type_iri=context_type_iri,
                            emmo_relation=emmo_relation,
                            display_name=display_name,
                            description=description,
                            default_template_id=default_template_id,
                        )
                        new_types.append(category_name)
                else:
                    print("Tab name = {} is not specified in the SQL table Tabs".format(tab_name))
                    print(
                        "Category {} has not be saved in db since tab_name {} is not in db".format(
                            category_name, tab_name
                        )
                    )

        # Delete unused types which remain in the sql table
        deleted_types = []
        if existing_ids_to_be_deleted:
            for id_to_delete in existing_ids_to_be_deleted:
                deleted_types.append(self.sql_category.get_name_from_id(id_to_delete))
                self.sql_category.delete_by_id(id_to_delete)

            print(
                "\n SQL table category is up to date according to the resource file categories.json"
            )
            if updated_types:
                print(" Updated categories : ", updated_types)
            if new_types:
                print(" New categories: ", new_types)
            if deleted_types:
                print(" Deleted categories: ", deleted_types)

    def execute_script(self):
        return self.update_category_from_json(self.get_resource_as_json())


if __name__ == "__main__":
    UpdateCategories().execute_script()
