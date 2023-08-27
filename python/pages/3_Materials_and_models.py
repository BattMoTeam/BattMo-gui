import streamlit as st

##############################
# Remember user changed values
for k, v in st.session_state.items():
    st.session_state[k] = v
##############################