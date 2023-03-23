class Electrode(object):
    def __init__(self, name, parameters):
        assert name in ["positive", "negative"], "name {} not handled".format(name)

        self.am = parameters.get("{}_electrode_active_material".format(name))
        self.binder = parameters.get("{}_electrode_binder".format(name))
        self.add = parameters.get("{}_electrode_additive".format(name))
        self.cc = parameters.get("{}_electrode_current_collector".format(name))
        self.properties = parameters.get("{}_electrode_properties".format(name))


class GuiDict(object):
    def __init__(self, gui_dict):
        self.model = gui_dict.get("model")
        self.cell = gui_dict.get("cell")
        self.pe = Electrode("positive", gui_dict.get("positive_electrode"))
        self.ne = Electrode("negative", gui_dict.get("negative_electrode"))
        self.elyte = gui_dict.get("electrolyte")
        self.sep = gui_dict.get("separator")
        self.protocol = gui_dict.get("protocol")


def get_batt_mo_dict_from_gui_dict(gui_dict):
    p = GuiDict(gui_dict)
    number_of_discrete_cells_electrode = p.pe.am.get("number_of_discrete_cells_electrode")
    total_time = 2 / p.protocol.get("c_rate") * p.protocol.get("number_of_cycles") * 3600

    return {
        "Geometry": {
            "case": "1D",
            "faceArea": p.pe.properties.get("length") * p.pe.properties.get("width")
        },
        "NegativeElectrode": {
            "ActiveMaterial": {
                "thickness": p.ne.properties.get("coating_thickness"),
                "N": number_of_discrete_cells_electrode,
                "specificHeatCapacity": p.ne.am.get("specific_heat_capacity"),
                "thermalConductivity": p.ne.am.get("thermal_conductivity"),
                "InterDiffusionCoefficient": 1e-14,
                "InterDiffusionCoefficientComment": "from Ecker 2015",
                "electricalConductivity": p.ne.am.get("electronic_conductivity"),
                "BruggemanCoefficient": p.ne.properties.get("bruggeman_coefficient"),
                "Interface": {
                    "cmax": p.ne.am.get("maximum_concentration"),
                    "volumeFraction": p.ne.am.get("volume_fraction"),
                    "volumetricSurfaceArea": p.ne.am.get("volumetric_surface_area"),
                    "density": p.ne.am.get("density"),
                    "n": p.ne.am.get("number_of_electrons_transferred"),
                    "Eak": p.ne.am.get("activation_energy_of_reaction"),
                    "k0": p.ne.am.get("reaction_rate_constant"),
                    "theta100": p.ne.am.get("maximum_lithium_stoichiometry"),
                    "theta0": p.ne.am.get("minimum_lithium_stoichiometry"),
                    "OCP": p.ne.am.get("open_circuit_potential"),
                    "BruggemanCoefficient": p.ne.properties.get("bruggeman_coefficient")
                },
                "diffusionModelType": p.model.get("solid_diffusion_model_type"),
                "SolidDiffusion": {
                    "EaD": p.ne.am.get("activation_energy_of_diffusion"),
                    "D0": p.ne.am.get("diffusion_pre_exponential_factor"),
                    "rp": p.ne.am.get("particle_radius"),
                    "N": number_of_discrete_cells_electrode
                }
            },
            "CurrentCollector": {
                "EffectiveElectricalConductivity": p.ne.cc.get("electronic_conductivity"),
                "thermalConductivity": p.ne.cc.get("thermal_conductivity"),
                "specificHeatCapacity": p.ne.cc.get("specific_heat_capacity"),
                "density": p.ne.cc.get("density")
            }
        },
        "PositiveElectrode": {
            "ActiveMaterial": {
                "thickness": p.pe.properties.get("coating_thickness"),
                "N": number_of_discrete_cells_electrode,
                "specificHeatCapacity": p.pe.am.get("specific_heat_capacity"),
                "thermalConductivity": p.pe.am.get("thermal_conductivity"),
                "InterDiffusionCoefficient": 1e-14,
                "InterDiffusionCoefficientComment": "from Ecker 2015",
                "electricalConductivity": p.pe.am.get("electronic_conductivity"),
                "BruggemanCoefficient": p.pe.properties.get("bruggeman_coefficient"),
                "Interface": {
                    "cmax": p.pe.am.get("maximum_concentration"),
                    "volumeFraction": p.pe.am.get("volume_fraction"),
                    "volumetricSurfaceArea": p.pe.am.get("volumetric_surface_area"),
                    "density": p.pe.am.get("density"),
                    "n": p.pe.am.get("number_of_electrons_transferred"),
                    "Eak": p.pe.am.get("activation_energy_of_reaction"),
                    "k0": p.pe.am.get("reaction_rate_constant"),
                    "theta100": p.pe.am.get("maximum_lithium_stoichiometry"),
                    "theta0": p.pe.am.get("minimum_lithium_stoichiometry"),
                    "OCP": p.pe.am.get("open_circuit_potential"),
                    "BruggemanCoefficient": p.pe.properties.get("bruggeman_coefficient")
                },
                "diffusionModelType": p.model.get("solid_diffusion_model_type"),
                "SolidDiffusion": {
                    "EaD": p.pe.am.get("activation_energy_of_diffusion"),
                    "D0": p.pe.am.get("diffusion_pre_exponential_factor"),
                    "rp": p.pe.am.get("particle_radius"),
                    "N": number_of_discrete_cells_electrode
                }
            },
            "CurrentCollector": {
                "EffectiveElectricalConductivity": p.pe.cc.get("electronic_conductivity"),
                "thermalConductivity": p.pe.cc.get("thermal_conductivity"),
                "specificHeatCapacity": p.pe.cc.get("specific_heat_capacity"),
                "density": p.pe.cc.get("density")
            }
        },
        "Electrolyte": {
            "Separator": {
                "thickness": p.sep.get("thickness"),
                "N": number_of_discrete_cells_electrode,
                "porosity": 0.55,
                "specificHeatCapacity": p.sep.get("specific_heat_capacity"),
                "thermalConductivity": p.sep.get("thermal_conductivity"),
                "density": p.sep.get("density"),
                "BruggemanCoefficient": p.sep.get("bruggeman_coefficient")
            },
            "specificHeatCapacity": p.elyte.get("specific_heat_capacity"),
            "thermalConductivity": p.elyte.get("thermal_conductivity"),
            "density": p.elyte.get("density"),
            "Conductivity": p.elyte.get("conductivity"),
            "DiffusionCoefficient": p.elyte.get("diffusion_coefficient"),
            "compnames": [
                p.elyte.get("charge_carrier_name"),
                p.elyte.get("counter_ion_name")
            ],
            "sp": {
                "z": p.elyte.get("charge_carrier_charge_number"),
                "t": p.elyte.get("counter_ion_transference_number")
            },
            "BruggemanCoefficient": p.elyte.get("bruggeman_coefficient")
        },
        "G": [],
        "SOC": p.cell.get("initial_state_of_charge"),
        "Ucut": p.protocol.get("lower_cutoff_voltage"),
        "initT": p.cell.get("initial_temperature"),
        "use_thermal": p.model.get("use_thermal"),
        "include_current_collectors": p.model.get("include_current_collector"),
        "use_particle_diffusion": p.model.get("use_solid_diffusion_model"),
        "Control": {
            "controlPolicy": p.protocol.get("protocol_name"),
            "initialControl": p.protocol.get("initial_step_type"),
            "CRate": p.protocol.get("c_rate"),
            "lowerCutoffVoltage": p.protocol.get("lower_cutoff_voltage"),
            "upperCutoffVoltage": p.protocol.get("upper_cutoff_voltage"),
            "dIdtLimit": p.protocol.get("d_idt_limit"),
            "dEdtLimit": p.protocol.get("d_edt_limit")
        },
        "ThermalModel": {
            "externalHeatTransferCoefficient": p.cell.get("external_heat_transfer_coefficient"),
            "externalTemperature": p.cell.get("ambient_temperature")
        },
        "TimeStepping": {
            "totalTime": total_time,
            "N": total_time / p.model.get("time_step_duration"),
            "useRampup": p.model.get("use_ramp_up"),
            "rampupTime": p.model.get("ramp_up_time")
        },
        "Output": {
            "variables": [
                "energy"
            ]
        }
    }
