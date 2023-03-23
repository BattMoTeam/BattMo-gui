from app_controller import *


def run_app():
    set_page_config()
    app = get_app_controller()

    set_heading()
    model_id = app.set_model_choice().selected_model
    gui_parameters = app.set_tabs(model_id).user_input
    battmo_parameters = app.match_json(gui_parameters)

    app.set_json_viewer(gui_parameters, "GUI output")
    app.set_json_viewer(battmo_parameters, "BattMo input")
    app.submit(gui_parameters, battmo_parameters)


if __name__ == "__main__":
    run_app()
