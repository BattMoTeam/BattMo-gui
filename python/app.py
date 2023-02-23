import streamlit as st

from resources.db.db_helper import Helper
from app_view import AppController, InitializeHeading, InitializeTabs, JsonViewer, SubmitJob


@st.cache_data
def get_app_controller():
    return AppController()


@st.cache_data
def get_db_helper():
    return Helper()


def run_app():
    app_controller = get_app_controller()
    db_helper = get_db_helper()

    InitializeHeading(app_controller.logo)

    parameters = InitializeTabs(
        db_helper=db_helper,
        images=app_controller.image_dict
    )
    user_input = parameters.user_input

    JsonViewer(user_input)

    SubmitJob(user_parameters=user_input)


if __name__ == "__main__":
    run_app()
