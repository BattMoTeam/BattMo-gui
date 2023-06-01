import os
import pickle
import numpy as np
from PIL import Image
import streamlit as st
import matplotlib.pyplot as plt


##############################
# Page Config
path_to_python_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path_to_images = os.path.join(path_to_python_dir, 'resources', 'images')
st.set_page_config(
    page_title="BattMo",
    page_icon=Image.open(os.path.join(path_to_images, "battmo_logo.png")),
    layout="wide"
)
##############################

with open(os.path.join(path_to_python_dir, "battmo_result"), "rb") as pickle_result:
    result = pickle.load(pickle_result)

np_result = np.array(result)[0]

# cf runEncodedJsonStruct.m
[
    number_of_states,
    cell_voltage,
    cell_current,
    time_values,
    negative_electrode_grid,
    electrolyte_grid,
    positive_electrode_grid,
    negative_electrode_concentration,
    electrolyte_concentration,
    positive_electrode_concentration,
    negative_electrode_potential,
    electrolyte_potential,
    positive_electrode_potential

] = np_result

number_of_states = int(number_of_states)


@st.cache_data
def get_graph_initial_limits():
    xmin = min(electrolyte_grid.nodes.coords)
    xmax = max(electrolyte_grid.nodes.coords)

    cmax_elyte = max(electrolyte_concentration[0])
    cmin_elyte = min(electrolyte_concentration[0])

    cmax_ne = max(negative_electrode_concentration[0])
    cmin_ne = min(negative_electrode_concentration[0])

    cmax_pe = max(positive_electrode_concentration[0])
    cmin_pe = min(positive_electrode_concentration[0])

    phimax_elyte = max(electrolyte_potential[0])
    phimin_elyte = min(electrolyte_potential[0])

    phimax_ne = max(negative_electrode_potential[0])
    phimin_ne = min(negative_electrode_potential[0])

    phimax_pe = max(positive_electrode_potential[0])
    phimin_pe = min(positive_electrode_potential[0])

    return xmin, \
        xmax, \
        cmin_elyte, \
        cmax_elyte, \
        cmin_ne, \
        cmax_ne, \
        cmin_pe, \
        cmax_pe, \
        phimax_elyte, \
        phimin_elyte, \
        phimax_ne, \
        phimin_ne, \
        phimax_pe, \
        phimin_pe


@st.cache_data
def get_graph_limits_from_state(state):
    xmin, \
        xmax, \
        init_cmin_elyte, \
        init_cmax_elyte, \
        init_cmin_ne, \
        init_cmax_ne, \
        init_cmin_pe, \
        init_cmax_pe, \
        init_phimax_elyte, \
        init_phimin_elyte, \
        init_phimax_ne, \
        init_phimin_ne, \
        init_phimax_pe, \
        init_phimin_pe = get_graph_initial_limits()

    cmax_elyte = max(init_cmax_elyte, max(electrolyte_concentration[state]))
    cmin_elyte = min(init_cmin_elyte, min(electrolyte_concentration[state]))

    cmax_ne = max(init_cmax_ne, max(negative_electrode_concentration[state]))
    cmin_ne = min(init_cmin_ne, min(negative_electrode_concentration[state]))

    cmax_pe = max(init_cmax_pe, max(positive_electrode_concentration[state]))
    cmin_pe = min(init_cmin_pe, min(positive_electrode_concentration[state]))

    phimax_elyte = max(init_phimax_elyte, max(electrolyte_potential[state]))
    phimin_elyte = min(init_phimin_elyte, min(electrolyte_potential[state]))

    phimax_ne = max(init_phimax_ne, max(negative_electrode_potential[state]))
    phimin_ne = min(init_phimin_ne, min(negative_electrode_potential[state]))

    phimax_pe = max(init_phimax_pe, max(positive_electrode_potential[state]))
    phimin_pe = min(init_phimin_pe, min(positive_electrode_potential[state]))

    return cmin_elyte, \
        cmax_elyte, \
        cmin_ne, \
        cmax_ne, \
        cmin_pe, \
        cmax_pe,\
        phimax_elyte, \
        phimin_elyte, \
        phimax_ne, \
        phimin_ne, \
        phimax_pe, \
        phimin_pe


def run_page():

    state = st.slider(
        label="Select a step",
        min_value=0,
        max_value=number_of_states-1
    )

    ne, elyte, pe, cell = st.columns(4)

    xmin, xmax, _, _, _, _, _, _, _, _, _, _, _, _ = get_graph_initial_limits()
    cmin_elyte, \
        cmax_elyte, \
        cmin_ne, \
        cmax_ne, \
        cmin_pe, \
        cmax_pe, \
        phimax_elyte, \
        phimin_elyte, \
        phimax_ne, \
        phimin_ne, \
        phimax_pe, \
        phimin_pe = get_graph_limits_from_state(state)

    # Negative Electrode Concentration
    ne_c_fig, ne_c_ax = plt.subplots()
    ne_c_ax.plot(negative_electrode_grid.cells.centroids, negative_electrode_concentration[state])
    ne_c_ax.set_title("Negative Electrode Concentration  /  mol . L-1")
    ne_c_ax.set_xlabel("Position  /  m")
    ne_c_ax.set_xlim(xmin, xmax)
    ne_c_ax.set_ylim(cmin_ne, cmax_ne)

    # Electrolyte Concentration
    elyte_c_fig, elyte_c_ax = plt.subplots()
    elyte_c_ax.plot(electrolyte_grid.cells.centroids, electrolyte_concentration[state])
    elyte_c_ax.set_title("Electrolyte Concentration  /  mol . L-1")
    elyte_c_ax.set_xlabel("Position  /  m")
    elyte_c_ax.set_xlim(xmin, xmax)
    elyte_c_ax.set_ylim(cmin_elyte, cmax_elyte)

    # Positive Electrode Concentration
    pe_c_fig, pe_c_ax = plt.subplots()
    pe_c_ax.plot(positive_electrode_grid.cells.centroids, positive_electrode_concentration[state])
    pe_c_ax.set_title("Positive Electrode Concentration  /  mol . L-1")
    pe_c_ax.set_xlabel("Position  /  m")
    pe_c_ax.set_xlim(xmin, xmax)
    pe_c_ax.set_ylim(cmin_pe, cmax_pe)

    # Cell Current
    cell_current_fig, cell_current_ax = plt.subplots()
    cell_current_ax.plot(time_values, cell_current)
    cell_current_ax.set_title("Cell Current  /  A")
    cell_current_ax.set_xlabel("Time  /  h")
    cell_current_ax.axvline(x=time_values[state], color='k', linestyle="dashed")

    # Negative Electrode Potential
    ne_p_fig, ne_p_ax = plt.subplots()
    ne_p_ax.plot(negative_electrode_grid.cells.centroids, negative_electrode_potential[state])
    ne_p_ax.set_title("Negative Electrode Potential  /  V")
    ne_p_ax.set_xlabel("Position  /  m")
    ne_p_ax.set_xlim(xmin, xmax)
    ne_p_ax.set_ylim(phimin_ne, phimax_ne)

    # Electrolyte Potential
    elyte_p_fig, elyte_p_ax = plt.subplots()
    elyte_p_ax.plot(electrolyte_grid.cells.centroids, electrolyte_potential[state])
    elyte_p_ax.set_title("Electrolyte Potential  /  V")
    elyte_p_ax.set_xlabel("Position  /  m")
    elyte_p_ax.set_xlim(xmin, xmax)
    elyte_p_ax.set_ylim(phimin_elyte, phimax_elyte)

    # Positive Electrode Potential
    pe_p_fig, pe_p_ax = plt.subplots()
    pe_p_ax.plot(positive_electrode_grid.cells.centroids, positive_electrode_potential[state])
    pe_p_ax.set_title("Positive Electrode Potential  /  V")
    pe_p_ax.set_xlabel("Position  /  m")
    pe_p_ax.set_xlim(xmin, xmax)
    pe_p_ax.set_ylim(phimin_pe, phimax_pe)

    # Cell Voltage
    cell_vol_fig, cell_vol_ax = plt.subplots()
    cell_vol_ax.plot(time_values, cell_voltage)
    cell_vol_ax.set_title("Cell Voltage  /  V")
    cell_vol_ax.set_xlabel("Time  /  h")
    cell_vol_ax.axvline(x=time_values[state], color='k', linestyle="dashed")

    ######################
    # Set streamlit plot
    ######################
    ne.pyplot(ne_c_fig)
    ne.pyplot(ne_p_fig)

    elyte.pyplot(elyte_c_fig)
    elyte.pyplot(elyte_p_fig)

    pe.pyplot(pe_c_fig)
    pe.pyplot(pe_p_fig)

    cell.pyplot(cell_current_fig)
    cell.pyplot(cell_vol_fig)


if __name__ == "__main__":
    run_page()
