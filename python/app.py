from app_controller import *


def run_app():
    set_page_config()
    app = get_app_controller()

    set_heading()
    model_id = app.set_model_choice().selected_model
    user_input = app.set_tabs(model_id).user_input

    app.set_json_viewer(user_input)
    app.submit(user_input)


if __name__ == "__main__":
    run_app()
