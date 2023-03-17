import os
import json
import sqlite3
db_name = "BattMo_gui.db"


def get_sqlite_con_and_cur():
    current_path = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_path, db_name)
    con = sqlite3.connect(db_path, check_same_thread=False)
    return con, con.cursor()


def get_path_to_db_dir():
    current_path = os.path.dirname(os.path.abspath(__file__))
    python_dir = os.path.abspath(os.path.join(current_path, os.pardir))
    return os.path.join(python_dir, "db")


def get_path_to_parameters_dir():
    return os.path.join(get_path_to_db_dir(), "resources", "parameters")


def get_path_to_templates_dir():
    return os.path.join(get_path_to_db_dir(), "resources", "templates")


def get_path_to_categories():
    file_name = "categories.json"
    return os.path.join(get_path_to_db_dir(), "resources", file_name)


def get_path_to_tabs():
    file_name = "tabs.json"
    return os.path.join(get_path_to_db_dir(), "resources", file_name)


def get_path_to_models():
    file_name = "models.json"
    return os.path.join(get_path_to_db_dir(), "resources", file_name)


def get_all_parameter_files_path():
    all_files = []
    for root, _, files in os.walk(get_path_to_parameters_dir()):
        for name in files:
            all_files.append(os.path.join(root, name))
    return all_files


def get_all_template_files_path():
    all_files = []
    for root, _, files in os.walk(get_path_to_templates_dir()):
        for name in files:
            all_files.append(os.path.join(root, name))
    return all_files


def get_json_from_path(path):
    return json.load(open(path))
