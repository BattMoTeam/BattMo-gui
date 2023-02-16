from python.db import db_handler
from python.db import db_connect

sql_category = db_handler.CategoryHandler()


def get_resource_as_json():
    return db_connect.get_json_from_path(
        db_connect.get_path_to_categories()
    )


def update_category_from_json(resource_file):
    """
    resource_file: {
        "categories": {
            "type_1": {
                "name": "new_type_1",
                "description": "this new category is used for this type of electrode"
            },
            "type_2": {
                "name": "existing_type",
                "description": "this category exists but has new description"
            }
        }
    }
    """
    categories = resource_file.get("categories")
    assert categories is not None, "This input format is not handled"

    new_types = []
    updated_types = []
    existing_ids_to_be_deleted = sql_category.get_all_ids()

    for category in categories:
        name = categories.get(category).get("name")
        description = categories.get(category).get("description")

        if name:
            category_id = sql_category.get_id_from_name(name)
            if category_id:  # existing type, only update description
                sql_category.update_by_id(
                    id=category_id,
                    columns_and_values={'description': description}
                )
                updated_types.append(name)
                existing_ids_to_be_deleted.remove(category_id)

            else:  # non-existing type, create it
                sql_category.insert_value(
                    name=name,
                    description=description
                )
                new_types.append(name)

        else:
            print("category's name can't be None.")

    # Delete unused types which remain in the sql table
    deleted_types = []
    for id_to_delete in existing_ids_to_be_deleted:
        deleted_types.append(sql_category.get_name_from_id(id_to_delete))
        sql_category.delete_by_id(id_to_delete)

    print(
        "\n SQL table category is up to date according to the resource file categories.json",
        "\n Updated categories : ", updated_types,
        "\n New categories: ", new_types,
        "\n Deleted categories: ", deleted_types
    )


def execute_script():
    return update_category_from_json(get_resource_as_json())


if __name__ == "__main__":
    execute_script()
