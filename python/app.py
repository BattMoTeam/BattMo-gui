import streamlit as st
from app_controller import AppController
from resources.db.db_helper import DBHelper


def get_app_controller():
    return AppController()


def get_db_helper():
    return DBHelper()


def run_app():
    app = get_app_controller()

    app.set_heading()
    model_id = app.set_model_choice().selected_model
    user_input = app.set_tabs(model_id).user_input

    app.set_json_viewer(user_input)
    app.submit(user_input)


if __name__ == "__main__":
    run_app()
