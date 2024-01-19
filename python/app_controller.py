from app_view import *
from app_development import *


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
        return SetModelChoice()

    def set_tabs(self, model_id):
        return SetTabs(self.images, model_id, self.context)

    def set_json_viewer(self, json_data, label=None):
        if label:
            return JsonViewer(json_data, label)
        return JsonViewer(json_data)

    def run_simulation(self, gui_parameters):
        return RunSimulation(gui_parameters)
    
    def divergence_check(self):
        return DivergenceCheck()

    def download_parameters(self):
        return DownloadParameters()

    def match_json(self, gui_dict):
        return match_json.get_batt_mo_dict_from_gui_dict(gui_dict)
    
    def set_download_hdf5_button(self, results):
        return SetHDF5Download(results)
    
    def set_graphs(self, results):
        return SetGraphs(results)


#####################################
# Main setting functions
#####################################
@st.cache_data
def get_app_controller():
    return AppController(get_image_dict(), get_context())


@st.cache_data
def set_heading():
    return SetHeading(get_logo())


def set_page_navigation():
    return SetPageNavigation()

@st.cache_data
def set_external_links():
    return SetExternalLinks()

@st.cache_data
def set_model_description():
    return SetModelDescription()

def set_material_description():
    return SetMaterialDescription()

def get_results_data():
    return GetResultsData()


#####################################
# Images
#####################################
def get_path_to_images():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'images')


@st.cache_data
def get_images():
    return LoadImages(get_path_to_images())


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
    return db_access.get_json_from_path(db_access.get_path_to_categories()).get("context")


#####################################
# development utilities
#####################################
def log_memory_usage():
    return LogMemoryUsage()