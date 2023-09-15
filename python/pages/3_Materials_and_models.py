import streamlit as st
import numpy as np
import os
import sys
from streamlit_toggle_component.src.st_toggle_component import st_toggle_component

##############################
# Remember user changed values
for k, v in st.session_state.items():
    st.session_state[k] = v
##############################

# set config is done before import to avoid streamlit error
path_to_python_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, path_to_python_dir)

from resources.db import db_access

label = ["A","B","C"]
values = st_toggle_component(label, initial_values=[False,False,False])
st.write(values)





# # Create a dictionary to store toggle states
# if 'toggle_states' not in st.session_state:
#     st.session_state.toggle_states = [
#         False,
#         False,
#                     False
#     ]

# toggle_states = [False, False, False]

# if 'toggle_names' not in st.session_state:
#     st.session_state.toggle_names = [
#         "A",
#         "B",
#                     "C"
#     ]

# st.title("Toggle System")

# # Create empty placeholders for the checkboxes
# checkbox_placeholders = {name: st.empty() for name in st.session_state.toggle_names}


# for name_id, name in enumerate(st.session_state.toggle_names):
#     state = checkbox_placeholders[name].toggle(label =st.session_state.toggle_names[name_id], 
#                                     value =True,
#                                     key = "toggle_{}".format(np.random.rand(100)),
#                                     label_visibility = "collapsed"
#                                     )
    
#     st.write(state)
#     toggle_states[name_id] = state

# # for name_id, name in enumerate(st.session_state.toggle_names):
# #     state = checkbox_placeholders[name].checkbox(label =st.session_state.toggle_names[name_id], 
# #                                     value =state,
# #                                     key = "toggle_{}".format(np.random.rand(100)),
# #                                     label_visibility = "collapsed"
# #                                     )
# #     st.write(state)

# # Count the number of active toggles
# active_count = sum(toggle_states)

# st.write(f"Active Count 1: {active_count}")

# # If more than 2 toggles are active, deactivate the extra onesss
# if active_count > 2:
#     for name_id in st.session_state.toggle_states:
#         if toggle_states[name_id] and active_count > 2:
#             toggle_states[name_id] = False
#             active_count -= 1

# for name_id in np.arange(len(st.session_state.toggle_names)):
#     st.write(f"{st.session_state.toggle_names[name_id]}: {toggle_states[name_id]}")
# #     checkbox_placeholders[name].toggle(name, 
# #                                        value=state,
# #                                        key = "toggle_{}".format(np.random.rand(100)),
# #                                        label_visibility = "collapsed"
# #                                        )

# # Display the count of active toggles
# st.write(f"Active Count: {active_count}")





# toggle_names = ["Toggle A", "Toggle B", "Toggle C"]

# st.title("Toggle System")

# # Create a multiselect widget to choose up to two active toggles
# selected_toggles = st.multiselect("Select up to two toggles to activate", toggle_names, default=["Toggle A", "Toggle B"])

# # Initialize the toggle states
# toggle_states = {name: False for name in toggle_names}

# # Activate the selected toggles
# for selected_toggle in selected_toggles:
#     toggle_states[selected_toggle] = True

# # Display the toggle states
# for name, state in toggle_states.items():
#     st.write(f"{name}: {state}")






# st.write("Streamlit Custom Component")

# checkbox_a = st.checkbox("Toggle A", key="toggle_a")
# checkbox_b = st.checkbox("Toggle B", key="toggle_b")
# checkbox_c = st.checkbox("Toggle C", key="toggle_c")

# # Load the JavaScript code from an external file or include it inline
# with open(os.path.join(path_to_python_dir,"custom_checkbox.js"), "r") as js_file:
#     js_code = js_file.read()

# st.components.v1.components.html(
#     f'<script>{js_code}</script>',
#     height=0,
#     width=0,
# )