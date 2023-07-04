from app_view import *


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

    def save_parameters(self, gui_parameters):
        return SaveParameters(gui_parameters)

    def run_simulation(self):
        return RunSimulation()

    def match_json(self, gui_dict):
        return match_json.get_batt_mo_dict_from_gui_dict(gui_dict)


#####################################
# Main setting functions
#####################################
@st.cache_data
def get_app_controller():
    return AppController(get_image_dict(), get_context())


@st.cache_data
def set_heading():
    return SetHeading(get_logo())


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
