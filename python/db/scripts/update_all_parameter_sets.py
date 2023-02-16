from python.db import db_handler
from python.db import db_connect

sql_parameter = db_handler.ParameterHandler()
sql_parameter_set = db_handler.ParameterSetHandler()
sql_category = db_handler.CategoryHandler()
sql_parameter_set_header = db_handler.ParameterSetHeaderHandler()


#####################################
#    UPDATE PARAMETER SET
#####################################
def update_parameter_set_from_json(parameter_set):
    """
    parameter_set: {
        "Name": "file_name",
        "Header":{
            "DOI": "EMMO_12345",
            "description": "new parameter_set for electrolyte from Chen 2020"
        },
        "Category": "electrolyte",
        "Parameters":{
            "initialTemperature": 298.15,
            "electrodeArea": 0.016808,
            "etc": "etc"
        }

    }
    """
    name = parameter_set.get("Name")
    header = parameter_set.get("Header")
    category = parameter_set.get("Category")
    parameters = parameter_set.get("Parameters")

    assert name is not None, "parameter_set must have a name"
    assert header is not None, "parameter_set must have header"
    assert category is not None, "category is not defined"
    assert parameters is not None, "parameter_set has no parameters"

    category_id = sql_category.get_id_from_name(category)
    assert category_id is not None, "Category = {} is not specified in categories.json".format(category)

    header_id = create_or_update_header(header)
    parameter_set_id, parameter_set_already_exists = create_or_update_parameter_set(
        name=name,
        category_id=category_id,
        header_id=header_id
    )

    if parameter_set_already_exists:
        print("\n Updating {}".format(name))
        update_parameters(
            parameters=parameters,
            parameter_set_id=parameter_set_id
        )
    else:
        print("\n Creating {}".format(name))
        add_parameters(
            parameters=parameters,
            parameter_set_id=parameter_set_id
        )
    return parameter_set_id, parameter_set_already_exists


def create_or_update_header(header):
    doi = header.get("DOI")
    description = header.get("description")

    header_id = sql_parameter_set_header.get_id_from_doi(doi)
    if header_id:
        sql_parameter_set_header.update_by_id(
            id=header_id,
            columns_and_values={'description': description},
        )
        return header_id

    else:
        return sql_parameter_set_header.insert_value(
            doi='doi',
            description='description'
        )


def create_or_update_parameter_set(name, category_id, header_id):
    parameter_set_id = sql_parameter_set.get_id_by_name_and_category(name, category_id)

    if parameter_set_id:
        sql_parameter_set.update_by_id(
            id=parameter_set_id,
            columns_and_values={
                "category_id": category_id
            }
        )
        return parameter_set_id, True
    else:
        return sql_parameter_set.insert_value(
            name=name,
            category_id=category_id,
            headers_id=header_id
        ), False


def add_parameters(parameters, parameter_set_id):
    added_parameters = []
    for parameter in parameters:
        value = parameters.get(parameter)
        value_type = type(value).__name__
        formatted_value = format_value(value, value_type)

        sql_parameter.insert_value(
            name=parameter,
            value=formatted_value,
            value_type=value_type,
            parameter_set_id=parameter_set_id,
            is_shown_to_user=value_type not in ["dict", "list"]
        )
        added_parameters.append(parameter)
    print('  Added parameters: ', added_parameters)


def update_parameters(parameters, parameter_set_id):
    new_parameters = {}
    existing_ids_to_be_deleted = sql_parameter.get_all_ids_by_parameter_set_id(parameter_set_id)
    for parameter in parameters:
        parameter_id = sql_parameter.get_id_from_name_and_parameter_set_id(
            name=parameter,
            parameter_set_id=parameter_set_id
        )
        if parameter_id:
            value = parameters.get(parameter)
            value_type = type(value).__name__
            formatted_value = format_value(value, value_type)
            try:
                sql_parameter.update_by_id(
                    id=parameter_id,
                    columns_and_values={
                        "value": formatted_value,
                        "value_type": value_type,
                        "is_shown_to_user": value_type not in ["dict", "list"]
                    }
                )
                existing_ids_to_be_deleted.remove(parameter_id)
            except:
                # SQL query in update_by_id could fail for str containing quotes
                # In that case, we delete and recreate the parameter instead of updating it
                new_parameters[parameter] = parameters.get(parameter)
        else:
            new_parameters[parameter] = parameters.get(parameter)

    # add new params and delete unused ones
    add_parameters(new_parameters, parameter_set_id)

    deleted_parameters = []
    for id_to_delete in existing_ids_to_be_deleted:
        deleted_parameters.append(sql_parameter.get_name_from_id(id_to_delete))
        sql_parameter.delete_by_id(id_to_delete)
    print('  Deleted parameters: ', deleted_parameters)


def format_value(value, value_type):
    return value if value_type == "str" else str(value)


#####################################
#    DELETE PARAMETER SET
#####################################
def delete_parameter_set_by_id(parameter_set_id):
    parameter_set = sql_parameter_set.select_by_id(parameter_set_id)
    if parameter_set:
        _, name, category_id, header_id = parameter_set
        parameter_ids = sql_parameter.get_all_ids_by_parameter_set_id(parameter_set_id)

        sql_parameter_set.delete_by_id(parameter_set_id)
        sql_parameter_set_header.delete_by_id(header_id)
        for parameter_id in parameter_ids:
            sql_parameter.delete_by_id(parameter_id)
        print("\n Parameter_set(name = {}, type={}) has been deleted.".format(
            name,
            sql_category.get_name_from_id(category_id)
        ))


#####################################
#    RUN SCRIPT
#####################################
def get_all_resources():
    return db_connect.get_all_parameter_files_path()


def execute_script():
    all_file_path = get_all_resources()
    existing_ids_to_be_deleted = sql_parameter_set.get_all_ids()
    for file_path in all_file_path:
        file_as_json = db_connect.get_json_from_path(file_path)
        parameter_set_id, parameter_set_already_exists = update_parameter_set_from_json(file_as_json)
        if parameter_set_already_exists:
            existing_ids_to_be_deleted.remove(parameter_set_id)

    for id_to_be_deleted in existing_ids_to_be_deleted:
        delete_parameter_set_by_id(id_to_be_deleted)


if __name__ == "__main__":
    execute_script()
