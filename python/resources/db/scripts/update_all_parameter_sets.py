from python.resources.db import db_handler, db_access

sql_parameter = db_handler.ParameterHandler()
sql_parameter_set = db_handler.ParameterSetHandler()
sql_category = db_handler.CategoryHandler()
sql_parameter_set_header = db_handler.ParameterSetHeaderHandler()


#####################################
#    UPDATE PARAMETER SET
#####################################

class ParameterField(object):
    def __init__(self):
        self.value = "value"
        self.type = "type"
        self.unit_name = "unit_name"
        self.unit_dimension = "unit_dimension"
        self.max_value = "max_value"
        self.min_value = "min_value"
        self.is_shown_to_user = "is_shown_to_user"
        self.description = "description"


def update_parameter_set_from_json(parameter_set, path):
    """
    parameter_set: {
        "Name": "file_name",
        "Header":{
            "DOI": "EMMO_12345",
            "description": "new parameter_set for electrolyte from Chen 2020"
        },
        "Category": "electrolyte",
        "Parameters":{
            "maximum_concentration": {
                "value": 31540,
                "max_value": 100000.0,
                "min_value": 1000.0,
                "description": "",
                "is_shown_to_user": true,
                "type": "float",
                "unit_name": "mole.meter\u207b\u00b3",
                "unit_dimension": "mol.m\u207b\u00b3"
            },
            "volume_fraction": {
                "value": 0.7,
                "max_value": 0.99,
                "min_value": 0.01,
                "description": "",
                "is_shown_to_user": true,
                "type": "float",
                "unit_name": "1",
                "unit_dimension": "1"
            },
            "etc": "etc"
        }
    }
    """
    name = parameter_set.get("Name")
    header = parameter_set.get("Header")
    category = parameter_set.get("Category")
    parameters = parameter_set.get("Parameters")

    assert name is not None, "Name of parameter_set {} must have a name".format(path)
    assert header is not None, "Header of parameter_set {} is not defined".format(name)
    assert category is not None, "Category of parameter_set {} is not defined".format(name)
    assert parameters is not None, "Parameters of parameter_set {} is not defined".format(name)

    category_id = sql_category.get_id_from_name(category)
    assert category_id is not None, "Category = {} is not specified in categories.json. path={}".format(category, path)

    header_id = create_or_update_header(header)
    parameter_set_id, parameter_set_already_exists = create_or_update_parameter_set(
        name=name,
        category_id=category_id,
        header_id=header_id
    )
    fields = ParameterField()
    if parameter_set_already_exists:
        print("\n Updating {}".format(name))
        update_parameters(
            parameters=parameters,
            parameter_set_id=parameter_set_id,
            fields=fields
        )
    else:
        print("\n Creating {}".format(name))
        add_parameters(
            parameters=parameters,
            parameter_set_id=parameter_set_id,
            fields=fields
        )
    return parameter_set_id, parameter_set_already_exists


def create_or_update_header(header):
    doi = header.get("DOI")
    description = header.get("description")

    if doi is None:
        doi = 'doi'

    if description is None:
        description = " "

    header_id = sql_parameter_set_header.get_id_from_doi(doi)

    if header_id:
        sql_parameter_set_header.update_by_id(
            id=header_id,
            columns_and_values={'description': description},
        )
        return header_id

    else:
        return sql_parameter_set_header.insert_value(
            doi=doi,
            description=description
        )


def create_or_update_parameter_set(name, category_id, header_id):
    parameter_set_id = sql_parameter_set.get_id_by_name_and_category(name, category_id)

    if parameter_set_id:
        sql_parameter_set.update_by_id(
            id=parameter_set_id,
            columns_and_values={
                "category_id": category_id,
                "header_id": header_id
            }
        )
        return parameter_set_id, True
    else:
        return sql_parameter_set.insert_value(
            name=name,
            category_id=category_id,
            header_id=header_id
        ), False


def add_parameters(parameters, parameter_set_id, fields):
    added_parameters = []
    for parameter in parameters:
        details = parameters.get(parameter)
        value = details.get(fields.value)
        value_type = details.get(fields.type)
        formatted_value = format_value(value, value_type, details)
        description = details.get(fields.description)

        sql_parameter.insert_value(
            name=parameter,
            parameter_set_id=parameter_set_id,
            value=formatted_value,
            type=value_type,
            unit_name=details.get(fields.unit_name),
            unit_dimension=details.get(fields.unit_dimension),
            max_value=details.get(fields.max_value),
            min_value=details.get(fields.min_value),
            is_shown_to_user=details.get(fields.is_shown_to_user),
            description=description if description else ""
        )
        added_parameters.append(parameter)
    print('  Added parameters: ', added_parameters)


def update_parameters(parameters, parameter_set_id, fields):
    new_parameters = {}
    existing_ids_to_be_deleted = sql_parameter.get_all_ids_by_parameter_set_id(parameter_set_id)

    for parameter in parameters:
        details = parameters.get(parameter)
        parameter_id = sql_parameter.get_id_from_name_and_parameter_set_id(
            name=parameter,
            parameter_set_id=parameter_set_id
        )
        if parameter_id:  # existing parameter, update fields
            value = details.get(fields.value)
            value_type = details.get(fields.type)
            formatted_value = format_value(value, value_type, details)
            try:
                sql_parameter.update_by_id(
                    id=parameter_id,
                    columns_and_values={
                        "value": formatted_value,
                        "type": value_type,
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
    add_parameters(new_parameters, parameter_set_id, fields)

    deleted_parameters = []
    for id_to_delete in existing_ids_to_be_deleted:
        deleted_parameters.append(sql_parameter.get_name_from_id(id_to_delete))
        sql_parameter.delete_by_id(id_to_delete)
    print('  Deleted parameters: ', deleted_parameters)


def format_value(value, value_type, details):
    if value is None:
        return str(details) if value_type == "function" else None
    else:
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
    return db_access.get_all_parameter_files_path()


def execute_script():
    all_file_path = get_all_resources()
    existing_ids_to_be_deleted = sql_parameter_set.get_all_ids()
    for file_path in all_file_path:
        file_as_json = db_access.get_json_from_path(file_path)
        parameter_set_id, parameter_set_already_exists = update_parameter_set_from_json(file_as_json, file_path)
        if parameter_set_already_exists:
            existing_ids_to_be_deleted.remove(parameter_set_id)

    for id_to_be_deleted in existing_ids_to_be_deleted:
        delete_parameter_set_by_id(id_to_be_deleted)


if __name__ == "__main__":
    execute_script()
