from app_controller import *
from resources.db.db_helper import DBHelper


@st.cache_data
def get_images():
    return LoadImages(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'images'))


@st.cache_data
def get_image_dict():
    return get_images().image_dict


@st.cache_data
def get_logo():
    return get_images().logo


@st.cache_data
def get_db_helper():
    return DBHelper()


@st.cache_data
def get_app_controller():
    return AppController(get_images(), get_db_helper())


@st.cache_data
def set_heading():
    return SetHeading(get_logo())


def run_app():
    app = get_app_controller()

    set_heading()
    model_id = app.set_model_choice().selected_model
    user_input = app.set_tabs(model_id).user_input

    app.set_json_viewer(user_input)
    app.submit(user_input)


if __name__ == "__main__":
    run_app()
