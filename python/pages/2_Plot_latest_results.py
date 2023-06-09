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

# Retrieve latest results
with open(os.path.join(path_to_python_dir, "battmo_result"), "rb") as pickle_result:
    result = pickle.load(pickle_result)

# Convert it to numpy object
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

    return [
        xmin,
        xmax,
        cmin_elyte,
        cmax_elyte,
        cmin_ne,
        cmax_ne,
        cmin_pe,
        cmax_pe,
        phimax_elyte,
        phimin_elyte,
        phimax_ne,
        phimin_ne,
        phimax_pe,
        phimin_pe
    ]


@st.cache_data
def get_graph_limits_from_state(state):
    [
        xmin,
        xmax,
        init_cmin_elyte,
        init_cmax_elyte,
        init_cmin_ne,
        init_cmax_ne,
        init_cmin_pe,
        init_cmax_pe,
        init_phimax_elyte,
        init_phimin_elyte,
        init_phimax_ne,
        init_phimin_ne,
        init_phimax_pe,
        init_phimin_pe
    ] = get_graph_initial_limits()

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

    return [
        cmin_elyte,
        cmax_elyte,
        cmin_ne,
        cmax_ne,
        cmin_pe,
        cmax_pe,
        phimax_elyte,
        phimin_elyte,
        phimax_ne,
        phimin_ne,
        phimax_pe,
        phimin_pe
    ]


@st.cache_data
def get_min_difference():
    diff = []
    n = len(time_values)
    for i in range(1, n):
        diff.append(round(time_values[i][0] - time_values[i - 1][0], 5))
    return float(min(diff))


def create_subplot(x_data, y_data, title, x_label, x_min=None, x_max=None, y_min=None, y_max=None, vertical_line=None):
    fig, ax = plt.subplots()
    ax.plot(x_data, y_data)
    ax.set_title(title)
    ax.set_xlabel(x_label)

    if x_max:
        ax.set_xlim(x_min, x_max)
    if y_max:
        ax.set_ylim(y_min, y_max)

    if vertical_line:
        ax.axvline(x=vertical_line, color='k', linestyle="dashed")

    return fig


def create_colormap(x_data, y_data, z_data, title, x_label, y_label, cbar_label):

    x_color, y_color = np.meshgrid(x_data, y_data)
    fig, ax = plt.subplots()

    # Precision is set to 100 (change to 10 for lower precision, to 1000 for higher precision)
    # The lower the precision, the faster it runs
    color_map = ax.contourf(x_color, y_color, z_data, 100)
    cbar = fig.colorbar(color_map)
    cbar.ax.set_ylabel(cbar_label)

    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    return fig


def get_ne_c_color():
    return create_colormap(
        x_data=negative_electrode_grid.cells.centroids,
        y_data=time_values,
        z_data=negative_electrode_concentration,
        title="Negative Electrode - Concentration",
        x_label="Position  /  m",
        y_label="Time  /  h",
        cbar_label="Concentration  /  mol . L-1"
    )


def get_ne_p_color():
    return create_colormap(
        x_data=negative_electrode_grid.cells.centroids,
        y_data=time_values,
        z_data=negative_electrode_potential,
        title="Negative Electrode - Potential",
        x_label="Position  /  m",
        y_label="Time  /  h",
        cbar_label="Potential  /  V"
    )


def get_pe_c_color():
    return create_colormap(
        x_data=positive_electrode_grid.cells.centroids,
        y_data=time_values,
        z_data=positive_electrode_concentration,
        title="Positive Electrode - Concentration",
        x_label="Position  /  m",
        y_label="Time  /  h",
        cbar_label="Concentration  /  mol . L-1"
    )


def get_pe_p_color():
    return create_colormap(
        x_data=positive_electrode_grid.cells.centroids,
        y_data=time_values,
        z_data=positive_electrode_potential,
        title="Positive Electrode - Potential",
        x_label="Position  /  m",
        y_label="Time  /  h",
        cbar_label="Potential  /  V"
    )


def get_elyte_c_color():
    return create_colormap(
        x_data=electrolyte_grid.cells.centroids,
        y_data=time_values,
        z_data=electrolyte_concentration,
        title="Electrolyte - Concentration",
        x_label="Position  /  m",
        y_label="Time  /  h",
        cbar_label="Concentration  /  mol . L-1"
    )


def get_elyte_p_color():
    return create_colormap(
        x_data=electrolyte_grid.cells.centroids,
        y_data=time_values,
        z_data=electrolyte_potential,
        title="Electrolyte - Potential",
        x_label="Position  /  m",
        y_label="Time  /  h",
        cbar_label="Potential  /  V"
    )


def set_dynamic_dashboard():
    selected_time = st.slider(
        label="Select a time (hours)",
        min_value=0.0,
        max_value=time_values[number_of_states-1][0],
        step=get_min_difference()
    )
    state = 0
    while time_values[state][0] < selected_time:
        state += 1

    initial_graph_limits = get_graph_initial_limits()
    xmin = initial_graph_limits[0]
    xmax = initial_graph_limits[1]
    [
        cmin_elyte,
        cmax_elyte,
        cmin_ne,
        cmax_ne,
        cmin_pe,
        cmax_pe,
        phimax_elyte,
        phimin_elyte,
        phimax_ne,
        phimin_ne,
        phimax_pe,
        phimin_pe
    ] = get_graph_limits_from_state(state)

    # Negative Electrode Concentration
    ne_concentration = create_subplot(
        x_data=negative_electrode_grid.cells.centroids,
        y_data=negative_electrode_concentration[state],
        title="Negative Electrode Concentration  /  mol . L-1",
        x_label="Position  /  m",
        x_min=xmin,
        x_max=xmax,
        y_min=cmin_ne,
        y_max=cmax_ne
    )

    # Electrolyte Concentration
    elyte_concentration = create_subplot(
        x_data=electrolyte_grid.cells.centroids,
        y_data=electrolyte_concentration[state],
        title="Electrolyte Concentration  /  mol . L-1",
        x_label="Position  /  m",
        x_min=xmin,
        x_max=xmax,
        y_min=cmin_elyte,
        y_max=cmax_elyte
    )

    # Positive Electrode Concentration
    pe_concentration = create_subplot(
        x_data=positive_electrode_grid.cells.centroids,
        y_data=positive_electrode_concentration[state],
        title="Positive Electrode Concentration  /  mol . L-1",
        x_label="Position  /  m",
        x_min=xmin,
        x_max=xmax,
        y_min=cmin_pe,
        y_max=cmax_pe
    )

    # Cell Current
    cell_current_fig = create_subplot(
        x_data=time_values,
        y_data=cell_current,
        title="Cell Current  /  A",
        x_label="Time  /  h",
        vertical_line=time_values[state]
    )

    # Negative Electrode Potential
    ne_potential = create_subplot(
        x_data=negative_electrode_grid.cells.centroids,
        y_data=negative_electrode_potential[state],
        title="Negative Electrode Potential  /  V",
        x_label="Position  /  m",
        x_min=xmin,
        x_max=xmax,
        y_min=phimin_ne,
        y_max=phimax_ne
    )

    # Electrolyte Potential
    elyte_potential = create_subplot(
        x_data=electrolyte_grid.cells.centroids,
        y_data=electrolyte_potential[state],
        title="Electrolyte Potential  /  V",
        x_label="Position  /  m",
        x_min=xmin,
        x_max=xmax,
        y_min=phimin_elyte,
        y_max=phimax_elyte
    )

    # Positive Electrode Potential
    pe_potential = create_subplot(
        x_data=positive_electrode_grid.cells.centroids,
        y_data=positive_electrode_potential[state],
        title="Positive Electrode Potential  /  V",
        x_label="Position  /  m",
        x_min=xmin,
        x_max=xmax,
        y_min=phimin_pe,
        y_max=phimax_pe
    )

    # Cell Voltage
    cell_voltage_fig = create_subplot(
        x_data=time_values,
        y_data=cell_voltage,
        title="Cell Voltage  /  V",
        x_label="Time  /  h",
        vertical_line=time_values[state]
    )

    ######################
    # Set streamlit plot
    ######################

    ne, elyte, pe, cell = st.columns(4)

    ne.pyplot(ne_concentration)
    ne.pyplot(ne_potential)

    elyte.pyplot(elyte_concentration)
    elyte.pyplot(elyte_potential)

    pe.pyplot(pe_concentration)
    pe.pyplot(pe_potential)

    cell.pyplot(cell_current_fig)
    cell.pyplot(cell_voltage_fig)


def set_colormaps():
    # Colormaps
    ne_color, elyte_color, pe_color = st.columns(3)

    ne_color.pyplot(get_ne_c_color())
    ne_color.pyplot(get_ne_p_color())

    elyte_color.pyplot(get_elyte_c_color())
    elyte_color.pyplot(get_elyte_p_color())

    pe_color.pyplot(get_pe_c_color())
    pe_color.pyplot(get_pe_p_color())


def run_page():
    display_dynamic_dashboard = st.checkbox(
        label="Dynamic dashboard",
        value=True
    )
    display_colormaps = st.checkbox(
        label="Colormaps",
        value=False
    )

    if display_dynamic_dashboard:
        set_dynamic_dashboard()

    if display_colormaps:
        set_colormaps()


if __name__ == "__main__":
    run_page()
