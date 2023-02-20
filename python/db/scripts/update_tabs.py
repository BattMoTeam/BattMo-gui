from python.db import db_handler
from python.db import db_connect

sql_tab = db_handler.TabHandler()


def get_resource_as_json():
    return db_connect.get_json_from_path(
        db_connect.get_path_to_tabs()
    )


def update_tab_from_json(resource_file):
    """
    resource_file: {
        "tabs": {
            "tab_name_1": {
                "description": "this new tab is used for this type of electrode"
            },
            "tab_name_2": {
                "description": "this tab exists but has new description"
            }
        }
    }
    """
    tabs = resource_file.get("tabs")
    assert tabs is not None, "This input format is not handled"

    new_types = []
    updated_types = []
    existing_ids_to_be_deleted = sql_tab.get_all_ids()

    for tab_name in tabs:

        description = tabs.get(tab_name).get("description")
        tab_id = sql_tab.get_id_from_name(tab_name)

        if tab_id:  # existing type, only update description
            sql_tab.update_by_id(
                id=tab_id,
                columns_and_values={"description": description}
            )
            updated_types.append(tab_name)
            existing_ids_to_be_deleted.remove(tab_id)

        else:  # non-existing type, create it
            sql_tab.insert_value(
                name=tab_name,
                description=description
            )
            new_types.append(tab_name)

    # Delete unused types which remain in the sql table
    deleted_types = []
    for id_to_delete in existing_ids_to_be_deleted:
        deleted_types.append(sql_tab.get_name_from_id(id_to_delete))
        sql_tab.delete_by_id(id_to_delete)

    print(
        "\n SQL table tab is up to date according to the resource file tabs.json",
        "\n Updated tabs : ", updated_types,
        "\n New tabs: ", new_types,
        "\n Deleted tabs: ", deleted_types
    )


def execute_script():
    return update_tab_from_json(get_resource_as_json())


if __name__ == "__main__":
    execute_script()
