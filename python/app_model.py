#use fileinput to handle files
#use glob to list documents with certain extensions
#here link https://towardsdatascience.com/the-best-practice-of-reading-text-files-in-python-509b1d4f5a4

import os
import json


def get_tree(d, indent=0):
    
    tree = ""
    for key, value in d.items():
        tree += " " * indent + str(key) + "\n"
        if isinstance(value, dict):
            tree += get_tree(value, indent+2)
        else:
            tree += " " * (indent+2) + str(value) + "\n"
    return tree


#### HIERARCHY OF APP MODEL ####
### Parameter objects -> ParameterSet -> Model
### Enables an API in this way: app_model.pe["paramset_name"].set_value("param_name", param_value)

class NumbericalParameter:

    def __init__(self, default: float, val_min: float = None, val_max: float= None):
        self.default = default
        self.val_min = val_min
        self.val_max = val_max


class OptionsParameter:

    def __init__(self, default: str, options: list, multiple: bool = False):
        self.default = default
        self.options = options
        self.multuple = multiple
        self.input = None


class BooleanParameter:
    def __init__(self, default:bool = True):
        self.default = default




class ParameterSet:

    def __init__(self, key_param_pairs:dict):
        self.key_param_pairs = key_param_pairs

    @property
    def parameters(self):
        return self.key_param_pairs

    @property
    def parameter_names(self):
        return list(self.key_param_pairs.keys())


    def get_value(self, parameter_name:str):

        assert parameter_name in self.key_param_pairs.keys(), f"{parameter_name} not a parameter in this set. Try the .parameter_names property to see which parameters are available"
        return self.key_param_pairs[parameter_name].default




class AppModel:

    def __init__(self, pe: dict = {}, 
                        ne:dict= {}, 
                        elyte:dict= {}, 
                        cell:dict= {},  
                        sep:dict= {},
                        cycling:dict= {}):

        self.pe = pe
        self.ne = ne
        self.elyte = elyte
        self.cell = cell
        self.sep = sep
        self.cycling = cycling







class ParametersLoader:
    """Base class to load parameters from multiple sources, and transform them
    into parameter objects that can be interpreted by the GUI"""

    def __init__(self, location:str):
        
        self.location = location
        self.schema_at_location_is_compatible()
        self.load_from_location()




    def schema_at_location_is_compatible(self):
        """Method to verify that the information in self.location is compatible with the json schema set by this loader"""

        raise NotImplementedError("Base class cannot be used. This methods is overwriten by children classes")


    def load_from_location(self):
        """Get the parameters from self.location using a predefined json schema"""
        raise NotImplementedError("Base class cannot be used. This methods is overwriten by children classes")


    def conform_params_to_appmodel(self):
        """Conform parameters from json files into a common data model that will be used across the app"""
        raise NotImplementedError("Base class cannot be used. This methods is overwriten by children classes")






class LoaderJsons(ParametersLoader):
    """Loads the default parameters when stored in a directory in disk"""


    def schema_at_location_is_compatible(self):

        assert os.path.isdir(self.location), f"Directory {self.location} not found"


        self.expected_folder_structure = ["cell",
                                        "elyte",
                                        "ne",
                                        "pe",
                                        "sep",
                                        "cycling"]

        self.expected_folder_structure.sort()

        self.folder_structure_at_location = os.listdir(self.location)
        self.folder_structure_at_location.sort()


        assert self.expected_folder_structure == self.folder_structure_at_location, f"""Folder structure not compatible.
        Expected: {self.expected_folder_structure}
        Found: {self.folder_structure_at_location}"""



    def load_from_location(self):  

        self.parameters_dict = {}

        for category in self.expected_folder_structure:

            self.parameters_dict.update({category:{}})

            for param_set in os.listdir(self.location+"/"+category):

                param_set_name = param_set.rstrip(".json")

                with open(self.location+"/"+category + "/" + param_set) as jsonfile:
                    json_dict = json.load(jsonfile)
                    #Dont show parameters that are functions, which are specified as a nesting
                    self.parameters_dict[category][param_set_name] = {key:value for key, value in json_dict["Parameters"].items() if not isinstance(value, dict)}
        
    


    def from_values_to_param_objects(self, value):


        if isinstance(value, (int, float)):
            app_parameter = NumbericalParameter(default=value) 

        elif (isinstance(value, tuple)) & (len(value)==3):
            app_parameter = NumbericalParameter(default=value[0], val_min=value[1], val_max=value[2])

        elif isinstance(value, str):
            app_parameter = OptionsParameter(default=value, options=[value]) 

        elif isinstance(value, list):
            app_parameter = OptionsParameter(default=value[0], options=value)

        elif isinstance(value, bool):
            app_parameter = BooleanParameter(default=value)

        return app_parameter



        
    def conform_params_to_appmodel(self):

        app_model = AppModel()
        
        for category, parameter_sets in self.parameters_dict.items():

            for parameter_set, key_value_pairs in parameter_sets.items():

                key_param_pairs = {}    

                for key, value in key_value_pairs.items():
                    
                    app_parameter = self.from_values_to_param_objects(value)

                    key_param_pairs.update({key: app_parameter})



                if category=="cell":
                    app_model.cell.update({parameter_set: key_param_pairs})

                if category=="elyte":
                    app_model.elyte.update({parameter_set: key_param_pairs})

                if category=="ne":
                    app_model.ne.update({parameter_set: key_param_pairs})

                if category=="pe":
                    app_model.pe.update({parameter_set: key_param_pairs})

                if category=="sep":
                    app_model.sep.update({parameter_set: key_param_pairs})

                if category=="cycling":
                    app_model.cycling.update({parameter_set: key_param_pairs})

        return app_model