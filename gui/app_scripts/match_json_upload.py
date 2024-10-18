import streamlit as st
import os
import sys
import json

##############################
# Set page directory to base level to allow for module import from different folder
path_to_streamlit_module = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, path_to_streamlit_module)
##############################

from app_scripts import app_access
from database import db_helper






class Material(object):
    def __init__(self, mat, prop, ad_prop):
        self.mat = mat
        self.prop = prop
        self.ad_prop = ad_prop
        self.mat_id = db_helper.get_parameter_set_id_by_name
        self.mat_ud_id = db_helper.get_parameter_set_id_by_name

class NonMaterial(object):
    def __init__(self, prop, ad_prop):
        self.prop = prop
        self.ad_prop = ad_prop

class Electrode(object):
    def __init__(self, am, binder, add, prop, ad_prop):

        self.am = am
        self.binder = binder
        self.add = add
        self.prop = prop 
        self.ad_prop = ad_prop


class UploadDict(object):
    """
    Create a python object from the uploaded parameter dict for easier access and better readability
    """
    def __init__(self, uploaded_dict):

        self.raw_ne = uploaded_dict["NegativeElectrode"]
        self.raw_pe = uploaded_dict["PositiveElectrode"]
        self.ne = Electrode(
            am = self.raw_ne["ActiveMaterial"],
            binder = self.raw_ne["Binder"],
            add = self.raw_ne["Additive"],
            prop = self.raw_ne["Properties"],
            ad_prop = self.raw_ne["AdvancedProperties"]
        )
        self.pe = Electrode(
            am = self.raw_pe["ActiveMaterial"],
            binder = self.raw_pe["Binder"],
            add = self.raw_pe["Additive"],
            prop = self.raw_pe["Properties"],
            ad_prop = self.raw_pe["AdvancedProperties"]
        )
        self.ne.am = Material(
            mat = self.ne.am["Material"],
            prop = self.ne.am["Properties"],
            ad_prop = self.ne.am["AdvancedProperties"]
            )
        self.pe.am = Material(
            mat = self.pe.am["Material"],
            prop = self.pe.am["Properties"],
            ad_prop = self.pe.am["AdvancedProperties"]
            )
        self.ne.binder = Material(
            mat = self.ne.binder["Material"],
            prop = self.ne.binder["Properties"],
            ad_prop = self.ne.binder["AdvancedProperties"]
            )
        self.pe.binder = Material(
            mat = self.pe.binder["Material"],
            prop = self.pe.binder["Properties"],
            ad_prop = self.pe.binder["AdvancedProperties"]
            )
        self.ne.add = Material(
            mat = self.ne.add["Material"],
            prop = self.ne.add["Properties"],
            ad_prop = self.ne.add["AdvancedProperties"]
            )
        self.pe.add = Material(
            mat = self.pe.add["Material"],
            prop = self.pe.add["Properties"],
            ad_prop = self.pe.add["AdvancedProperties"]
            )
        
        self.raw_elyte = uploaded_dict["Electrolyte"]
        self.elyte = Material(
            mat = self.raw_elyte["Material"],
            prop = self.raw_elyte["Properties"],
            ad_prop = self.raw_elyte["AdvancedProperties"]
        )

        self.raw_sep = uploaded_dict["Separator"]
        self.sep = Material(
            mat = self.raw_sep["Material"],
            prop = self.raw_sep["Properties"],
            ad_prop = self.raw_sep["AdvancedProperties"]
        )
        
        self.raw_bc = uploaded_dict["BoundaryConditions"]
        self.bc = NonMaterial(
            prop = self.raw_bc["Properties"],
            ad_prop = self.raw_bc["AdvancedProperties"]
        )

        self.raw_cycle = uploaded_dict["Protocol"]
        self.cycle = NonMaterial(
            prop = self.raw_cycle["Properties"],
            ad_prop = self.raw_cycle["AdvancedProperties"]
        )


class GuiInputFormatting():
    def __init__(self, model):
        self.model = model
        self.gui_dict = {}
        self.get_gui_formatted_dict_from_uploaded_dict()


    def get_gui_formatted_dict_from_uploaded_dict(self):
        uploaded_file = app_access.get_path_to_uploaded_input()

        with open(uploaded_file, 'r') as f:
            input = json.load(f)

        dict = UploadDict(input)

        if "Model" in input:
            if input["Model"] == self.model:

                

                # Negative ELectrode
                ## Active Material
                if dict.ne.am.mat == "User Defined":
                    user_defined = "user_defined_ne_am"
                    
                    self.gui_dict["negative_electrode_active_material"] = dict.ne.am.mat_ud_id(user_defined)
                    self.gui_dict["negative_electrode_active_material_properties"] = self.user_defined_active_material_properties(dict.ne.am.prop)
                    

                else:
                    self.gui_dict["negative_electrode_active_material"] = dict.ne.am.mat_id(dict.ne.am.mat)
                    self.gui_dict["negative_electrode_active_material_properties"] = self.default_electrode_material_properties(dict.ne.am.prop)


                self.gui_dict["negative_electrode_active_material_advanced"] = {
                        "specific_heat_capacity": dict.ne.am.ad_prop.get("specificHeatCapacity"),
                        "thermal_conductivity": dict.ne.am.ad_prop.get("thermalConductivity")
                    }
                
                ## Binder
                if dict.ne.binder.mat == "User Defined":
                    user_defined = "user_defined_ne_binder"
                    
                    self.gui_dict["negative_electrode_binder"] = dict.ne.binder.mat_ud_id(user_defined)
                    self.gui_dict["negative_electrode_binder_properties"] = self.user_defined_binder_properties(dict.ne.binder.prop)
                    

                else:
                    self.gui_dict["negative_electrode_binder"] = dict.ne.binder.mat_id(dict.ne.binder.mat)
                    self.gui_dict["negative_electrode_binder_properties"] = self.default_electrode_material_properties(dict.ne.binder.prop)


                self.gui_dict["negative_electrode_binder_advanced"] = {
                        "electronic_conductivity": dict.ne.binder.ad_prop.get("electronicConductivity"),
                    }
                
                ## Additive
                if dict.ne.add.mat == "User Defined":
                    user_defined = "user_defined_ne_ad"
                    
                    self.gui_dict["negative_electrode_additive"] = dict.ne.add.mat_ud_id(user_defined)
                    self.gui_dict["negative_electrode_additive_properties"] = self.user_defined_additive_properties(dict.ne.add.prop)
                    

                else:
                    self.gui_dict["negative_electrode_additive"] = dict.ne.add.mat_id(dict.ne.add.mat)
                    self.gui_dict["negative_electrode_additive_properties"] = self.default_electrode_material_properties(dict.ne.add.prop)


                self.gui_dict["negative_electrode_additive_advanced"] = {
                    "electronic_conductivity": dict.ne.add.ad_prop.get("electronicConductivity"),
                    }
                
                ## Properties

                self.gui_dict["negative_electrode_properties"] = {
                    "coating_thickness": dict.ne.prop.get("coatingThickness"),
                    "coating_porosity": dict.ne.prop.get("coatingPorosity"),
                    "mass_loading": dict.ne.prop.get("massLoading")
                }

                self.gui_dict["negative_electrode_properties_advanced"] = {
                    "length": dict.ne.ad_prop.get("length"),
                    "width": dict.ne.ad_prop.get("width"),
                    "bruggeman_coefficient": dict.ne.ad_prop.get("bruggemanCoefficient")
                }
                
                
                # Positive Electrode
                # Active Material
                if dict.pe.am.mat == "User Defined":
                    user_defined = "user_defined_pe_am"
                    
                    self.gui_dict["positive_electrode_active_material"] = dict.pe.am.mat_ud_id(user_defined)
                    self.gui_dict["positive_electrode_active_material_properties"] = self.user_defined_active_material_properties(dict.pe.am.prop)
                    

                else:
                    self.gui_dict["positive_electrode_active_material"] = dict.pe.am.mat_id(dict.pe.am.mat)
                    self.gui_dict["positive_electrode_active_material_properties"] = self.default_electrode_material_properties(dict.pe.am.prop)


                self.gui_dict["positive_electrode_active_material_advanced"] = {
                        "specific_heat_capacity": dict.pe.am.ad_prop.get("specificHeatCapacity"),
                        "thermal_conductivity": dict.pe.am.ad_prop.get("thermalConductivity")
                    }
                
                ## Binder
                if dict.pe.binder.mat == "User Defined":
                    user_defined = "user_defined_pe_binder"
                    
                    self.gui_dict["positive_electrode_binder"] = dict.pe.binder.mat_ud_id(user_defined)
                    self.gui_dict["negative_electrode_binder_properties"] = self.user_defined_binder_properties(dict.pe.binder.prop)
                    

                else:
                    self.gui_dict["positive_electrode_binder"] = dict.pe.binder.mat_id(dict.pe.binder.mat)
                    self.gui_dict["negative_electrode_binder_properties"] = self.default_electrode_material_properties(dict.pe.binder.prop)


                self.gui_dict["positive_electrode_binder_advanced"] = {
                        "electronic_conductivity": dict.pe.binder.ad_prop.get("electronicConductivity"),
                    }
                
                ## Additive
                if dict.pe.add.mat == "User Defined":
                    user_defined = "user_defined_pe_ad"
                    
                    self.gui_dict["positive_electrode_additive"] = dict.pe.add.mat_ud_id(user_defined)
                    self.gui_dict["positive_electrode_additive_properties"] = self.user_defined_additive_properties(dict.pe.add.prop)
                    

                else:
                    self.gui_dict["positive_electrode_additive"] = dict.pe.add.mat_id(dict.pe.add.mat)
                    self.gui_dict["positive_electrode_additive_properties"] = self.default_electrode_material_properties(dict.pe.add.prop)


                self.gui_dict["positive_electrode_additive_advanced"] = {
                        "electronic_conductivity": dict.pe.add.ad_prop.get("electronicConductivity"),
                    }
                
                ## Properties

                self.gui_dict["positive_electrode_properties"] = {
                    "coating_thickness": dict.pe.prop.get("coatingThickness"),
                    "coating_porosity": dict.pe.prop.get("coatingPorosity"),
                    "mass_loading": dict.pe.prop.get("massLoading")
                }

                self.gui_dict["positive_electrode_properties_advanced"] = {
                    "length": dict.pe.ad_prop.get("length"),
                    "width": dict.pe.ad_prop.get("width"),
                    "bruggeman_coefficient": dict.pe.ad_prop.get("bruggemanCoefficient")
                }
                
                # Electrolyte
                
                if dict.elyte.mat == "User Defined":
                    user_defined = "user_defined_elyte"
                    
                    self.gui_dict["electrolyte_materials"] = dict.elyte.mat_ud_id(user_defined)
                    self.gui_dict["electrolyte_properties"] = self.user_defined_electrolyte_properties(dict.elyte.prop)
                    

                else:
                    self.gui_dict["electrolyte_materials"] = dict.elyte.mat_id(dict.elyte.mat)
                    self.gui_dict["electrolyte_properties"] = self.default_electrolyte_material_properties(dict.elyte.prop)


                self.gui_dict["electrolyte_advanced"] = {
                        "bruggeman_coefficient": dict.elyte.ad_prop.get("bruggemanCoefficient")
                    }
                
                # Separator

                if dict.sep.mat == "User Defined":
                    user_defined = "user_defined_sep"
                    
                    self.gui_dict["separator_materials"] = dict.sep.mat_ud_id(user_defined)
                    self.gui_dict["separator_properties"] = self.user_defined_separator_properties(dict.sep.prop)
                    

                else:
                    self.gui_dict["separator_materials"] = dict.sep.mat_id(dict.sep.mat)
                    self.gui_dict["separator_properties"] = self.default_separator_material_properties(dict.sep.prop)


                self.gui_dict["separator_advanced"] = {
                        "number_of_discrete_cells_separator": dict.sep.ad_prop.get("numberOfDiscreteCellsSeparator")
                    }
                
                # Boundary condictions

                self.gui_dict["boundary_conditions"] = {
                    "ambient_temperature": dict.bc.prop.get("ambientTemperature"),
                    "initial_temperature": dict.bc.prop.get("initialTemperature"),
                    "initial_state_of_charge": dict.bc.prop.get("initialStateOfCharge")
                }

                self.gui_dict["boundary_conditions_advanced"] = {
                    "external_heat_transfer_coefficient": dict.bc.ad_prop.get("externalHeatTransferCoefficient"),
                    "external_surface_area": dict.bc.ad_prop.get("externalSurfaceArea")
                }

                # Protocol

                self.gui_dict["protocol_properties"] = {
                    "protocol": dict.cycle.prop.get("protocol"),
                    "initial_step_type": dict.cycle.prop.get("initialStepType"),
                    "number_of_cycles": dict.cycle.prop.get("numberOfCycles")
                }

                self.gui_dict["protocol_properties_advanced"] = {
                    "protocol_name": dict.cycle.ad_prop.get("protocolName"),
                    "c_rate": dict.cycle.ad_prop.get("cRate"),
                    "lower_cutoff_voltage": dict.cycle.ad_prop.get("lowerCutOffVoltage"),
                    "upper_cutoff_voltage": dict.cycle.ad_prop.get("upperCutOffVoltage"),
                    "d_idt_limit": dict.cycle.ad_prop.get("D_idt_limit"),
                    "d_edt_limit": dict.cycle.ad_prop.get("D_edt_limit")
                }


            else:
                st.error("Your file can not be processed. You specified the wrong simulation model.")

        else:
            st.error("Your file can not be processed. You haven't specified the simulation model.")

    def default_electrode_material_properties(self, dict):
        return {
            "mass_fraction": dict.get("massFraction")
        }
    
    def default_electrolyte_material_properties(self, dict):
        return {
            "concentration": dict.get("concentration"),
            "EC_DMC_ratio": dict.get("EC_DMC_ratio")
        }
    
    def default_separator_material_properties(self, dict):
        return {
            "thickness": dict.get("thickness"),
            "porosity": dict.get("porosity"),
            "bruggeman_coefficient": dict.get("bruggemanCoefficient")
        }
    
    def user_defined_active_material_properties(self, dict):
        return {
            "mass_fraction": dict.get("massFraction"),
            "maximum_concentration": dict.get("maximumConcentration"),
            "volumetric_surface_area": dict.get("volumetricSurfaceArea"),
            "density": dict.get("density"),
            "number_of_electrons_transfered": dict.get("numberOfElectronsTransfered"),
            "activation_energy_of_reaction": dict.get("activationEnergyOfReaction"),
            "reaction_rate_constant": dict.get("reactionRateConstant"),
            "maximum_lithium_stoichiometry": dict.get("maximumLithiumStoichiometry"),
            "minimum_lithium_stochiometry": dict.get("minimumLithiumStochiometry"),
            "open_circuit_potential": {
                "function": dict.get("openCircuitPotential").get("function"),
                "argumentlist": dict.get("openCircuitPotential").get("argumentlist")
            }
        }
    
    def user_defined_binder_properties(self, dict):
        return {
            "density": dict.get("density"),
            "specific_heat_capacity": dict.get("specificHeatCapacity"),
            "thermal_conductivity": dict.get("thermalConductivity")
        }
    
    def user_defined_additive_properties(self, dict):
        return {
            "density": dict.get("density"),
            "specific_heat_capacity": dict.get("specificHeatCapacity"),
            "thermal_conductivity": dict.get("thermalConductivity")
        }
    
    def user_defined_electrolyte_properties(self, dict):
        return {
            "specific_heat_capacity": dict.get("specificHeatCapacity"),
            "thermal_conductivity": dict.get("thermalConductivity"),
            "density": dict.get("density"),
            "charge_carrier_name": dict.get("chargeCarrierName"),
            "charge_carrier_number": dict.get("chargeCarrierNumber"),
            "counter_ion_name": dict.get("CounterIonName"),
            "counter_ion_transference_number": dict.get("CounterIonTransferenceNumber"),
            "conductivity": {
                "function": dict.get("conductivity").get("function"),
                "argumentlist": dict.get("conductivity").get("argumentlist")
            },
            "diffusion_coefficient": {
                "function": dict.get("diffusion_coefficient").get("function"),
                "argumentlist": dict.get("diffusion_coefficient").get("argumentlist")
            }
        }
    
    def user_defined_separator_properties(self, dict):
        return {
            "specific_heat_capacity": dict.get("specificHeatCapacity"),
            "thermal_conductivity": dict.get("thermalConductivity"),
            "density": dict.get("density"),
        }