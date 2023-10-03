######################
# Get BattMo json input from json ld format
#
# Several parameters in the BattMo json input are useless (ex: InterDiffusionCoefficient)
# Also many namings are not explicit enough (ex: "sp": {"z": ..., "t": ...} )
# It must be refactored on the BattMo side to get something more robust
######################
import numpy as np
from itertools import chain

def get_dict_from_has_quantitative(has_quantitative):
    """
    Simplifies json ld dict to increase readability in this file
    """
    new_dict = {}
    # if type(has_quantitative) == list:
    #     has_quantitative = has_quantitative[0]
    print("quant=", has_quantitative)
    for item in has_quantitative:

        #if type(item) ==list:
        
        # item =list(chain.from_iterable(item))
        # print("item2=", item)
        if type(item) != str:
            item_value_type = item.get("value", {}).get("@type", None)
            if item_value_type == "emmo:Numerical":
                new_dict[item.get("label")] = item.get("value", {}).get("hasNumericalData")
            elif item_value_type == "emmo:String":
                new_dict[item.get("label")] = item.get("value", {}).get("hasStringData")
            elif item_value_type == "emmo:Boolean":
                new_dict[item.get("label")] = bool(item.get("value", {}).get("hasStringData"))
            elif item_value_type is None:
                new_dict[item.get("label")] = item.get("value", {})
            else:
                assert False, "item not handled. {}".format(item)

    return new_dict


class Electrode(object):
    def __init__(self, am, binder, add, prop):
        print("am=",am)

        self.am = get_dict_from_has_quantitative(am)
        self.binder = get_dict_from_has_quantitative(binder)
        self.add = get_dict_from_has_quantitative(add)
        #self.cc = get_dict_from_has_quantitative(cc)
        self.properties = get_dict_from_has_quantitative(prop)


class GuiDict(object):
    """
    Create a python object from the parameter dict for easier access and better readability
    """
    def __init__(self, gui_dict):
        self.model = get_dict_from_has_quantitative(gui_dict.get("battery:P2DModel").get("hasQuantitativeProperty"))
        self.cell = get_dict_from_has_quantitative(gui_dict.get("battery:BatteryCell").get("battery:BatteryCell").get("battery:BatteryCell").get("battery:BatteryCell").get("hasQuantitativeProperty"))
        self.raw_ele = gui_dict.get("echem:Electrode").get("echem:Electrode")
        self.raw_ele_pe = self.raw_ele.get("echem:PositiveElectrode")
        self.raw_ele_ne = self.raw_ele.get("echem:NegativeElectrode")
        print("PE=",self.raw_ele_pe)
        self.pe = Electrode(
            
            am=self.raw_ele_pe.get("echem:ActiveMaterial").get("hasQuantitativeProperty"),
            binder=self.raw_ele_pe.get("echem:Binder").get("hasQuantitativeProperty"),
            add=self.raw_ele_pe.get("echem:ConductiveAdditive").get("hasQuantitativeProperty"),
            #cc=self.raw_ele_pe.get("hasConstituent").get("hasQuantitativeProperty"),
            prop=self.raw_ele_pe.get("emmo:NominalProperty").get("hasQuantitativeProperty"),
        )

        
        self.ne = Electrode(
            am=self.raw_ele_ne.get("echem:ActiveMaterial").get("hasQuantitativeProperty"),
            binder=self.raw_ele_ne.get("echem:Binder").get("hasQuantitativeProperty"),
            add=self.raw_ele_ne.get("echem:ConductiveAdditive").get("hasQuantitativeProperty"),
            #cc=self.raw_ne.get("hasConstituent")[0].get("hasQuantitativeProperty"),
            prop=self.raw_ele_ne.get("emmo:NominalProperty").get("hasQuantitativeProperty"),
        )
        
        self.elyte_mat = get_dict_from_has_quantitative(gui_dict.get("echem:Electrolyte").get("echem:Electrolyte").get("echem:Electrolyte").get("echem:ElectrolyteMaterial").get("hasQuantitativeProperty"))
        self.sep_mat = get_dict_from_has_quantitative(gui_dict.get("echem:Separator").get("echem:Separator").get("echem:Separator").get("echem:SeparatorMaterial").get("hasQuantitativeProperty"))
        self.sep_prop = get_dict_from_has_quantitative(gui_dict.get("echem:Separator").get("echem:Separator").get("echem:Separator").get("echem:Separator").get("hasQuantitativeProperty"))
        self.protocol = get_dict_from_has_quantitative(gui_dict.get("echem:CyclingProcess").get("echem:CyclingProcess").get("echem:CyclingProcess").get("echem:CyclingProcess").get("hasQuantitativeProperty"))
        self.el = get_dict_from_has_quantitative(self.raw_ele.get("echem:Electrode").get("hasQuantitativeProperty"))

def get_batt_mo_dict_from_gui_dict(gui_dict):
    json_ld = GuiDict(gui_dict)
    number_of_discrete_cells_electrode = json_ld.ne.am.get("number_of_discrete_cells_electrode")
    total_time = 2 / json_ld.protocol.get("c_rate") * json_ld.protocol.get("number_of_cycles") * 3600

    return {
        "Geometry": {
            "case": "1D",
            "faceArea": 1#json_ld.pe.properties.get("length") * json_ld.pe.properties.get("width")
        },
        "NegativeElectrode": {
            "ActiveMaterial": {
                "thickness": json_ld.ne.properties.get("coating_thickness")*10**(-6),#6.4e-05 ,
                "N": number_of_discrete_cells_electrode,
                #"specificHeatCapacity": json_ld.ne.am.get("specific_heat_capacity"),
                #"thermalConductivity": json_ld.ne.am.get("thermal_conductivity"),
                #"InterDiffusionCoefficient": 1e-14,
               # "InterDiffusionCoefficientComment": "from Ecker 2015",
                "electricalConductivity": json_ld.ne.am.get("electronic_conductivity"),
                "BruggemanCoefficient": json_ld.ne.properties.get("bruggeman_coefficient"),
                "Interface": {
                    "cmax": json_ld.ne.am.get("maximum_concentration"),
                    "volumeFraction": json_ld.ne.am.get("volume_fraction"),
                    "volumetricSurfaceArea": json_ld.ne.am.get("volumetric_surface_area"),
                    #"density": json_ld.ne.am.get("density"),
                    "n": json_ld.ne.am.get("number_of_electrons_transferred"),
                    "Eak": json_ld.ne.am.get("activation_energy_of_reaction"),
                    "k0": json_ld.ne.am.get("reaction_rate_constant"),
                    "theta100": json_ld.ne.am.get("maximum_lithium_stoichiometry"),
                    "theta0": json_ld.ne.am.get("minimum_lithium_stoichiometry"),
                    "OCP": {
                        "type": "function",
                        "functionname": json_ld.ne.am.get("open_circuit_potential")["functionname"],#"compute_ocp_graphite"
                        "argumentlist": json_ld.ne.am.get("open_circuit_potential")["argument_list"]
                    },
                    "BruggemanCoefficient": json_ld.ne.properties.get("bruggeman_coefficient")
                },
                "diffusionModelType": json_ld.model.get("solid_diffusion_model_type"),
                "SolidDiffusion": {
                    "EaD": json_ld.ne.am.get("activation_energy_of_diffusion"),#0,
                    "D0": json_ld.ne.am.get("diffusion_pre_exponential_factor"),#3.3e-14
                    "rp":json_ld.ne.am.get("particle_radius"),#5.86e-06
                    "N": number_of_discrete_cells_electrode
                }
            },
            "CurrentCollector": {
                "EffectiveElectricalConductivity":35500000.0,# json_ld.ne.cc.get("electronic_conductivity"),
                "N" : 5,
                "thickness" : 25e-6 
                #"thermalConductivity": json_ld.ne.cc.get("thermal_conductivity"),
                #"specificHeatCapacity": json_ld.ne.cc.get("specific_heat_capacity"),
                #"density": json_ld.ne.cc.get("density")
            }
        },
        "PositiveElectrode": {
            "ActiveMaterial": {
                "thickness": json_ld.pe.properties.get("coating_thickness")*10**(-6),#5.7e-05
                "N": number_of_discrete_cells_electrode,
                #"specificHeatCapacity": json_ld.pe.am.get("specific_heat_capacity"),
                #"thermalConductivity": json_ld.pe.am.get("thermal_conductivity"),
                #"InterDiffusionCoefficient": 1e-14,
                #"InterDiffusionCoefficientComment": "from Ecker 2015",
                "electricalConductivity": json_ld.pe.am.get("electronic_conductivity"),
                "BruggemanCoefficient": json_ld.pe.properties.get("bruggeman_coefficient"),
                "Interface": {
                    "cmax": json_ld.pe.am.get("maximum_concentration"),#55554
                    "volumeFraction": json_ld.pe.am.get("volume_fraction"),#0.8
                    "volumetricSurfaceArea": json_ld.pe.am.get("volumetric_surface_area"),#885000
                    #"density": json_ld.pe.am.get("density"),
                    "n": json_ld.pe.am.get("number_of_electrons_transferred"),
                    "Eak": json_ld.pe.am.get("activation_energy_of_reaction"),#5000
                    "k0": json_ld.pe.am.get("reaction_rate_constant"),#2.33e-11
                    "theta100": json_ld.pe.am.get("maximum_lithium_stoichiometry"),#0.4955
                    "theta0": json_ld.pe.am.get("minimum_lithium_stoichiometry"),#0.99174
                    "OCP": {
                        "type": "function",
                        #"functionname": "compute_ocp_nmc111",
                        "functionname": json_ld.pe.am.get("open_circuit_potential")["functionname"],
                        "argumentlist": json_ld.pe.am.get("open_circuit_potential")["argument_list"]
                    },
                    "BruggemanCoefficient": json_ld.pe.properties.get("bruggeman_coefficient")
                },
                "diffusionModelType": json_ld.model.get("solid_diffusion_model_type"),
                "SolidDiffusion": {
                    "EaD": json_ld.pe.am.get("activation_energy_of_diffusion"), #0
                    "D0": json_ld.pe.am.get("diffusion_pre_exponential_factor"),#4e-15
                    "rp": json_ld.pe.am.get("particle_radius"),#5.22e-6
                    "N": number_of_discrete_cells_electrode
                }
            },
            "CurrentCollector": {
                "EffectiveElectricalConductivity": 59600000.0,#json_ld.pe.cc.get("electronic_conductivity"),
                "N" : 5,
                "thickness" : 15e-6
                #"thermalConductivity": json_ld.pe.cc.get("thermal_conductivity"),
                #"specificHeatCapacity": json_ld.pe.cc.get("specific_heat_capacity"),
                #"density": json_ld.pe.cc.get("density")
            }
        },
        "Electrolyte": {
            "Separator": {
                "thickness": json_ld.sep_prop.get("thickness")*10**(-6),#1.5e-05
                "N": number_of_discrete_cells_electrode,
                "porosity": json_ld.sep_prop.get("porosity"),
                #"specificHeatCapacity": json_ld.sep.get("specific_heat_capacity"),
                #"thermalConductivity": json_ld.sep.get("thermal_conductivity"),
                #"density": json_ld.sep.get("density"),
                "BruggemanCoefficient": json_ld.sep_prop.get("bruggeman_coefficient")#1.5
            },
            #"specificHeatCapacity": json_ld.elyte.get("specific_heat_capacity"),
            #"thermalConductivity": json_ld.elyte.get("thermal_conductivity"),
            #"density": json_ld.elyte.get("density"),
            "Conductivity": {
                "type": "function",
                "functionname": "computeElectrolyteConductivity_default", #json_ld.elyte.get("conductivity"),
                "argumentlist": ["c", "T"]
            },
            "DiffusionCoefficient": {
                "type": "function",
                "functionname": "computeDiffusionCoefficient_default", #json_ld.elyte.get("diffusion_coefficient"),
                "argumentlist": ["c", "T"]
            },
            # "compnames": [
            #     json_ld.elyte.get("charge_carrier_name"),
            #     json_ld.elyte.get("counter_ion_name")
            # ],
            "sp": {
                "z": json_ld.elyte_mat.get("charge_carrier_charge_number"),
                "t": json_ld.elyte_mat.get("counter_ion_transference_number")
            },
            "BruggemanCoefficient": json_ld.elyte_mat.get("bruggeman_coefficient")
        },
        #"G": [],
        "SOC": json_ld.cell.get("initial_state_of_charge"),
        #"Ucut": json_ld.protocol.get("lower_cutoff_voltage"),
        "initT": json_ld.cell.get("initial_temperature"),
        #"use_thermal": json_ld.model.get("use_thermal"),
        "include_current_collectors": False, #json_ld.model.get("include_current_collector"),
        #"use_particle_diffusion": json_ld.model.get("use_solid_diffusion_model"),
        "Control": {
            "controlPolicy": json_ld.protocol.get("protocol_name"),
            "initialControl": json_ld.protocol.get("initial_step_type"),
            "CRate": json_ld.protocol.get("c_rate"),
            "lowerCutoffVoltage": json_ld.protocol.get("lower_cutoff_voltage"),
            "tup" : 0.1
            #"upperCutoffVoltage": json_ld.protocol.get("upper_cutoff_voltage"),
            #"dIdtLimit": json_ld.protocol.get("d_idt_limit"),
            #"dEdtLimit": json_ld.protocol.get("d_edt_limit")
        },
        # "ThermalModel": {
        #     "externalHeatTransferCoefficient": json_ld.cell.get("external_heat_transfer_coefficient"),
        #     "externalTemperature": json_ld.cell.get("ambient_temperature")
        # },
        "TimeStepping": {
            "totalTime": total_time,
            "N": total_time / json_ld.model.get("time_step_duration"),
            "useRampup": json_ld.model.get("use_ramp_up"),
            "rampupTime": json_ld.model.get("ramp_up_time")
        }
        # "Output": {
        #     "variables": [
        #         "energy"
        #     ]
        # }
    }
