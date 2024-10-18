import os
import json
import sqlite3
import streamlit as st

db_name = "BattMo_gui.db"

"""
Get paths and connections to files
"""


###########
## PATHS ##
###########


@st.cache_data
def get_path_to_app_scripts():
    current_path = os.path.dirname(os.path.abspath(__file__))
    return current_path


@st.cache_data
def get_path_to_streamlit_dir():
    app_scripts_path = get_path_to_app_scripts()
    streamlit_path = os.path.dirname(app_scripts_path)
    return streamlit_path


@st.cache_data
def get_path_to_pages_dir():
    streamlit_path = get_path_to_streamlit_dir()
    pages_path = os.path.join(streamlit_path, "app_pages")
    return pages_path


@st.cache_data
def get_path_to_html_dir():
    streamlit_path = get_path_to_streamlit_dir()
    html_path = os.path.join(streamlit_path, "html")
    return html_path


@st.cache_data
def get_path_to_light_style_css():
    html_path = get_path_to_html_dir()
    light_style_css_path = os.path.join(html_path, "light_style.css")
    return light_style_css_path


@st.cache_data
def get_path_to_custom_style_css():
    html_path = get_path_to_html_dir()
    light_style_css_path = os.path.join(html_path, "light_style.css")
    return light_style_css_path


@st.cache_data
def get_path_to_dark_style_css():
    html_path = get_path_to_html_dir()
    dark_style_css_path = os.path.join(html_path, "dark_style.css")
    return dark_style_css_path


@st.cache_data
def get_path_to_input_files_dir():
    streamlit_path = get_path_to_streamlit_dir()
    input_files_path = os.path.join(streamlit_path, "input_files")
    return input_files_path


@st.cache_data
def get_path_to_battmo_formatted_input():
    input_files_path = get_path_to_input_files_dir()
    battmo_formatted_input_path = os.path.join(input_files_path, "battmo_formatted_input.json")
    return battmo_formatted_input_path


@st.cache_data
def get_path_to_uploaded_input():
    input_files_path = get_path_to_input_files_dir()
    uploaded_input_path = os.path.join(input_files_path, "uploaded_input.json")
    return uploaded_input_path


@st.cache_data
def get_path_to_gui_formatted_input():
    input_files_path = get_path_to_input_files_dir()
    gui_formatted_input_path = os.path.join(input_files_path, "gui_formatted_input.json")
    return gui_formatted_input_path


@st.cache_data
def get_path_to_linked_data_input():
    input_files_path = get_path_to_input_files_dir()
    linked_data_input_path = os.path.join(input_files_path, "linked_data_input.json")
    return linked_data_input_path


@st.cache_data
def get_path_to_output_files_dir():
    streamlit_path = get_path_to_streamlit_dir()
    output_files_path = os.path.join(streamlit_path, "output_files")
    return output_files_path


@st.cache_data
def get_path_to_uploaded_hdf5_files_dir():
    streamlit_path = get_path_to_streamlit_dir()
    uploaded_hdf5_files_path = os.path.join(streamlit_path, "uploaded_hdf5_files")
    return uploaded_hdf5_files_path


@st.cache_data
def get_path_to_zipped_results():
    output_files_path = get_path_to_output_files_dir()
    zipped_results_path = os.path.join(output_files_path, "zipped")
    return zipped_results_path


@st.cache_data
def get_path_to_battmo_results():
    output_files_path = get_path_to_output_files_dir()
    battmo_results_path = os.path.join(output_files_path, "battmo_results.hdf5")
    return battmo_results_path


@st.cache_data
def get_path_to_indicator_values():
    output_files_path = get_path_to_output_files_dir()
    indicator_values_path = os.path.join(output_files_path, "indicator_quantities.json")
    return indicator_values_path


@st.cache_data
def get_path_to_calculated_values():
    output_files_path = get_path_to_output_files_dir()
    calculated_values_path = os.path.join(output_files_path, "gui_calculated_quantities.json")
    return calculated_values_path


@st.cache_data
def get_path_to_database_dir():
    streamlit_path = get_path_to_streamlit_dir()
    database_path = os.path.join(streamlit_path, "database")
    return database_path


@st.cache_data
def get_path_to_database():
    database_path = get_path_to_database_dir()
    database = os.path.join(database_path, db_name)
    return database


@st.cache_data
def get_path_to_database_create_update_dir():
    database_path = get_path_to_database_dir()
    create_update_path = os.path.join(database_path, "create_update")
    return create_update_path


@st.cache_data
def get_path_to_database_recources_dir():
    database_path = get_path_to_database_dir()
    recources_path = os.path.join(database_path, "recources")
    return recources_path


@st.cache_data
def get_path_to_database_recources_parameter_sets_dir():
    recources_path = get_path_to_database_recources_dir()
    parameter_sets_path = os.path.join(recources_path, "parameter_sets")
    return parameter_sets_path


@st.cache_data
def get_path_to_database_recources_parameter_sets_experimental_data_dir():
    parameter_sets_path = get_path_to_database_recources_parameter_sets_dir()
    experimental_data_path = os.path.join(parameter_sets_path, "data_sets")
    return experimental_data_path


@st.cache_data
def get_path_to_database_recources_parameter_sets_meta_data_dir():
    parameter_sets_path = get_path_to_database_recources_parameter_sets_dir()
    meta_data_path = os.path.join(parameter_sets_path, "meta_data")
    return meta_data_path


@st.cache_data
def get_path_to_images_dir():
    streamlit_path = get_path_to_streamlit_dir()
    images_path = os.path.join(streamlit_path, "images")
    return images_path


@st.cache_data
def get_path_to_categories():
    recources_path = get_path_to_database_recources_dir()
    categories_path = os.path.join(recources_path, "categories.json")
    return categories_path


@st.cache_data
def get_path_to_components():
    recources_path = get_path_to_database_recources_dir()
    components_path = os.path.join(recources_path, "components.json")
    return components_path


@st.cache_data
def get_path_to_materials():
    recources_path = get_path_to_database_recources_dir()
    materials_path = os.path.join(recources_path, "materials.json")
    return materials_path


@st.cache_data
def get_path_to_tabs():
    recources_path = get_path_to_database_recources_dir()
    tabs_path = os.path.join(recources_path, "tabs.json")
    return tabs_path


@st.cache_data
def get_path_to_models():
    recources_path = get_path_to_database_recources_dir()
    models_path = os.path.join(recources_path, "models.json")
    return models_path


@st.cache_data
def get_all_parameter_sets_experimental_data_files_path():
    all_files = []
    for root, _, files in os.walk(
        get_path_to_database_recources_parameter_sets_experimental_data_dir()
    ):
        for name in files:
            all_files.append(os.path.join(root, name))
    return all_files


@st.cache_data
def get_all_parameter_sets_meta_data_files_path():
    all_files = []
    for root, _, files in os.walk(get_path_to_database_recources_parameter_sets_meta_data_dir()):
        for name in files:
            all_files.append(os.path.join(root, name))
    return all_files


#################
## CONNECTIONS ##
#################


@st.cache_resource
def get_sqlite_con_and_cur():
    database = get_path_to_database()
    con = sqlite3.connect(database, check_same_thread=False)
    return con, con.cursor()


@st.cache_data
def get_json_from_path(path):
    with open(path) as file_content:
        return json.load(file_content)
