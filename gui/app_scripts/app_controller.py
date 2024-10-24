import os
import streamlit as st
import sys


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app_view as view
import app_development as dev
import app_access


class AppController:
    """
    Centralize app features in a single class
    Use cache data when it's possible to optimize software's performance
    """

    def __init__(self, images, context):
        self.path_to_python_dir = os.path.dirname(os.path.abspath(__file__))

        self.images = images
        self.context = context

    def set_model_choice(self):
        return view.SetModelChoice()

    def set_tabs(self, model_id):
        return view.SetTabs(self.images, model_id, self.context)

    def set_json_viewer(self, json_data, label=None):
        if label:
            return view.JsonViewer(json_data, label)
        return view.JsonViewer(json_data)

    def run_simulation(self, gui_parameters):
        return view.RunSimulation(gui_parameters)

    def divergence_check(self, save_run, error):
        return view.DivergenceCheck(save_run, error)

    def download_parameters(self, gui_parameters):
        return view.DownloadParameters(gui_parameters)

    def json_LD_to_BattMo(self, gui_dict):
        return view.match_json_LD.get_batt_mo_dict_from_gui_dict(gui_dict)

    def set_indicators(self, page_name, results_simulation=None, file_names=None):
        return view.SetIndicators(page_name, results_simulation, file_names)

    def set_geometry_visualization(self, gui_parameters):
        return view.SetGeometryVisualization(gui_parameters)

    def set_download_hdf5_button(self, results, selected_data_sets):
        return view.SetHDF5Download(results, selected_data_sets)

    def set_graphs(self, results, selected_data_sets):
        return view.SetGraphs(results, selected_data_sets)

    def set_hdf5_upload(self):
        return view.SetHDF5Upload()

    def set_data_set_selector(self):
        return view.SetDataSetSelector()


#####################################
# Main setting functions
#####################################


def get_app_controller():
    return AppController(get_image_dict(), get_context())


def set_heading():
    return view.SetHeading(get_logo())


def set_page_navigation():
    return view.SetPageNavigation()


def set_external_links():
    return view.SetExternalLinks()


def set_model_description():
    return view.SetModelDescription()


def set_material_description():
    return view.SetMaterialDescription()


def get_results_data(file_names, response=None):
    return view.GetResultsData(file_names, response)


def set_acknowlegent_info():
    return view.SetAcknowledgementInfo()


#####################################
# JSON
#####################################


def setup_linked_data_structure():
    return view.SetupLinkedDataStruct()


#####################################
# Images
#####################################


@st.cache_data
def get_images():
    return view.LoadImages(app_access.get_path_to_images_dir())


def get_image_dict():
    return get_images().image_dict


def get_logo():
    return get_images().logo


#####################################
# context
#####################################
@st.cache_data
def get_context():
    return app_access.get_json_from_path(app_access.get_path_to_categories()).get("context")


#####################################
# development utilities
#####################################
def log_memory_usage():
    return dev.LogMemoryUsage()
