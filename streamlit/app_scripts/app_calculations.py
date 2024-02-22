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
def validate_volume_fraction(vf_sum,category_display_name,_tab):
    vf_summing = 0
    for id, value in vf_sum.items():
        vf_summing += value
    if vf_summing != 1.0:
        _tab.warning("The sum of the '%s' material volume fractions is not equal to 1." % (category_display_name))

@st.cache_data
def calc_density_mix(vf, density):
        
    density_eff=0
    for id, fraction in vf.items():
        
        density_eff += fraction*density.get(id)
    
    return density_eff

@st.cache_data
def calc_mass_loading(density_eff, thickness, porosity):
        
    ml = thickness*10**(-6)*density_eff*100*(1-porosity)
    
    return ml

@st.cache_data
def calc_thickness( density_eff, mass_loading, porosity):
    th = mass_loading*10**(7)/(density_eff*1000*(1-porosity))
    return th

@st.cache_data
def calc_porosity( density_eff, thickness, mass_loading):
    por = 1-(mass_loading/(thickness*10**(-6)*density_eff*100))
    return por

@st.cache_data
def calc_specific_capacity_electrode(mass_fraction, c_max, density, li_stoich_max, li_stoich_min, n, porosity):
    F = 26.801
    Q_sp = c_max*(abs(li_stoich_max - li_stoich_min))*n*F/density
    Q_sp_eff = mass_fraction*Q_sp*(1-porosity)
    return Q_sp_eff

@st.cache_data
def calc_n_to_p_ratio(effective_specific_capacities):
    effective_specific_capacities_n = effective_specific_capacities["negative_electrode"]
    effective_specific_capacities_p = effective_specific_capacities["positive_electrode"]

    n_to_p = round(effective_specific_capacities_n/effective_specific_capacities_p,2)

    return n_to_p

@st.cache_data
def calc_cell_mass(mass_loadings):
    """
    Can be implemented for 3D models
    """
    
    return 

@st.cache_data
def calc_cell_energy(mass_loadings):
    """
    Can be implemented for 3D models
    """

    return 

