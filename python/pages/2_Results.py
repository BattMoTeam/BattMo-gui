import os
import pickle
import io
import h5py
import numpy as np
from PIL import Image
import streamlit as st
import matplotlib.pyplot as plt
import time
from queue import Queue
import juliacall as jl


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
# Remember user changed values
for k, v in st.session_state.items():
    st.session_state[k] = v

#Remember widget actions when switching between pages (for example: selectbox choice)
st.session_state.update(st.session_state)
##############################


# Retrieve latest results
with open(os.path.join(path_to_python_dir, "battmo_result"), "rb") as pickle_result:
    result = pickle.load(pickle_result)

[
    log_messages,
    number_of_states,
    cell_voltage,
    cell_current,
    time_values,
    negative_electrode_grid,
    electrolyte_grid,
    positive_electrode_grid,
    negative_electrode_concentration_jl,
    electrolyte_concentration_jl,
    positive_electrode_concentration_jl,
    negative_electrode_potential_jl,
    electrolyte_potential_jl,
    positive_electrode_potential_jl

] = result #np_result


# number_of_states = int(number_of_states)
length_1d_ne = len(negative_electrode_concentration_jl)
length_2d_ne = len(negative_electrode_concentration_jl[0])
length_1d_pe = len(positive_electrode_concentration_jl)
length_2d_pe = len(positive_electrode_concentration_jl[0])
length_1d_el = len(electrolyte_concentration_jl)
length_2d_el = len(electrolyte_concentration_jl[0])
negative_electrode_concentration = np.zeros((length_1d_ne,length_2d_ne))
#negative_electrode_grid = np.zeros(length_2d_ne)
positive_electrode_concentration = np.zeros((length_1d_pe,length_2d_pe))
#positive_electrode_grid = np.zeros(length_2d_ne)
negative_electrode_potential = np.zeros((length_1d_ne,length_2d_ne))
positive_electrode_potential = np.zeros((length_1d_pe,length_2d_pe))
electrolyte_concentration = np.zeros((length_1d_el,length_2d_el))
#electrolyte_grid = np.zeros(length_2d_ne)
electrolyte_potential = np.zeros((length_1d_el,length_2d_el))

for i in range(length_1d_pe):
    for j in range(length_2d_pe):
        pe_c_sub = positive_electrode_concentration_jl[i]
        pe_p_sub = positive_electrode_potential_jl[i]
        #pe_grid = negative_electrode_grid_jl[0][i]
        positive_electrode_concentration[i,j] = pe_c_sub[j]
        positive_electrode_potential[i,j] = pe_p_sub[j]
        #positive_electrode_grid[i] = pe_grid


for i in range(length_1d_el):
    for j in range(length_2d_el):
        el_c_sub = electrolyte_concentration_jl[i]
        el_p_sub = electrolyte_potential_jl[i]
        #el_grid = negative_electrode_grid_jl[0][i]
        electrolyte_concentration[i,j] = el_c_sub[j]
        electrolyte_potential[i,j] = el_p_sub[j]
        #electrolyte_grid[i] = el_grid


for i in range(length_1d_ne):
    for j in range(length_2d_ne):
        ne_c_sub = negative_electrode_concentration_jl[i]
        ne_p_sub = negative_electrode_potential_jl[i]
        #ne_grid = negative_electrode_grid_jl[0][i]
        negative_electrode_concentration[i,j] = ne_c_sub[j]
        negative_electrode_potential[i,j] = ne_p_sub[j]
        #negative_electrode_grid[i] = ne_grid


@st.cache_data
def get_graph_initial_limits():
    xmin = min(np.squeeze(electrolyte_grid[1]))
    xmax = max(np.squeeze(electrolyte_grid[1]))

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

    cmax_elyte_sub = max(electrolyte_concentration[state])
    cmin_elyte_sub = min(electrolyte_concentration[state])

    cmax_ne_sub = max(negative_electrode_concentration[state])
    cmin_ne_sub = min(negative_electrode_concentration[state])

    cmax_pe_sub = max(positive_electrode_concentration[state])
    cmin_pe_sub = min(positive_electrode_concentration[state])

    phimax_elyte_sub = max(electrolyte_potential[state])
    phimin_elyte_sub =min(electrolyte_potential[state])

    phimax_ne_sub = max(negative_electrode_potential[state])
    phimin_ne_sub = min(negative_electrode_potential[state])

    phimax_pe_sub = max(positive_electrode_potential[state])
    phimin_pe_sub = min(positive_electrode_potential[state])

    cmax_elyte = max(init_cmax_elyte, cmax_elyte_sub)
    cmin_elyte = min(init_cmin_elyte, cmin_elyte_sub)

    cmax_ne = max(init_cmax_ne, cmax_ne_sub)
    cmin_ne = min(init_cmin_ne, cmin_ne_sub)

    cmax_pe = max(init_cmax_pe, cmax_pe_sub)
    cmin_pe = min(init_cmin_pe, cmin_pe_sub)

    phimax_elyte = max(init_phimax_elyte, phimax_elyte_sub)
    phimin_elyte = min(init_phimin_elyte, phimin_elyte_sub)

    phimax_ne = max(init_phimax_ne, phimax_ne_sub)
    phimin_ne = min(init_phimin_ne, phimin_ne_sub)

    phimax_pe = max(init_phimax_pe, phimax_pe_sub)
    phimin_pe = min(init_phimin_pe, phimin_pe_sub)



    return [
        cmax_elyte_sub,
        cmin_elyte_sub,
        cmax_ne_sub, 
        cmin_ne_sub, 
        cmax_pe_sub,
        cmin_pe_sub,
        phimax_elyte_sub, 
        phimin_elyte_sub,
        phimax_ne_sub,
        phimin_ne_sub,
        phimax_pe_sub,
        phimin_pe_sub,
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
        diff.append(round(time_values[i] - time_values[i - 1], 5))
    return float(min(diff))


def create_subplot(x_data, y_data, title, x_label, x_min=None, y_min_sub=None, y_max_sub=None,x_max=None, y_min=None, y_max=None, vertical_line=None):
    fig, ax = plt.subplots()


    ax.plot(x_data, y_data)

    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.get_yaxis().get_major_formatter().set_useOffset(False)

    if x_max:
        ax.set_xlim(x_min, x_max)
    if y_max and y_min != y_max:
        ax.set_ylim(y_min, y_max)
    if y_max and y_min_sub and abs(y_min_sub- y_max_sub) <= 0.001:
        delta = y_min_sub/10
        ax.set_ylim(y_min - delta, y_max + delta)

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
        x_data=negative_electrode_grid[0],
        y_data=time_values,
        z_data=negative_electrode_concentration,
        title="Negative Electrode - Concentration",
        x_label="Position  / \u00B5m",
        y_label="Time  /  h",
        cbar_label="Concentration  /  mol . L-1"
    )


@st.cache_data
def get_ne_p_color():
    return create_colormap(
        x_data=negative_electrode_grid[0],
        y_data=time_values,
        z_data=negative_electrode_potential,
        title="Negative Electrode - Potential",
        x_label="Position  /  \u00B5m",
        y_label="Time  /  h",
        cbar_label="Potential  /  V"
    )


@st.cache_data
def get_pe_c_color():
    return create_colormap(
        x_data=positive_electrode_grid[0],
        y_data=time_values,
        z_data=np.array(positive_electrode_concentration),
        title="Positive Electrode - Concentration",
        x_label="Position  /  \u00B5m",
        y_label="Time  /  h",
        cbar_label="Concentration  /  mol . L-1"
    )


@st.cache_data
def get_pe_p_color():
    return create_colormap(
        x_data=positive_electrode_grid[0],
        y_data=time_values,
        z_data=positive_electrode_potential,
        title="Positive Electrode - Potential",
        x_label="Position  /  \u00B5m",
        y_label="Time  /  h",
        cbar_label="Potential  /  V"
    )


@st.cache_data
def get_elyte_c_color():
    return create_colormap(
        x_data=electrolyte_grid[0],
        y_data=time_values,
        z_data=electrolyte_concentration,
        title="Electrolyte - Concentration",
        x_label="Position  /  \u00B5m",
        y_label="Time  /  h",
        cbar_label="Concentration  /  mol . L-1"
    )


@st.cache_data
def get_elyte_p_color():
    return create_colormap(
        x_data=electrolyte_grid[0],
        y_data=time_values,
        z_data=electrolyte_potential,
        title="Electrolyte - Potential",
        x_label="Position  /  \u00B5m",
        y_label="Time  /  h",
        cbar_label="Potential  /  V"
    )

def view_plots_static(state):
    
    initial_graph_limits = get_graph_initial_limits()
    xmin = initial_graph_limits[0]
    xmax = initial_graph_limits[1]
    [
        cmax_elyte_sub,
        cmin_elyte_sub,
        cmax_ne_sub, 
        cmin_ne_sub, 
        cmax_pe_sub,
        cmin_pe_sub,
        phimax_elyte_sub, 
        phimin_elyte_sub,
        phimax_ne_sub,
        phimin_ne_sub,
        phimax_pe_sub,
        phimin_pe_sub,
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
        x_data=np.squeeze(negative_electrode_grid[0]),
        y_data=np.squeeze(negative_electrode_concentration)[state],
        title="Negative Electrode Concentration  /  mol . L-1",
        x_label="Position  /  \u00B5m",
        x_min=xmin,
        x_max=xmax,
        y_min=cmin_ne,
        y_max=cmax_ne,
        y_min_sub = cmin_ne_sub,
        y_max_sub = cmax_ne_sub
    )

    # Electrolyte Concentration
    elyte_concentration = create_subplot(
        x_data=np.squeeze(electrolyte_grid[0]),
        y_data=electrolyte_concentration[state],
        title="Electrolyte Concentration  /  mol . L-1",
        x_label="Position  /  \u00B5m",
        x_min=xmin,
        x_max=xmax,
        y_min=cmin_elyte,
        y_max=cmax_elyte,
        y_min_sub = cmin_elyte_sub,
        y_max_sub = cmax_elyte_sub
    )
    
    # Positive Electrode Concentration
    pe_concentration = create_subplot(
        x_data=np.squeeze(positive_electrode_grid[0]),
        y_data=np.squeeze(positive_electrode_concentration)[state],
        title="Positive Electrode Concentration  /  mol . L-1",
        x_label="Position  /  \u00B5m",
        x_min=xmin,
        x_max=xmax,
        y_min=cmin_pe,
        y_max=cmax_pe,
        y_min_sub = cmin_pe_sub,
        y_max_sub = cmax_pe_sub
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
        x_data=np.squeeze(negative_electrode_grid[0]),
        y_data=negative_electrode_potential[state],
        title="Negative Electrode Potential  /  V",
        x_label="Position  /  \u00B5m",
        x_min=xmin,
        x_max=xmax,
        y_min=phimin_ne,
        y_max=phimax_ne,
        y_min_sub = phimin_ne_sub,
        y_max_sub = phimax_ne_sub
    )

    # Electrolyte Potential
    elyte_potential = create_subplot(
        x_data=np.squeeze(electrolyte_grid[0]),
        y_data=electrolyte_potential[state],
        title="Electrolyte Potential  /  V",
        x_label="Position  /  \u00B5m",
        x_min=xmin,
        x_max=xmax,
        y_min=phimin_elyte,
        y_max=phimax_elyte,
        y_min_sub = phimin_elyte_sub,
        y_max_sub = phimax_elyte_sub
    )

    # Positive Electrode Potential
    pe_potential = create_subplot(
        x_data=np.squeeze(positive_electrode_grid[0]),
        y_data=positive_electrode_potential[state],
        title="Positive Electrode Potential  /  V",
        x_label="Position  /  \u00B5m",
        x_min=xmin,
        x_max=xmax,
        y_min=phimin_pe,
        y_max=phimax_pe,
        y_min_sub = phimin_pe_sub,
        y_max_sub = phimax_pe_sub
        
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

    ne.pyplot(ne_concentration, clear_figure=True)
    ne.pyplot(ne_potential, clear_figure=True)

    elyte.pyplot(elyte_concentration, clear_figure=True)
    elyte.pyplot(elyte_potential, clear_figure=True)

    pe.pyplot(pe_concentration, clear_figure=True)
    pe.pyplot(pe_potential, clear_figure=True)

    cell.pyplot(cell_current_fig, clear_figure=True)
    cell.pyplot(cell_voltage_fig, clear_figure=True)


def view_plots_dynamic(state, q):
    
    [time_value,
    negative_electrode_concentration_time_step,
    electrolyte_concentration_time_step,
    positive_electrode_concentration_time_step,
    negative_electrode_potential_time_step,
    electrolyte_potential_time_step,
    positive_electrode_potential_time_step] = q.get()


    initial_graph_limits = get_graph_initial_limits()
    xmin = initial_graph_limits[0]
    xmax = initial_graph_limits[1]
    [
        cmax_elyte_sub,
        cmin_elyte_sub,
        cmax_ne_sub, 
        cmin_ne_sub, 
        cmax_pe_sub,
        cmin_pe_sub,
        phimax_elyte_sub, 
        phimin_elyte_sub,
        phimax_ne_sub,
        phimin_ne_sub,
        phimax_pe_sub,
        phimin_pe_sub,
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



def run_dynamic_dashboard():
    #q = Queue()

    time_step = 0
    init_time_value = 0.0
    max_time_value = max(time_values)
    step_size = get_min_difference()
    time_array = np.arange(init_time_value,max_time_value,step_size)

    cmax_elyte_sub_full = np.amax(electrolyte_concentration)
    cmin_elyte_sub_full = np.amin(electrolyte_concentration)

    cmax_ne_sub_full =np.amax(negative_electrode_concentration)
    cmin_ne_sub_full = np.amin(negative_electrode_concentration)

    cmax_pe_sub_full = np.amax(positive_electrode_concentration)
    cmin_pe_sub_full = np.amin(positive_electrode_concentration)

    phimax_elyte_sub_full = np.amax(electrolyte_potential)
    phimin_elyte_sub_full =np.amin(electrolyte_potential)

    phimax_ne_sub_full = np.amax(negative_electrode_potential)
    phimin_ne_sub_full = np.amin(negative_electrode_potential)

    phimax_pe_sub_full = np.amax(positive_electrode_potential)
    phimin_pe_sub_full = np.amin(positive_electrode_potential)


    # Negative Electrode Concentration
    ne_concentration, ax_ne_c = plt.subplots()
    line_ne_c, = ax_ne_c.plot([])
        #x_data=np.squeeze(negative_electrode_grid[0]),
        #y_data=negative_electrode_concentration_time_step,
        #title="Negative Electrode Concentration  /  mol . L-1",
        #x_label="Position  /  m",
    ax_ne_c.set_ylim(24,28)


    while time_step <= len(time_values)-1:

        #value = time_array[time_step]
        

        new_data = [ 

            # time_values[time_step],
            negative_electrode_concentration[time_step],
            # electrolyte_concentration[time_step],
            # positive_electrode_concentration[time_step],
            # negative_electrode_potential[time_step],
            # electrolyte_potential[time_step],
            # positive_electrode_potential[time_step]

        ]

        #q.put(new_data)

        line_ne_c.set_data(np.squeeze(negative_electrode_grid[0]),negative_electrode_concentration[time_step])


        time.sleep(0.5)

        #line_ne_c.set_data([],[])
        time_step += 1

        #plt.show

        ######################
        # Set streamlit plot
        ######################

        #ne, elyte, pe, cell = st.columns(4)

        st.pyplot(ne_concentration)
    


def set_dynamic_dashboard():
    init_time_value = 0.0
    max_time_value = max(time_values)
    step_size = get_min_difference()
    selected_time = st.slider(
        key = "DynamicDashboard",
        label="Select a time (hours)",
        min_value=init_time_value,
        max_value= max_time_value,
        step=step_size
        )


    state = 0
    while time_values[state] < selected_time:
        state += 1

    view_plots_static(state)




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
        grids.create_dataset("negative_electrode_grid", data=negative_electrode_grid[1])
        grids.create_dataset("positive_electrode_grid", data=positive_electrode_grid[1])
        grids.create_dataset("electrolyte_grid", data=electrolyte_grid[1])

        concentrations = f.create_group("concentrations")

        negative_electrode_concentrations = concentrations.create_group("negative_electrode")
        electrolyte_concentrations = concentrations.create_group("electrolyte")
        positive_electrode_concentrations = concentrations.create_group("positive_electrode")

        potentials = f.create_group("potentials")

        negative_electrode_potentials = potentials.create_group("negative_electrode")
        electrolyte_potentials = potentials.create_group("electrolyte")
        positive_electrode_potentials = potentials.create_group("positive_electrode")

        for i in range(number_of_states[0]):
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
        file_name="hdf5_results.hdf5",
        data=prepare_h5_file(),
        mime="application/x-hdf",
        help="Download your results."
    )


    

def run_page():

    set_download_button()
    dash, color = st.columns((2,5))

    display_dynamic_dashboard = dash.toggle(
        label="Dynamic dashboard",
        value=True
    )


    display_colormaps = color.toggle(
        label="Colormaps",
        value=False
    )

    st.divider()



    

    if display_dynamic_dashboard:
        set_dynamic_dashboard()

        # run_dashboard = st.button(
        #     label = "Run dynamic dashboard")
        
        # if run_dashboard:
        #     run_dynamic_dashboard()

    if display_colormaps:
        set_colormaps()

    st.divider()


if __name__ == "__main__":
    run_page()
