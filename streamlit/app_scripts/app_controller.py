
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
    
    def divergence_check(self):
        return view.DivergenceCheck()

    def download_parameters(self,gui_parameters):
        return view.DownloadParameters(gui_parameters)

    def json_LD_to_BattMo(self, gui_dict):
        return view.json_LD_to_BattMo.get_batt_mo_dict_from_gui_dict(gui_dict)
    
    def set_indicators(self):
        return view.SetIndicators()
    
    def set_download_hdf5_button(self, results):
        return view.SetHDF5Download(results)
    
    def set_graphs(self, results):
        return view.SetGraphs(results)


#####################################
# Main setting functions
#####################################
@st.cache_data
def get_app_controller():
    return AppController(get_image_dict(), get_context())


@st.cache_data
def set_heading():
    return view.SetHeading(get_logo())


def set_page_navigation():
    return view.SetPageNavigation()

@st.cache_data
def set_external_links():
    return view.SetExternalLinks()

@st.cache_data
def set_model_description():
    return view.SetModelDescription()

def set_material_description():
    return view.SetMaterialDescription()

def get_results_data():
    return view.GetResultsData()


#####################################
# Images
#####################################

@st.cache_data
def get_images():
    return view.LoadImages(app_access.get_path_to_images_dir())


@st.cache_data
def get_image_dict():
    return get_images().image_dict


@st.cache_data
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