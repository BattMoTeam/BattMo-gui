import os
import pickle
import io
import h5py
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

##############################
# Remember user changed values
for k, v in st.session_state.items():
    st.session_state[k] = v
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


@st.cache_data
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


@st.cache_data
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


@st.cache_data
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


@st.cache_data
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


@st.cache_data
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


@st.cache_data
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


# Create hdf5 from numpy arrays, result cached to optimize software.
# Cache cleared after generating new results (cf RunSimulation)
@st.cache_data
def prepare_h5_file():
    bio = io.BytesIO()
    # cf https://stackoverflow.com/questions/73157377/how-to-download-various-data-from-streamlit-to-hdf5-file-with-st-download-butto

    with h5py.File(bio, "w") as f:
        f.attrs['number_of_states'] = number_of_states

        f.create_dataset("time_values", data=time_values)
        f.create_dataset("cell_voltage", data=cell_voltage)
        f.create_dataset("cell_current", data=cell_current)

        grids = f.create_group("grids")
        grids.create_dataset("negative_electrode_grid", data=negative_electrode_grid.cells.centroids)
        grids.create_dataset("positive_electrode_grid", data=positive_electrode_grid.cells.centroids)
        grids.create_dataset("electrolyte_grid", data=electrolyte_grid.cells.centroids)

        concentrations = f.create_group("concentrations")

        negative_electrode_concentrations = concentrations.create_group("negative_electrode")
        electrolyte_concentrations = concentrations.create_group("electrolyte")
        positive_electrode_concentrations = concentrations.create_group("positive_electrode")

        potentials = f.create_group("potentials")

        negative_electrode_potentials = potentials.create_group("negative_electrode")
        electrolyte_potentials = potentials.create_group("electrolyte")
        positive_electrode_potentials = potentials.create_group("positive_electrode")

        for i in range(number_of_states):
            negative_electrode_concentrations.create_dataset(
                "ne_c_state_{}".format(i),
                data=np.array(negative_electrode_concentration[i], dtype=float)
            )
            positive_electrode_concentrations.create_dataset(
                "pe_c_state_{}".format(i),
                data=np.array(positive_electrode_concentration[i], dtype=float)
            )
            electrolyte_concentrations.create_dataset(
                "elyte_c_state_{}".format(i),
                data=np.array(electrolyte_concentration[i], dtype=float)
            )

            negative_electrode_potentials.create_dataset(
                "ne_p_state_{}".format(i),
                data=np.array(negative_electrode_potential[i], dtype=float)
            )
            positive_electrode_potentials.create_dataset(
                "pe_p_state_{}".format(i),
                data=np.array(positive_electrode_potential[i], dtype=float)
            )
            electrolyte_potentials.create_dataset(
                "elyte_p_state_{}".format(i),
                data=np.array(electrolyte_potential[i], dtype=float)
            )

    return bio


def set_download_button():
    st.download_button(
        label="HDF5 Results",
        file_name="hdf5_results",
        data=prepare_h5_file(),
        mime="application/x-hdf"
    )


def run_page():
    display_dynamic_dashboard = st.checkbox(
        label="Dynamic dashboard",
        value=True
    )
    display_colormaps = st.checkbox(
        label="Colormaps",
        value=False
    )

    download_h5 = st.checkbox(
        label="Download results",
        value=False
    )

    if download_h5:
        set_download_button()

    if display_dynamic_dashboard:
        set_dynamic_dashboard()

    if display_colormaps:
        set_colormaps()


if __name__ == "__main__":
    run_page()
