############################################
# Get BattMo json input from json ld format
############################################

import numpy as np
from itertools import chain
import streamlit as st
import json
import app_access


def get_dict_from_has_quantitative(has_quantitative, give_references=False):
    """
    Simplifies json ld dict to increase readability in this file
    """
    new_dict = {}
    reference_list = []

    for item in has_quantitative:

        if type(item) != str:

            if "hasNumericalPart" in item:
                item_value_type = item.get("hasNumericalPart", {}).get("@type", None)

                if item_value_type == "Real":
                    new_dict[item.get("rdfs:label")] = {
                        "value": item.get("hasNumericalPart", {}).get("hasNumericalValue"),
                        "unit": item.get("hasMeasurementUnit", {}).get("hasSymbolValue"),
                    }
                    if "schema:citation" in item:
                        reference = item["schema:citation"]["@id"]
                        new_dict[item.get("rdfs:label")]["reference_url"] = reference
                        if reference not in reference_list:
                            reference_list.append(reference)

                elif item_value_type == "Boolean":
                    new_dict[item.get("rdfs:label")] = {
                        "value": bool(item.get("hasNumericalPart", {}).get("hasNumericalValue"))
                    }

            elif "hasStringPart" in item:

                item_value_type = item.get("hasStringPart", {}).get("@type", None)
                if item_value_type:

                    if item.get("@type") != None and "Expression" in item.get("@type"):

                        new_dict[item.get("rdfs:label")] = {
                            "value": item.get("hasStringPart", {}).get("hasStringValue"),
                            "variable": item.get("hasVariable"),
                            "unit": item.get("hasMeasurementUnit", {}).get("hasSymbolValue"),
                        }

                        if "schema:citation" in item:
                            reference = item["schema:citation"]["@id"]
                            new_dict[item.get("rdfs:label")]["reference_url"] = reference
                            if reference not in reference_list:
                                reference_list.append(reference)

                    elif item_value_type == "String":
                        new_dict[item.get("rdfs:label")] = {
                            "value": item.get("hasStringPart", {}).get("hasStringValue")
                        }

                        if "schema:citation" in item:
                            reference = item["schema:citation"]["@id"]
                            new_dict[item.get("rdfs:label")]["reference_url"] = reference
                            if reference not in reference_list:
                                reference_list.append(reference)
            else:
                assert False, "item not handled. {}".format(item)

    return new_dict


class Electrode(object):
    def __init__(self, am, binder, add, prop):

        self.am = get_dict_from_has_quantitative(am)
        self.binder = get_dict_from_has_quantitative(binder)
        self.add = get_dict_from_has_quantitative(add)
        # self.cc = get_dict_from_has_quantitative(cc)
        self.properties = get_dict_from_has_quantitative(prop)


class GuiDict(object):
    """
    Create a python object from the parameter dict for easier access and better readability
    """

    def __init__(self, gui_dict):

        self.model = get_dict_from_has_quantitative(
            gui_dict.get("@graph").get("hasModel").get("hasQuantitativeProperty")
        )
        self.cell = get_dict_from_has_quantitative(
            gui_dict.get("@graph").get("hasBatteryCell").get("hasQuantitativeProperty")
        )
        self.bc = get_dict_from_has_quantitative(
            gui_dict.get("@graph").get("hasBoundaryConditions").get("hasQuantitativeProperty")
        )
        self.raw_ele = gui_dict.get("@graph").get("hasElectrode")
        self.raw_ele_pe = self.raw_ele.get("hasPositiveElectrode")
        self.raw_ele_ne = self.raw_ele.get("hasNegativeElectrode")

        self.pe = Electrode(
            am=self.raw_ele_pe.get("hasActiveMaterial").get("hasQuantitativeProperty"),
            binder=self.raw_ele_pe.get("hasBinder").get("hasQuantitativeProperty"),
            add=self.raw_ele_pe.get("hasConductiveAdditive").get("hasQuantitativeProperty"),
            # cc=self.raw_ele_pe.get("hasConstituent").get("hasQuantitativeProperty"),
            prop=self.raw_ele_pe.get("hasPositiveElectrode").get("hasQuantitativeProperty"),
        )

        self.ne = Electrode(
            am=self.raw_ele_ne.get("hasActiveMaterial").get("hasQuantitativeProperty"),
            binder=self.raw_ele_ne.get("hasBinder").get("hasQuantitativeProperty"),
            add=self.raw_ele_ne.get("hasConductiveAdditive").get("hasQuantitativeProperty"),
            # cc=self.raw_ne.get("hasConstituent")[0].get("hasQuantitativeProperty"),
            prop=self.raw_ele_ne.get("hasNegativeElectrode").get("hasQuantitativeProperty"),
        )

        self.elyte_mat = get_dict_from_has_quantitative(
            gui_dict.get("@graph").get("hasElectrolyte").get("hasQuantitativeProperty")
        )
        self.sep_mat = get_dict_from_has_quantitative(
            gui_dict.get("@graph").get("hasSeparator").get("hasQuantitativeProperty")
        )
        self.sep_prop = get_dict_from_has_quantitative(
            gui_dict.get("@graph").get("hasSeparator").get("hasQuantitativeProperty")
        )
        self.protocol = get_dict_from_has_quantitative(
            gui_dict.get("@graph").get("hasCyclingProcess").get("hasQuantitativeProperty")
        )


@st.cache_data
def get_batt_mo_dict_from_gui_dict(gui_dict):

    with open(app_access.get_path_to_calculated_values(), "r") as f:
        calculated_values = json.load(f)["calculatedParameters"]

    json_ld = GuiDict(gui_dict)

    if json_ld.protocol.get("protocol_name").get("value") == "CCCV":

        total_time = 2 / json_ld.protocol.get("d_rate").get("value") * 3600 * json_ld.protocol.get(
            "number_of_cycles"
        ).get("value") + 2 / json_ld.protocol.get("c_rate").get(
            "value"
        ) * 3600 * json_ld.protocol.get(
            "number_of_cycles"
        ).get(
            "value"
        )
    elif json_ld.protocol.get("protocol_name").get("value") == "CCDischarge":
        total_time = 2 / json_ld.protocol.get("d_rate").get("value") * 3600
    else:

        st.error("This cycling protocol is not handled yet.")

    if (
        "functionname" in json_ld.ne.am["open_circuit_potential"].get("value")
        and json_ld.ne.am["open_circuit_potential"].get("value")["functionname"] != None
    ):
        ne_am_function = "functionname"
    elif (
        "function" in json_ld.ne.am["open_circuit_potential"].get("value")
        and json_ld.ne.am["open_circuit_potential"].get("value")["function"] != None
    ):
        ne_am_function = "function"
    # elif "functionname" in json_ld.ne.am["open_circuit_potential"]:
    #     ne_am_function = "functionname"
    else:
        ne_am_function = None

    if (
        "functionname" in json_ld.pe.am["open_circuit_potential"].get("value")
        and json_ld.pe.am["open_circuit_potential"].get("value")["functionname"] != None
    ):
        pe_am_function = "functionname"
    elif (
        "function" in json_ld.pe.am["open_circuit_potential"].get("value")
        and json_ld.pe.am["open_circuit_potential"].get("value")["function"] != None
    ):
        pe_am_function = "function"
    # elif "functionname" in json_ld.pe.am["open_circuit_potential"]:
    #     pe_am_function = "functionname"
    else:
        pe_am_function = None

    if (
        "functionname" in json_ld.elyte_mat["conductivity"].get("value")
        and json_ld.elyte_mat["conductivity"].get("value")["functionname"] != None
    ):
        elyte_cond_function = "functionname"
    elif (
        "function" in json_ld.elyte_mat["conductivity"].get("value")
        and json_ld.elyte_mat["conductivity"].get("value")["function"] != None
    ):
        elyte_cond_function = "function"
    # elif "functionname" in json_ld.elyte_mat["conductivity"]:
    #     elyte_cond_function = "functionname"
    else:
        elyte_cond_function = None

    if (
        "functionname" in json_ld.elyte_mat["diffusion_coefficient"].get("value")
        and json_ld.elyte_mat["diffusion_coefficient"].get("value")["functionname"] != None
    ):
        elyte_diff_function = "functionname"
    elif (
        "function" in json_ld.elyte_mat["diffusion_coefficient"].get("value")
        and json_ld.elyte_mat["diffusion_coefficient"].get("value")["function"] != None
    ):
        elyte_diff_function = "function"
    # elif "functionname" in json_ld.elyte_mat["diffusion_coefficient"]:
    #     elyte_diff_function = "functionname"
    else:
        elyte_diff_function = None

    return {
        "Geometry": {
            "case": "1D",
            "faceArea": json_ld.cell.get("length").get("value")
            * json_ld.cell.get("width").get("value")
            * json_ld.cell.get("number_parallel_electrode_pairs_within_cell").get("value"),
        },
        "NegativeElectrode": {
            "Coating": {
                "thickness": json_ld.ne.properties.get("coating_thickness").get("value")
                * 10 ** (-6),
                "N": json_ld.ne.properties.get("number_of_discrete_cells_electrode").get("value"),
                "effectiveDensity": calculated_values["effective_density"]["negative_electrode"],
                "bruggemanCoefficient": json_ld.ne.properties.get("bruggeman_coefficient").get(
                    "value"
                ),
                "ActiveMaterial": {
                    "massFraction": json_ld.ne.am.get("mass_fraction").get("value"),
                    "density": json_ld.ne.am.get("density").get("value"),
                    "electronicConductivity": json_ld.ne.am.get("electronic_conductivity").get(
                        "value"
                    ),
                    "specificHeatCapacity": json_ld.ne.am.get("specific_heat_capacity").get(
                        "value"
                    ),
                    "thermalConductivity": json_ld.ne.am.get("thermal_conductivity").get("value"),
                    "Interface": {
                        "saturationConcentration": json_ld.ne.am.get("maximum_concentration").get(
                            "value"
                        ),
                        "volumetricSurfaceArea": json_ld.ne.am.get("volumetric_surface_area").get(
                            "value"
                        ),
                        "density": json_ld.ne.am.get("density").get("value"),
                        "numberOfElectronsTransferred": json_ld.ne.am.get(
                            "number_of_electrons_transferred"
                        ).get("value"),
                        "activationEnergyOfReaction": json_ld.ne.am.get(
                            "activation_energy_of_reaction"
                        ).get("value"),
                        "reactionRateConstant": json_ld.ne.am.get("reaction_rate_constant").get(
                            "value"
                        ),
                        "guestStoichiometry100": json_ld.ne.am.get(
                            "maximum_lithium_stoichiometry"
                        ).get("value"),
                        "guestStoichiometry0": json_ld.ne.am.get(
                            "minimum_lithium_stoichiometry"
                        ).get("value"),
                        "chargeTransferCoefficient": 0.5,
                        "openCircuitPotential": {
                            "type": "function",
                            ne_am_function: json_ld.ne.am.get("open_circuit_potential").get(
                                "value"
                            )[ne_am_function],
                            "argumentlist": json_ld.ne.am.get("open_circuit_potential").get(
                                "variable"
                            ),
                        },
                    },
                    "diffusionModelType": json_ld.model.get("solid_diffusion_model_type").get(
                        "value"
                    ),
                    "SolidDiffusion": {
                        "activationEnergyOfDiffusion": json_ld.ne.am.get(
                            "activation_energy_of_diffusion"
                        ).get("value"),
                        "referenceDiffusionCoefficient": json_ld.ne.am.get(
                            "diffusion_pre_exponential_factor"
                        ).get("value"),
                        "particleRadius": json_ld.ne.am.get("particle_radius").get("value"),
                        "N": json_ld.ne.am.get("number_of_discrete_cells_particle_radius").get(
                            "value"
                        ),
                    },
                },
                "Binder": {
                    "density": json_ld.ne.binder.get("density").get("value"),
                    "massFraction": json_ld.ne.binder.get("mass_fraction").get("value"),
                    "electronicConductivity": json_ld.ne.binder.get("electronic_conductivity").get(
                        "value"
                    ),
                    "specificHeatCapacity": json_ld.ne.binder.get("specific_heat_capacity").get(
                        "value"
                    ),
                    "thermalConductivity": json_ld.ne.binder.get("thermal_conductivity").get(
                        "value"
                    ),
                },
                "ConductingAdditive": {
                    "density": json_ld.ne.add.get("density").get("value"),
                    "massFraction": json_ld.ne.add.get("mass_fraction").get("value"),
                    "electronicConductivity": json_ld.ne.add.get("electronic_conductivity").get(
                        "value"
                    ),
                    "specificHeatCapacity": json_ld.ne.add.get("specific_heat_capacity").get(
                        "value"
                    ),
                    "thermalConductivity": json_ld.ne.add.get("thermal_conductivity").get("value"),
                },
            },
            "CurrentCollector": {
                "electronicConductivity": 35500000.0,
                "N": 5,
                "thickness": 25e-6,
                # "thermalConductivity": json_ld.ne.cc.get("thermal_conductivity"),
                # "specificHeatCapacity": json_ld.ne.cc.get("specific_heat_capacity"),
                # "density": json_ld.ne.cc.get("density")
            },
        },
        "PositiveElectrode": {
            "Coating": {
                "thickness": json_ld.pe.properties.get("coating_thickness").get("value")
                * 10 ** (-6),
                "N": json_ld.pe.properties.get("number_of_discrete_cells_electrode").get("value"),
                "effectiveDensity": calculated_values["effective_density"]["positive_electrode"],
                "bruggemanCoefficient": json_ld.pe.properties.get("bruggeman_coefficient").get(
                    "value"
                ),
                "ActiveMaterial": {
                    "massFraction": json_ld.pe.am.get("mass_fraction").get("value"),
                    "density": json_ld.pe.am.get("density").get("value"),
                    "electronicConductivity": json_ld.pe.am.get("electronic_conductivity").get(
                        "value"
                    ),
                    "specificHeatCapacity": json_ld.pe.am.get("specific_heat_capacity").get(
                        "value"
                    ),
                    "thermalConductivity": json_ld.pe.am.get("thermal_conductivity").get("value"),
                    "Interface": {
                        "saturationConcentration": json_ld.pe.am.get("maximum_concentration").get(
                            "value"
                        ),
                        "volumetricSurfaceArea": json_ld.pe.am.get("volumetric_surface_area").get(
                            "value"
                        ),
                        "density": json_ld.pe.am.get("density").get("value"),
                        "numberOfElectronsTransferred": json_ld.pe.am.get(
                            "number_of_electrons_transferred"
                        ).get("value"),
                        "activationEnergyOfReaction": json_ld.pe.am.get(
                            "activation_energy_of_reaction"
                        ).get("value"),
                        "reactionRateConstant": json_ld.pe.am.get("reaction_rate_constant").get(
                            "value"
                        ),
                        "guestStoichiometry100": json_ld.pe.am.get(
                            "maximum_lithium_stoichiometry"
                        ).get("value"),
                        "guestStoichiometry0": json_ld.pe.am.get(
                            "minimum_lithium_stoichiometry"
                        ).get("value"),
                        "chargeTransferCoefficient": 0.5,
                        "openCircuitPotential": {
                            "type": "function",
                            pe_am_function: json_ld.pe.am.get("open_circuit_potential").get(
                                "value"
                            )[pe_am_function],
                            "argumentlist": json_ld.pe.am.get("open_circuit_potential").get(
                                "variable"
                            ),
                        },
                    },
                    "diffusionModelType": json_ld.model.get("solid_diffusion_model_type").get(
                        "value"
                    ),
                    "SolidDiffusion": {
                        "activationEnergyOfDiffusion": json_ld.pe.am.get(
                            "activation_energy_of_diffusion"
                        ).get("value"),
                        "referenceDiffusionCoefficient": json_ld.pe.am.get(
                            "diffusion_pre_exponential_factor"
                        ).get("value"),
                        "particleRadius": json_ld.pe.am.get("particle_radius").get("value"),
                        "N": json_ld.pe.am.get("number_of_discrete_cells_particle_radius").get(
                            "value"
                        ),
                    },
                },
                "Binder": {
                    "density": json_ld.pe.binder.get("density").get("value"),
                    "massFraction": json_ld.pe.binder.get("mass_fraction").get("value"),
                    "electronicConductivity": json_ld.pe.binder.get("electronic_conductivity").get(
                        "value"
                    ),
                    "specificHeatCapacity": json_ld.pe.binder.get("specific_heat_capacity").get(
                        "value"
                    ),
                    "thermalConductivity": json_ld.pe.binder.get("thermal_conductivity").get(
                        "value"
                    ),
                },
                "ConductingAdditive": {
                    "density": json_ld.pe.add.get("density").get("value"),
                    "massFraction": json_ld.pe.add.get("mass_fraction").get("value"),
                    "electronicConductivity": json_ld.pe.add.get("electronic_conductivity").get(
                        "value"
                    ),
                    "specificHeatCapacity": json_ld.pe.add.get("specific_heat_capacity").get(
                        "value"
                    ),
                    "thermalConductivity": json_ld.pe.add.get("thermal_conductivity").get("value"),
                },
            },
            "CurrentCollector": {
                "electronicConductivity": 59600000.0,
                "N": 5,
                "thickness": 15e-6,
                # "thermalConductivity": json_ld.pe.cc.get("thermal_conductivity"),
                # "specificHeatCapacity": json_ld.pe.cc.get("specific_heat_capacity"),
                # "density": json_ld.pe.cc.get("density")
            },
        },
        "Separator": {
            "thickness": json_ld.sep_prop.get("thickness").get("value") * 10 ** (-6),
            "N": json_ld.sep_prop.get("number_of_discrete_cells_separator").get("value"),
            "porosity": json_ld.sep_prop.get("porosity").get("value"),
            "specificHeatCapacity": json_ld.sep_prop.get("specific_heat_capacity").get("value"),
            "thermalConductivity": json_ld.sep_prop.get("thermal_conductivity").get("value"),
            "density": json_ld.sep_prop.get("density").get("value"),
            "bruggemanCoefficient": json_ld.sep_prop.get("bruggeman_coefficient").get("value"),
        },
        "Electrolyte": {
            "initialConcentration": json_ld.elyte_mat.get("concentration").get("value"),
            "specificHeatCapacity": json_ld.elyte_mat.get("specific_heat_capacity").get("value"),
            "thermalConductivity": json_ld.elyte_mat.get("thermal_conductivity").get("value"),
            "density": json_ld.elyte_mat.get("density").get("value"),
            "ionicConductivity": {
                "type": "function",
                elyte_cond_function: json_ld.elyte_mat.get("conductivity").get("value")[
                    elyte_cond_function
                ],
                "argumentlist": json_ld.elyte_mat.get("conductivity").get("variable"),
            },
            "diffusionCoefficient": {
                "type": "function",
                elyte_diff_function: json_ld.elyte_mat.get("diffusion_coefficient").get("value")[
                    elyte_diff_function
                ],
                "argumentlist": json_ld.elyte_mat.get("diffusion_coefficient").get("variable"),
            },
            "compnames": [
                json_ld.elyte_mat.get("charge_carrier_name").get("value"),
                json_ld.elyte_mat.get("counter_ion_name").get("value"),
            ],
            "species": {
                "chargeNumber": json_ld.elyte_mat.get("charge_carrier_charge_number").get("value"),
                "transferenceNumber": json_ld.elyte_mat.get(
                    "charge_carrier_transference_number"
                ).get("value"),
                "nominalConcentration": 1000,
            },
            "bruggemanCoefficient": json_ld.elyte_mat.get("bruggeman_coefficient").get("value"),
        },
        "G": [],
        "SOC": json_ld.protocol.get("initial_state_of_charge").get("value"),
        # "Ucut": json_ld.protocol.get("lower_cutoff_voltage"),
        "initT": json_ld.bc.get("initial_temperature").get("value"),
        "use_thermal": json_ld.model.get("use_thermal").get("value"),
        "include_current_collectors": json_ld.model.get("include_current_collector").get("value"),
        # "use_particle_diffusion": json_ld.model.get("use_solid_diffusion_model"),
        "Control": {
            "controlPolicy": json_ld.protocol.get("protocol_name").get("value"),
            "initialControl": json_ld.protocol.get("initial_step_type").get("value"),
            "numberOfCycles": json_ld.protocol.get("number_of_cycles").get("value"),
            "CRate": json_ld.protocol.get("c_rate").get("value"),
            "DRate": json_ld.protocol.get("d_rate").get("value"),
            "lowerCutoffVoltage": json_ld.protocol.get("lower_cutoff_voltage").get("value"),
            "upperCutoffVoltage": json_ld.protocol.get("upper_cutoff_voltage").get("value"),
            "rampupTime": 10.0,
            "dIdtLimit": json_ld.protocol.get("d_idt_limit").get("value"),
            "dEdtLimit": json_ld.protocol.get("d_edt_limit").get("value"),
        },
        "ThermalModel": {
            "externalHeatTransferCoefficient": json_ld.bc.get(
                "external_heat_transfer_coefficient"
            ).get("value"),
            "externalTemperature": json_ld.bc.get("ambient_temperature").get("value"),
        },
        "TimeStepping": {
            "useRampup": json_ld.model.get("use_ramp_up").get("value"),
            "rampupTime": 10.0,
            # "totalTime": total_time,
            "numberOfRampupSteps": json_ld.protocol.get("number_of_ramp_up_steps").get("value"),
            # "numberOfRampupSteps": 10,
            "timeStepDuration": json_ld.protocol.get("time_step_duration").get("value"),
        },
        "Output": {"variables": ["energy"]},
    }


@st.cache_data
def get_indicators_from_gui_dict(gui_dict):

    json_ld = GuiDict(gui_dict)

    indicators = {
        "Cell": {
            "cellMass": {
                "value": json_ld.cell.get("cell_mass").get("value"),
                "unit": json_ld.cell.get("cell_mass").get("unit"),
            },
            "roundTripEfficiency": {"unit": json_ld.cell.get("round_trip_efficiency").get("unit")},
            "dischargeEnergy": {"unit": json_ld.cell.get("discharge_energy").get("unit")},
            "specificEnergy": {"unit": json_ld.cell.get("specific_energy").get("unit")},
            "energyEfficiency": {"unit": json_ld.cell.get("round_trip_efficiency").get("unit")},
            "nominalCellCapacity": {
                "value": json_ld.cell.get("nominal_cell_capacity").get("value"),
                "unit": json_ld.cell.get("nominal_cell_capacity").get("unit"),
            },
            "NPRatio": {
                "value": json_ld.cell.get("n_to_p_ratio").get("value"),
                "unit": json_ld.cell.get("n_to_p_ratio").get("unit"),
            },
        },
        "NegativeElectrode": {
            "massLoading": {
                "value": json_ld.ne.properties.get("mass_loading").get("value"),
                "unit": json_ld.ne.properties.get("mass_loading").get("unit"),
            },
            "thickness": {
                "value": json_ld.ne.properties.get("coating_thickness").get("value"),
                "unit": json_ld.ne.properties.get("coating_thickness").get("unit"),
            },
            "porosity": {
                "value": json_ld.ne.properties.get("coating_porosity").get("value"),
                "unit": json_ld.ne.properties.get("coating_porosity").get("unit"),
            },
            "specificCapacity": {
                "value": json_ld.ne.properties.get("electrode_capacity").get("value"),
                "unit": json_ld.ne.properties.get("electrode_capacity").get("unit"),
            },
            "ActiveMaterial": {
                "specificCapacity": {
                    "value": json_ld.ne.am.get("specific_capacity").get("value"),
                    "unit": json_ld.ne.am.get("specific_capacity").get("unit"),
                }
            },
        },
        "PositiveElectrode": {
            "massLoading": {
                "value": json_ld.pe.properties.get("mass_loading").get("value"),
                "unit": json_ld.pe.properties.get("mass_loading").get("unit"),
            },
            "thickness": {
                "value": json_ld.pe.properties.get("coating_thickness").get("value"),
                "unit": json_ld.pe.properties.get("coating_thickness").get("unit"),
            },
            "porosity": {
                "value": json_ld.pe.properties.get("coating_porosity").get("value"),
                "unit": json_ld.pe.properties.get("coating_porosity").get("unit"),
            },
            "specificCapacity": {
                "value": json_ld.pe.properties.get("electrode_capacity").get("value"),
                "unit": json_ld.pe.properties.get("electrode_capacity").get("unit"),
            },
            "ActiveMaterial": {
                "specificCapacity": {
                    "value": json_ld.pe.am.get("specific_capacity").get("value"),
                    "unit": json_ld.pe.am.get("specific_capacity").get("unit"),
                }
            },
        },
    }

    return indicators


def get_geometry_data_from_gui_dict(gui_dict):

    json_ld = GuiDict(gui_dict)
    geometry_data = {
        "length": json_ld.cell.get("length").get("value"),
        "width": json_ld.cell.get("width").get("value"),
        "thickness_ne": json_ld.ne.properties.get("coating_thickness").get("value"),
        "thickness_pe": json_ld.pe.properties.get("coating_thickness").get("value"),
        "thickness_sep": json_ld.sep_prop.get("thickness").get("value"),
        "particle_radius_ne": json_ld.ne.am.get("particle_radius").get("value"),
        "particle_radius_pe": json_ld.pe.am.get("particle_radius").get("value"),
        "porosity_ne": json_ld.ne.properties.get("coating_porosity").get("value"),
        "porosity_pe": json_ld.pe.properties.get("coating_porosity").get("value"),
        "porosity_sep": json_ld.sep_prop.get("porosity").get("value"),
    }

    return geometry_data
