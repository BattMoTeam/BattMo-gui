import numpy as np
import os
import sys
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app_scripts.app_parameter_model import *
from database import db_helper


class SetupLinkedDataStruct():

    def __init__(self):
        # Ontology definitions
                    
        self.id = "@id"
        self.type = "@type"
        self.label = "rdfs:label"

        self.hasInput = "hasInput"
        self.hasActiveMaterial = "hasActiveMaterial"
        self.hasBinder = "hasBinder"
        self.hasConductiveAdditive = "hasConductiveAdditive"
        self.hasElectrode = "hasElectrode"
        self.hasNegativeElectrode = "hasNegativeElectrode"
        self.hasPositiveElectrode = "hasPositiveElectrode"
        self.hasElectrolyte = "hasElectrolyte"
        self.hasSeparator = "hasSeparator"
        self.hasBoundaryConditions = "hasBoundaryConditions"
        self.hasCyclingProcess = "hasCyclingProcess"
        self.hasBatteryCell = "hasBatteryCell"

        self.hasQuantitativeProperty = "hasQuantitativeProperty"
        self.hasObjectiveProperty = "hasObjectiveProperty"
        self.hasConstituent = "hasConstituent"
        self.hasNumericalData = "hasNumericalData"
        self.hasNumericalPart = "hasNumericalPart"
        self.hasNumericalValue = "hasNumericalValue"
        self.hasStringData = "hasStringData"
        self.hasStringValue = "hasStringValue"
        self.hasStringPart = "hasStringPart"
        self.hasModel = "hasModel"
        self.hasCell = "hasCell"

        self.universe_label = "MySimulationSetup"
        self.cell_label = "MyCell"
        self.cell_type = "battery:Cell"


        self.context= {
                        "schema":"https://schema.org/",
                        "":"https://raw.githubusercontent.com/BIG-MAP/BattINFO/master/context.json",
                        "emmo": "https://w3id.org/emmo#",
                        "echem": "https://w3id.org/emmo/domain/electrochemistry#",
                        "battery": "https://w3id.org/emmo/domain/battery#",
                        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                        "hasConstituent": "emmo:hasConstituent",


                        # "hasNumericalData": "emmo:hasNumericalData",
                        # "hasStringData": "emmo:hasStringData",
                        # "value": "emmo:hasQuantityValue",
                        # "unit": "emmo:hasReferenceUnit",
                        # "label": "skos:prefLabel"

                        # "skos": "http://www.w3.org/2004/02/skos/core#",
                        # "bkb": "https://w3id.org/emmo/domain/battery_knowledge_base#",
                        # "qudt": "http://qudt.org/vocab/unit/",
                    }

    def setup_linked_data_dict(self, model_id, model_name):

        model_label = "{} model".format(model_name)
        id = ""
        model_type = "battery:{}Model".format(model_name)

        dict = {
            "@context": self.context,
        
            self.universe_label:{
                self.hasModel:{
                    "label": model_label,
                    "@type": model_type,
                    self.hasQuantitativeProperty: db_helper.get_model_parameters_as_dict(model_name)
                }
            }             
        }

        # dict = {
        #     "@context": self.context,
        
        #     self.id:id,
        #     self.type:["Dataset"],
        #     "schema:headline": headline,
        #     "battinfo:hasModel":{
        #         self.type: model_type,
        #         self.id: model_id,
        #         self.label: model_label,
                
        #         self.hasInput: db_helper.get_model_parameters_as_dict(model_id)
        #     }
        #     }             
        
        return dict

    def fill_sub_dict(self,dict,relation_dict_1, parameters,existence,relation_dict_2 = None,relation_par=None):
        parameters = parameters.copy()
        if self.universe_label in dict:
            if relation_par:
                if existence == "new":
                    dict[self.universe_label][relation_dict_1] = parameters[relation_par]
                elif existence == "existing":
                    dict[self.universe_label][relation_dict_1] += parameters[relation_par]
            else:
                if existence == "new":
                    dict[self.universe_label][relation_dict_1] = parameters
                elif existence == "existing":
                    dict[self.universe_label][relation_dict_1] += parameters
        else:
            if relation_par:
                if existence == "new":
                    if relation_dict_2:
                        dict[relation_dict_1][relation_dict_2] = parameters[relation_par]
                    else:
                        dict[relation_dict_1] = parameters[relation_par]
                elif existence == "existing":
                    if relation_dict_2:
                        dict[relation_dict_1][relation_dict_2] += parameters[relation_par]
                    else:
                        dict[relation_dict_1] += parameters[relation_par]
            else:
                if existence == "new":
                    if relation_dict_2:
                        dict[relation_dict_1][relation_dict_2] = parameters
                    else:
                        dict[relation_dict_1] = parameters

                elif existence == "existing":
                    dict[relation_dict_1] += parameters
        return dict
    
    def setup_sub_dict(self,dict=None,display_name=None, context_type=None, type=None, existence = None):
        
        if type:
            if type == "cell":
                dict = {
                    "label": self.cell_label,
                    "@type": self.cell_type
                }
        elif existence =="new":
            dict = {
                    "label": display_name,
                    "@type": context_type
                }
                

        else:
            dict["label"] = display_name
            dict["@type"] = context_type
        
        return dict
    
    def fill_linked_data_dict(self, user_input, content):
        user_input[self.universe_label][self.hasCell] = content

        return user_input


    def setup_parameter_struct(self, parameter,component_parameters=None, value = None):

        # st.cache_data.clear()

        try:

            if isinstance(parameter, NumericalParameter):
                
                formatted_value_dict = {
                    "@type": "emmo:Numerical",
                    self.hasNumericalData: parameter.selected_value
                }

            elif isinstance(parameter, StrParameter):
                
                formatted_value_dict = {
                    "@type": "emmo:String",
                    self.hasStringData: parameter.selected_value
                }

            elif isinstance(parameter, BooleanParameter):
                formatted_value_dict = {
                    "@type": "emmo:Boolean",
                    self.hasStringData: parameter.selected_value
                }
            elif isinstance(parameter, FunctionParameter):
                formatted_value_dict = {
                    "@type": "emmo:String",
                    self.hasStringData: parameter.selected_value
                }
            # else: 

            #     st.error("This instance of parameter is not handled: {}".format(parameter))

            parameter_details = {
                "label": parameter.name,
                "@type": parameter.context_type if parameter.context_type else "string",
                "value": formatted_value_dict
            }
            if isinstance(parameter, NumericalParameter):
                parameter_details["unit"] = {
                        "label": parameter.unit_name if parameter.unit_name else parameter.unit,
                        "symbol": parameter.unit,
                        "@type": "emmo:"+parameter.unit_name if parameter.unit_name else parameter.unit,
                    }
            component_parameters.append(parameter_details)
            return component_parameters
        
        except:
            
            category_parameters = []

            parameter_id, \
                        name, \
                        model_name, \
                        par_class, \
                        difficulty, \
                        template_id, \
                        context_type, \
                        context_type_iri, \
                        parameter_type, \
                        unit, \
                        unit_name, \
                        unit_iri, \
                        max_value, \
                        min_value, \
                        is_shown_to_user, \
                        description,  \
                        display_name = tuple(np.squeeze(parameter[0]))


            formatted_value_dict = value

        
            formatted_value_dict = {
                "@type": "emmo:Numerical",
                self.hasNumericalData: value
            }

            parameter_details = {
                "label": name,
                "@type": context_type,
                "value": formatted_value_dict
            }
            
            parameter_details["unit"] = {
                "label": unit_name,
                "symbol": unit,
                "@type": "emmo:"+unit_name
            }

            category_parameters.append(parameter_details)
            return category_parameters
            
        
    
    def get_relation(self, id, type):

        if type == "tab":
            context_type= db_helper.get_context_type_and_iri_by_id(id)
            
        elif type == "category":
            context_type = db_helper.get_categories_context_type_from_id(id)
        elif type == "component":
            context_type = db_helper.get_components_context_type_from_id(id)
        else:
            print("Error: The relation for type {} is non-existing.".format(type))

        relation = "has" + context_type.split(':')[1]
        return relation
        
    def fill_component_dict(self,component_parameters,existence, dict = None, relation = None):
        component_parameters = component_parameters.copy()
        if existence == "new":
            dict = {self.hasQuantitativeProperty: component_parameters}

        elif existence == "existing":
            if self.hasQuantitativeProperty in component_parameters:
                
                if self.hasQuantitativeProperty in dict:
                    dict[self.hasQuantitativeProperty] += component_parameters[self.hasQuantitativeProperty]
                elif relation in dict:
                    if self.hasQuantitativeProperty in dict[relation]:
                        dict[relation][self.hasQuantitativeProperty] += component_parameters[self.hasQuantitativeProperty]
                    else:
                        dict[relation][self.hasQuantitativeProperty] = component_parameters
                else:
                    if relation:
                        dict[relation] = component_parameters
                        
                    else:
                        dict[self.hasQuantitativeProperty] = component_parameters[self.hasQuantitativeProperty]
            else:
                
                dict[relation] = component_parameters

        return dict
    
    def change_numerical_value(self,dict, index, value):
        try:
            dict[index]["value"][self.hasNumericalData]=value
        except:
            dict[index]["value"]=value

        return dict
    
    def add_indicators_to_struct(self, dict, n_to_p, cell_mass, cell_cap, specific_cap_ne, specific_cap_pe, cap_ne,cap_pe):
        dict[self.universe_label][self.hasCell][self.hasBatteryCell][self.hasQuantitativeProperty] += n_to_p
        dict[self.universe_label][self.hasCell][self.hasBatteryCell][self.hasQuantitativeProperty] += cell_mass
        dict[self.universe_label][self.hasCell][self.hasBatteryCell][self.hasQuantitativeProperty] += cell_cap
        dict[self.universe_label][self.hasCell][self.hasElectrode][self.hasNegativeElectrode][self.hasNegativeElectrode][self.hasQuantitativeProperty] += specific_cap_ne
        dict[self.universe_label][self.hasCell][self.hasElectrode][self.hasPositiveElectrode][self.hasPositiveElectrode][self.hasQuantitativeProperty] += specific_cap_pe
        dict[self.universe_label][self.hasCell][self.hasElectrode][self.hasNegativeElectrode][self.hasActiveMaterial][self.hasQuantitativeProperty] += cap_ne
        dict[self.universe_label][self.hasCell][self.hasElectrode][self.hasPositiveElectrode][self.hasActiveMaterial][self.hasQuantitativeProperty] += cap_pe

        return dict