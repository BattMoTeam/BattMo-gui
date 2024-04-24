#############################
# Some background calculations done within the GUI
#############################

import numpy as np
import os
import sys
import streamlit as st
import json

##############################
# Set page directory to base level to allow for module import from different folder
path_to_streamlit_module = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, path_to_streamlit_module)
##############################
from app_scripts import app_access

@st.cache_data
def validate_mass_fraction(mf_sum,category_display_name,_tab):
    mf_summing = 0
    for id, value in mf_sum.items():
        mf_summing += value
    if mf_summing != 1.0:
        _tab.warning("The sum of the '%s' material mass fractions is not equal to 1." % (category_display_name))


@st.cache_data
def calc_density_mix(mf, density):
        
    density_mix=0
    for id, fraction in mf.items():
        
        density_mix += fraction*density.get(id)
    
    return density_mix

@st.cache_data
def calc_density_eff(density_mix,porosity):
    
    density_eff = density_mix * (1-porosity)
    
    return density_eff

@st.cache_data
def calc_mass_loading(density_eff, thickness, porosity):
        
    ml = thickness*10**(-6)*density_eff*100*(1-porosity)
    
    return ml

@st.cache_data
def calc_thickness( density_mix, mass_loading, porosity):
    th = mass_loading*10**(7)/(density_mix*1000(1-porosity))
    return th

@st.cache_data
def calc_porosity( density_mix, thickness, mass_loading):
    por = 1-(mass_loading/(thickness*10**(-6)*density_mix*100))
    return por

@st.cache_data
def calc_specific_capacity_active_material(c_max, density, li_stoich_max, li_stoich_min, n):
    F = 26.801
    Q_sp = c_max*(abs(li_stoich_max - li_stoich_min))*n*F/(density)
    return Q_sp

@st.cache_data
def calc_capacity_electrode(specific_capacity_am, mass_fraction, density_eff, volume, porosity):
    Q_sp = specific_capacity_am
    Q_elde = mass_fraction*Q_sp*(volume * density_eff*1000)
    return Q_elde

@st.cache_data
def calc_n_to_p_ratio(electrode_capacities):
    electrode_capacities_n = electrode_capacities["negative_electrode"]
    electrode_capacities_p = electrode_capacities["positive_electrode"]

    n_to_p = round(electrode_capacities_n/electrode_capacities_p,2)

    return n_to_p

@st.cache_data
def calc_cell_mass(densities, porosities, volumes, CC_mass, packing_mass):
    
    vf_sep = 1-porosities["separator"]
    vf_el_ne = 1-porosities["negative_electrode"]
    vf_el_pe = 1-porosities["positive_electrode"]
    vf_elyte_el_ne = porosities["negative_electrode"]
    vf_elyte_el_pe = porosities["positive_electrode"]
    vf_elyte_sep = porosities["separator"]

    # Electrodes
    mass_ne= densities["negative_electrode"]*volumes["negative_electrode"]*vf_el_ne
    mass_pe = densities["positive_electrode"]*volumes["positive_electrode"]*vf_el_pe

    # Separator
    mass_sep = densities["separator"]*volumes["separator"]*vf_sep

    # Electrolyte
    mass_elyte_ne = densities["electrolyte"]*volumes["negative_electrode"]*vf_elyte_el_ne
    mass_elyte_pe = densities["electrolyte"]*volumes["positive_electrode"]*vf_elyte_el_pe
    mass_elyte_sep = densities["electrolyte"]*volumes["separator"]*vf_elyte_sep
    
    mass = mass_ne +mass_pe +mass_sep +mass_elyte_ne +mass_elyte_pe +mass_elyte_sep+mass_elyte_sep + CC_mass 
    mass = mass*1000 + packing_mass
    return mass, mass_ne, mass_pe

@st.cache_data
def calc_cell_capacity(capacities_electrodes):

    min_key = min(capacities_electrodes, key=lambda k: capacities_electrodes[k])
    Qcell = capacities_electrodes[min_key]

    return Qcell

