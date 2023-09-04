######################
# Get BattMo json input from json ld format
#
# Several parameters in the BattMo json input are useless (ex: InterDiffusionCoefficient)
# Also many namings are not explicit enough (ex: "sp": {"z": ..., "t": ...} )
# It must be refactored on the BattMo side to get something more robust
######################


def get_dict_from_has_quantitative(has_quantitative):
    """
    Simplifies json ld dict to increase readability in this file
    """
    new_dict = {}
    for item in has_quantitative:
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
    def __init__(self, am, binder, add, cc, prop):

        self.am = get_dict_from_has_quantitative(am)
        self.binder = get_dict_from_has_quantitative(binder)
        self.add = get_dict_from_has_quantitative(add)
        self.cc = get_dict_from_has_quantitative(cc)
        self.properties = get_dict_from_has_quantitative(prop)


class GuiDict(object):
    """
    Create a python object from the parameter dict for easier access and better readability
    """
    def __init__(self, gui_dict):
        self.model = get_dict_from_has_quantitative(gui_dict.get("battery:P2DModel").get("hasQuantitativeProperty"))
        self.cell = get_dict_from_has_quantitative(gui_dict.get("battery:BatteryCell").get("hasQuantitativeProperty"))
        self.raw_ele = gui_dict.get("echem:Electrode")
        self.raw_ele_pe = self.raw_ele.get("echem:PositiveElectrode")
        print("PE=",self.raw_ele)
        self.pe = Electrode(
            am=self.raw_ele_pe.get("hasActiveMaterial")[0].get("hasQuantitativeProperty"),
            binder=self.raw_pe.get("echem:Binder").get("hasQuantitativeProperty"),
            add=self.raw_pe.get("echem:ConductiveAdditive").get("hasQuantitativeProperty"),
            cc=self.raw_pe.get("hasConstituent")[0].get("hasQuantitativeProperty"),
            prop=self.raw_pe.get("emmo:NominalProperty").get("hasQuantitativeProperty"),
        )

        self.raw_ne = gui_dict.get("echem:NegativeElectrode")
        self.ne = Electrode(
            am=self.raw_ne.get("hasActiveMaterial")[0].get("hasQuantitativeProperty"),
            binder=self.raw_ne.get("echem:Binder").get("hasQuantitativeProperty"),
            add=self.raw_ne.get("echem:ConductiveAdditive").get("hasQuantitativeProperty"),
            cc=self.raw_ne.get("hasConstituent")[0].get("hasQuantitativeProperty"),
            prop=self.raw_ne.get("emmo:NominalProperty").get("hasQuantitativeProperty"),
        )
        self.elyte = get_dict_from_has_quantitative(gui_dict.get("echem:Electrolyte").get("hasQuantitativeProperty"))
        self.sep = get_dict_from_has_quantitative(gui_dict.get("echem:Separator").get("hasQuantitativeProperty"))
        self.protocol = get_dict_from_has_quantitative(gui_dict.get("echem:CyclingProcess").get("hasQuantitativeProperty"))


def get_batt_mo_dict_from_gui_dict(gui_dict):
    json_ld = GuiDict(gui_dict)
    number_of_discrete_cells_electrode = json_ld.pe.am.get("number_of_discrete_cells_electrode")
    total_time = 2 / json_ld.protocol.get("c_rate") * json_ld.protocol.get("number_of_cycles") * 3600

    return {
        "Geometry": {
            "case": "1D",
            "faceArea": 1#json_ld.pe.properties.get("length") * json_ld.pe.properties.get("width")
        },
        "NegativeElectrode": {
            "ActiveMaterial": {
                "thickness": 6.4e-05,# json_ld.ne.properties.get("coating_thickness"),
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
                        "functionname": json_ld.ne.am.get("open_circuit_potential"),
                        "argumentlist": ["cElectrode", "T", "cmax"]
                    },
                    "BruggemanCoefficient": json_ld.ne.properties.get("bruggeman_coefficient")
                },
                "diffusionModelType": json_ld.model.get("solid_diffusion_model_type"),
                "SolidDiffusion": {
                    "EaD": 0,#json_ld.ne.am.get("activation_energy_of_diffusion"),
                    "D0": 3.3e-14,#json_ld.ne.am.get("diffusion_pre_exponential_factor"),
                    "rp":5.86e-06,#json_ld.ne.am.get("particle_radius"),
                    "N": number_of_discrete_cells_electrode
                }
            },
            "CurrentCollector": {
                "EffectiveElectricalConductivity": json_ld.ne.cc.get("electronic_conductivity"),
                "N" : 5,
                "thickness" : 25e-6 
                #"thermalConductivity": json_ld.ne.cc.get("thermal_conductivity"),
                #"specificHeatCapacity": json_ld.ne.cc.get("specific_heat_capacity"),
                #"density": json_ld.ne.cc.get("density")
            }
        },
        "PositiveElectrode": {
            "ActiveMaterial": {
                "thickness": 5.7e-05,#json_ld.pe.properties.get("coating_thickness"),
                "N": number_of_discrete_cells_electrode,
                #"specificHeatCapacity": json_ld.pe.am.get("specific_heat_capacity"),
                #"thermalConductivity": json_ld.pe.am.get("thermal_conductivity"),
                #"InterDiffusionCoefficient": 1e-14,
                #"InterDiffusionCoefficientComment": "from Ecker 2015",
                "electricalConductivity": json_ld.pe.am.get("electronic_conductivity"),
                "BruggemanCoefficient": json_ld.pe.properties.get("bruggeman_coefficient"),
                "Interface": {
                    "cmax": 55554,#json_ld.pe.am.get("maximum_concentration"),
                    "volumeFraction": 0.8,#json_ld.pe.am.get("volume_fraction"),
                    "volumetricSurfaceArea": 885000,#json_ld.pe.am.get("volumetric_surface_area"),
                    #"density": json_ld.pe.am.get("density"),
                    "n": json_ld.pe.am.get("number_of_electrons_transferred"),
                    "Eak": 5000,#json_ld.pe.am.get("activation_energy_of_reaction"),
                    "k0": 2.33e-11,#json_ld.pe.am.get("reaction_rate_constant"),
                    "theta100": 0.4955,#json_ld.pe.am.get("maximum_lithium_stoichiometry"),
                    "theta0": 0.99174,#json_ld.pe.am.get("minimum_lithium_stoichiometry"),
                    "OCP": {
                        "type": "function",
                        "functionname": "compute_ocp_nmc111",
                        #"functionname": json_ld.pe.am.get("open_circuit_potential"),
                        "argumentlist": ["cElectrode", "T", "cmax"]
                    },
                    "BruggemanCoefficient": json_ld.pe.properties.get("bruggeman_coefficient")
                },
                "diffusionModelType": json_ld.model.get("solid_diffusion_model_type"),
                "SolidDiffusion": {
                    "EaD": 0, #json_ld.pe.am.get("activation_energy_of_diffusion"),
                    "D0": 4e-15,#json_ld.pe.am.get("diffusion_pre_exponential_factor"),
                    "rp": 5.22e-6,#json_ld.pe.am.get("particle_radius"),
                    "N": number_of_discrete_cells_electrode
                }
            },
            "CurrentCollector": {
                "EffectiveElectricalConductivity": json_ld.pe.cc.get("electronic_conductivity"),
                "N" : 5,
                "thickness" : 15e-6
                #"thermalConductivity": json_ld.pe.cc.get("thermal_conductivity"),
                #"specificHeatCapacity": json_ld.pe.cc.get("specific_heat_capacity"),
                #"density": json_ld.pe.cc.get("density")
            }
        },
        "Electrolyte": {
            "Separator": {
                "thickness": 1.5e-05,#json_ld.sep.get("thickness"),
                "N": number_of_discrete_cells_electrode,
                "porosity": json_ld.sep.get("porosity"),
                #"specificHeatCapacity": json_ld.sep.get("specific_heat_capacity"),
                #"thermalConductivity": json_ld.sep.get("thermal_conductivity"),
                #"density": json_ld.sep.get("density"),
                "BruggemanCoefficient": 1.5#json_ld.sep.get("bruggeman_coefficient")
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
                "z": json_ld.elyte.get("charge_carrier_charge_number"),
                "t": json_ld.elyte.get("counter_ion_transference_number")
            },
            "BruggemanCoefficient": json_ld.elyte.get("bruggeman_coefficient")
        },
        #"G": [],
        "SOC": json_ld.cell.get("initial_state_of_charge"),
        #"Ucut": json_ld.protocol.get("lower_cutoff_voltage"),
        "initT": json_ld.cell.get("initial_temperature"),
        #"use_thermal": json_ld.model.get("use_thermal"),
        "include_current_collectors": json_ld.model.get("include_current_collector"),
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
