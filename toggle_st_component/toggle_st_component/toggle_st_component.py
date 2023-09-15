# my_streamlit_component/my_streamlit_component.py
import streamlit as st

def toggle_st_component():

    st.markdown(
        """
        <div>
            <h4>Select up to two toggles to activate</h4>
            <label>
                <input type="checkbox" id="toggle_a" /> Toggle A
            </label>
            <label>
                <input type="checkbox" id="toggle_b" /> Toggle B
            </label>
            <label>
                <input type="checkbox" id="toggle_c" /> Toggle C
            </label>
        </div>
        
        """
    )
    # Include the JavaScript code
    st.components.v1.html("""
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script src="custom_checkbox.js"></script>
    """)

