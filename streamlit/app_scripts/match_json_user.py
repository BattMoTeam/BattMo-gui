import streamlit as st

def get_gui_dict_from_user_dict(user_dict,model):
    
    if "Model" in user_dict:
        if user_dict["Model"] == model:
            ""

        else:
            st.error("Your file can not be processed. You specified the wrong simulation model.")

    else:
        st.error("Your file can not be processed. You haven't specified the simulation model.")