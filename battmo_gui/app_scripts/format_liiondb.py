import pandas as pd
import streamlit as st
import requests
import json
import sys
import os
import traceback
import ast
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app_scripts import app_access
from database import db_handler

class RetrieveAndFormatLiionDB:
    def __init__(self):

        self.liiondb_api_url = "http://liiondb_api:5000/"

    
    def create_liiondb_data_file(self):

        components = ["Negative electrode Active material", "Positive electrode Active material", "Electrolyte", "Separator"]

        try:
            data_df = pd.DataFrame()
            for component in components:
                liiondb_materials = self.retrieve_liiondb_data(component)
                liiondb_materials_filtered = self.filter_liiondb_data(liiondb_materials, component)
                liiondb_materials_renamed = self.rename_liiondb_data(liiondb_materials_filtered, component)
                liiondb_materials_prepared = self.format_liion_data(liiondb_materials_renamed)
                liiondb_materials_validated = self.validate_liion_data(liiondb_materials_prepared, component)

                data_df = pd.concat([data_df, liiondb_materials_validated], ignore_index=True)
            
            data_df_json = data_df.to_json()

            with open(app_access.get_path_to_liiondb_data(), 'w') as f:
                json.dump(data_df_json,f)

            liiondb = True

            return liiondb, data_df

        except Exception as e:
            print("Warning: the creation of the liiondb data file resulted in an error.")
            print(str(e))
            traceback.print_exc()
            liiondb = False 

            return liiondb, components

    @st.cache_data
    def retrieve_liiondb_data(_self,component):

        """
        retrieves and organizes the following data in a pandas dataframe:
        - material
        - paper_tag
        - doi
        - parameter_name
        - parameter_symbol
        - raw_data
        - unit_output
        - unit_input
        - parameter_count (number of parameters within the material dataset)
        - material (paper_tag)
        
        """
        response = requests.post(_self.liiondb_api_url, data=component).json()

        response_dict = json.loads(response)
        response_pd = pd.DataFrame(response_dict)
        response_pd['material_paper_tag'] = response_pd['material'] + ' (' + response_pd['paper_tag'] + ') '
        response_pd['parameter_count'] = response_pd.groupby(['material', 'paper_tag'])['parameter'].transform('nunique')

        return response_pd

    @st.cache_data
    def filter_liiondb_data(_self, materials, component):

        wanted_parameters = {
            "Negative electrode Active material": ["electronic conductivity", "half cell ocv", "maximum concentration","particle surface area per unit volume", "particle radius", "minimum soc stoichiometry", "maximum soc stoichiometry"], 
            "Positive electrode Active material": ["electronic conductivity", "half cell ocv", "maximum concentration","particle surface area per unit volume", "particle radius", "minimum soc stoichiometry", "maximum soc stoichiometry"], 
            "Electrolyte":["ionic conductivity", "diffusion coefficient","transference number"], 
            "Separator": ["bruggeman exponent", "porosity"]
        }


        if component == "Negative electrode Active material" or component == "Positive electrode Active material":
            # Filter the DataFrame to keep only the rows where the 'parameter' column matches any value in the parameter_names list
            filtered_df = materials[materials['parameter'].isin(wanted_parameters[component])]
            # Filter out the Chen2020 dataset
            filtered_df = filtered_df[~(filtered_df['paper_tag'] == 'Chen2020')]
            # Filter out the parameter that have 'see function' as raw data
            filtered_df = filtered_df[~(filtered_df['raw_data'] == 'see function')]
            # Filter out the datasets that don't include a 'half cell ocv' parameter
            ocv_df = filtered_df[filtered_df['parameter'] == 'half cell ocv']
            valid_paper_tags = ocv_df['paper_tag'].unique()
            filtered_df = filtered_df[filtered_df['paper_tag'].isin(valid_paper_tags)]

            filtered_df = filtered_df[filtered_df['parameter_count'] >= 5]

        elif component == "Electrolyte":

            # Filter out the Chen2020 dataset
            filtered_df = materials[~(materials['paper_tag'] == 'Chen2020')]
            # Filter out the parameter that have 'see function' as raw data
            filtered_df = filtered_df[~(filtered_df['raw_data'] == 'see function')]
            # Filter out the datasets that don't include a 'diffusion coefficient' and 'condictivity' parameter
            diffusion_df = filtered_df[filtered_df['parameter'] == 'diffusion coefficient']
            diffusion_paper_tags = set(diffusion_df['paper_tag'].unique())
            conductivity_df = filtered_df[filtered_df['parameter'] == 'ionic conductivity']
            conductivity_paper_tags = set(conductivity_df['paper_tag'].unique())
            valid_paper_tags = diffusion_paper_tags.intersection(conductivity_paper_tags)
            filtered_df = filtered_df[filtered_df['paper_tag'].isin(valid_paper_tags)]
            
            # Filter out the material datasets that have less then a certain count of parameters
            filtered_df = filtered_df[filtered_df['parameter_count'] >= 2]

        else:
            
            # Filter the DataFrame to keep only the rows where the 'parameter' column matches any value in the parameter_names list
            filtered_df = materials[materials['parameter'].isin(wanted_parameters[component])]      
            # Filter out the Chen2020 dataset
            filtered_df = filtered_df[~(filtered_df['paper_tag'] == 'Chen2020')]

            # Filter out the parameter that have 'see function' as raw data
            filtered_df = filtered_df[~(filtered_df['raw_data'] == 'see function')]
            filtered_df = filtered_df[filtered_df['parameter_count'] >= 2]


        return filtered_df
    
    @st.cache_data
    def rename_liiondb_data(_self, materials, component):

        if component == "Negative electrode Active material" or component == "Positive electrode Active material":

            # Use the rename() method to change the column name
            materials.loc[materials['parameter'] == 'electronic conductivity', 'parameter'] = 'Electronic conductivity'
            materials.loc[materials['parameter'] == 'half cell ocv', 'parameter'] = 'Open circuit potential'
            materials.loc[materials['parameter'] == 'maximum concentration', 'parameter'] = 'Maximum concentration'
            materials.loc[materials['parameter'] == 'particle surface area per unit volume', 'parameter'] = 'Volumetric surface area'
            materials.loc[materials['parameter'] == 'particle radius', 'parameter'] = 'Particle radius'
            materials.loc[materials['parameter'] == 'minimum soc stoichiometry', 'parameter'] = 'Minimum soc stoichiometry'
            materials.loc[materials['parameter'] == 'maximum soc stoichiometry', 'parameter'] = 'Maximum soc stoichiometry'

        elif component == "Electrolyte":
        
            # Use the rename() method to change the column name
            materials.loc[materials['parameter'] == 'ionic conductivity', 'parameter'] = 'Conductivity'
            materials.loc[materials['parameter'] == 'diffusion coefficient', 'parameter'] = 'Diffusion coefficient'
            materials.loc[materials['parameter'] == 'transference number', 'parameter'] = 'Charge carrier transference number'

        else:

            # Use the rename() method to change the column name
            materials.loc[materials['parameter'] == 'porosity', 'parameter'] = 'Porosity'
            materials.loc[materials['parameter'] == 'bruggeman exponent', 'parameter'] = 'Bruggeman exponent'

        return materials
    
    @st.cache_data
    def parse_raw_data(_self,raw_data):

        try:
            # Remove outer curly braces
            data_string = raw_data[2:-2]

            # Split string into individual tuple strings
            tuple_strings = data_string.split("},{")

            # Parse each tuple string into a tuple of floats
            data_array = np.transpose(np.array([(float(tuple_str.split(",")[0]), float(tuple_str.split(",")[1])) for tuple_str in tuple_strings]))
                
            N = len(data_array[0,:])

            data_x = np.zeros(N)
            data_y = np.zeros(N)
            for i in range(N):
                data_x[i] = data_array[0,i]
                data_y[i] = data_array[1,i]

            if len(data_x) == 1:
                dic = {
                    "data_x": data_x[0],
                    "data_y": data_y[0]
                }
            else:
                dic = {
                    "data_x": list(data_x),
                    "data_y": list(data_y)
                }

            return dic
        except:
            if isinstance(raw_data, str):
                raw_data = ast.literal_eval(raw_data)

            return raw_data

    @st.cache_data
    def categorize_raw_data(_self,raw_data):
        try: 
            # Attempt to parse the raw_data string to a Python object
            parsed_data = ast.literal_eval(raw_data) 

            if isinstance(parsed_data, (int, float)):
                return 'constant'
            else: 
                print("wrong parse")
        except:
            dict = _self.parse_raw_data(raw_data)
            data_y = dict["data_y"]
            if isinstance(data_y, list):
                    return 'tabular'
            elif isinstance(data_y, (int, float)):
                return 'constant'
    
        return 'unknown'
    
    @st.cache_data
    def format_liion_data(_self, materials):

        materials['data_type'] = materials['raw_data'].apply(_self.categorize_raw_data)

        materials['raw_data'] = materials['raw_data'].apply(_self.parse_raw_data)

        

        #     with open("json.json", 'w') as f:
        #         json.dump(dict,f)

        return materials
    
    @st.cache_data
    def is_letter_in_string(_self, symbol, string):
        return symbol in string
    
    @st.cache_data
    def to_unicode_expr(_self,liiondb_unit):
        # Replace Unicode superscripts and middle dot with equivalent plain text expressions

        superscript_dict = {
            '0': '\u2070', '1': '\u00b9', '2': '\u00b2', '3': '\u00b3', '4': '\u2074',
            '5': '\u2075', '6': '\u2076', '7': '\u2077', '8': '\u2078', '9': '\u2079',
            '-': '\u207b', '+': '\u207a', '^': '', ')': '\u207e', "*": "\u00b7", 
        }
        if liiondb_unit == "1/m":
            liiondb_unit = "m\u00b2m\u207b\u00b3"
        elif liiondb_unit == "none":
            liiondb_unit = "1"
        else:
            for symbol in superscript_dict:
                symbol_in_unit = _self.is_letter_in_string(symbol, liiondb_unit)
                if symbol_in_unit:
                    liiondb_unit = liiondb_unit.replace(symbol, superscript_dict[symbol])
                    

        return liiondb_unit

    @st.cache_data
    def are_units_equal(_self,unit1_str, unit2_str):
        expr1 = unit1_str
        expr2 = _self.to_unicode_expr(unit2_str)
        
        return expr1 == expr2

    @st.cache_data
    def validate_liion_data(_self, materials, component):

        # List all parameter names in the liiondb dataframe
        parameter_names = materials['parameter'].unique().tolist()
        parameter_names = tuple(parameter_names)
        # Retrieve template parameter data from BattMo gui database
        sql = db_handler.TemplateParameterHandler()
        for name in parameter_names:
            parameter_meta_data = sql.get_all_by_display_name(name)
            if parameter_meta_data:
                _,name,_,_,_,_,context_type,context_type_iri,type,unit,unit_name,unit_iri,max_value,min_value,_,_,display_name = parameter_meta_data

                for index,row in materials.iterrows():
                    if row['parameter'] == display_name:
                        if type=='float' or type=='int':
                            if materials.at[index,'data_type'] == 'tabular':
                                raw_data = materials.at[index, 'raw_data']
                                data = np.mean(raw_data.get("data_y"))
                                materials.at[index, 'raw_data'] = data

                            liiondb_unit = materials.at[index,'units_output']

                            equal_units = _self.are_units_equal(unit,liiondb_unit)

                            if equal_units:
                                # Adding the ontology data to the table
                                materials.at[index, 'context_type_iri'] = context_type_iri
                                materials.at[index, 'units_output'] = unit
                                materials.at[index, 'unit_iri'] = unit_iri


                                # st.write("unit = ", unit)
                                # st.write("liiondb_unit = ",liiondb_unit)
                                # st.write("parsed liiondb_unit = ", _self.to_unicode_expr(liiondb_unit))
                                # st.write("are the units the same?", _self.are_units_equal(unit,liiondb_unit))

                            else:
                                materials = materials.drop(index)
                        if type == "function":
                            if materials.at[index,'data_type'] == 'constant':
                                paper_tag = materials.at[index, 'paper_tag']
                                materials = materials[materials['paper_tag'] != paper_tag]
                            else:
                                # Adding the ontology data to the table
                                materials.at[index, 'context_type_iri'] = context_type_iri
                                materials.at[index, 'units_output'] = unit
                                materials.at[index, 'unit_iri'] = unit_iri
           
            else:
                materials = materials[materials['parameter'] != name]

        return materials