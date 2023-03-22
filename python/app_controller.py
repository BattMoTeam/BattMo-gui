from app_view import *


class AppController:
    def __init__(self, images, db_helper):
        self.path_to_python_dir = os.path.dirname(os.path.abspath(__file__))

        self.images = images
        self.db = db_helper

    def set_model_choice(self):
        return SetModelChoice(self.db, self.images.image_dict)

    def set_tabs(self, model_id):
        return SetTabs(self.db, self.images.image_dict, model_id)

    def set_json_viewer(self, json_data):
        return JsonViewer(json_data)

    def submit(self, user_parameters):
        return SubmitJob(user_parameters)
