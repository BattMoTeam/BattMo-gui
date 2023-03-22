from app_view import *
from resources.db.db_helper import DBHelper


class AppController:
    def __init__(self, images, db_helper):
        self.path_to_python_dir = os.path.dirname(os.path.abspath(__file__))

        self.images = images
        self.db = db_helper

    def set_model_choice(self):
        return SetModelChoice(self.db, self.images)

    def set_tabs(self, model_id):
        return SetTabs(self.db, self.images, model_id)

    def set_json_viewer(self, json_data):
        return JsonViewer(json_data)

    def submit(self, user_parameters):
        return SubmitJob(user_parameters)


#####################################
# Main setting functions
#####################################
@st.cache_data
def get_app_controller():
    return AppController(get_image_dict(), get_db_helper())


@st.cache_data
def set_heading():
    return SetHeading(get_logo())


#####################################
# Page config
#####################################
def set_page_config():
    st.set_page_config(
        page_title="BattMo",
        page_icon=Image.open(os.path.join(get_path_to_images(), "battmo_logo.png"))
    )


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
# db helper
#####################################
@st.cache_data
def get_db_helper():
    return DBHelper()
