from app_view import *
from resources.db.db_helper import DBHelper


class AppController:
    def __init__(self):
        self.path_to_python_dir = os.path.dirname(os.path.abspath(__file__))

        self.images = LoadImages(self.get_path_to_images())
        self.db = DBHelper()

    def get_path_to_images(self):
        return os.path.join(self.path_to_python_dir, 'resources', 'images')

    def set_heading(self):
        return SetHeading(self.images.logo)

    def set_model_choice(self):
        return SetModelChoice(self.db, self.images.image_dict)

    def set_tabs(self, model_id):
        return SetTabs(self.db, self.images.image_dict, model_id)

    def set_json_viewer(self, json_data):
        return JsonViewer(json_data)

    def submit(self, user_parameters):
        return SubmitJob(user_parameters)
