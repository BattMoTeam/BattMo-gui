import os
import sys

##############################
# Set page directory to base level to allow for module import from different folder
path_to_python_module = os.path.dirname(os.path.abspath(__file__))
os.chdir("..")
path_to_python_module = os.path.join(os.path.abspath(os.curdir), "BattMo-gui")
sys.path.insert(0, path_to_python_module)
##############################

from python.resources.db import db_handler, db_access

class UpdateMaterials:

    def __init__(self):
        self.sql_material = db_handler.MaterialHandler()
        self.sql_component = db_handler.ComponentHandler()
        self.sql_model = db_handler.ModelHandler()

    def get_resource_as_json(self):
        return db_access.get_json_from_path(
            db_access.get_path_to_materials()
        )
        
    def update_material_from_json(self, resource_file):
        """
        resource_file: {
            "materials": {
                "material_name_1": {
                    "component_name": "component_1",
                    "description": "this new component is used for this type of electrode,
                                    which will be displayed on component_1"
                },
                "material_name_2": {
                    "component_name": "component_2",
                    "display_name": "material 2",
                    "description": "this material exists but has new description"
                }
            }
        }
        """
        materials = resource_file.get("materials")
        assert materials is not None, "This input format is not handled"

        new_types = []
        updated_types = []
        # every item which is not updated will be deleted, so we don't keep useless items in db
        existing_ids_to_be_deleted = self.sql_material.get_all_ids()

        for material_name in materials:
            details = materials.get(material_name)
            number_of_components = details.get("number_of_components")
            model_name = details.get("model_name")


            if model_name == "p2d_p3d_p4d":
                model = "P2D"
                model_id = self.sql_model.get_model_id_from_model_name(model)
            if model_name == "p3d_p4d":
                model = "P3D"
                model_id = self.sql_model.get_model_id_from_model_name(model)
            if model_name == "p4d":
                model = "P4D"
                model_id = self.sql_model.get_model_id_from_model_name(model)
            

            if number_of_components == 2:

                component_name_1 = details.get("component_name_1")
                component_name_2 = details.get("component_name_2")
                component_id_1 = self.sql_component.get_id_from_name(component_name_1)
                component_id_2 = self.sql_component.get_id_from_name(component_name_2)
                
                if component_id_1 and component_id_2:

                    
                    model_name = details.get("model_name")
                    difficulty = details.get("difficulty")
                    reference_name = details.get("reference_name")
                    reference = details.get("reference")
                    reference_url = details.get("reference_url")
                    context_type = details.get("context_type")
                    context_type_iri = details.get("context_type_iri")
                    emmo_relation = details.get("emmo_relation")
                    description = details.get("description")
                    display_name = details.get("display_name")
                    number_of_components = details.get("number_of_components")
                    component_name_1 = details.get("component_name_1")
                    print(component_name_1)
                    component_name_2 = details.get("component_name_2")
                    default_material = int(details.get("default_material"))


                    material_id = self.sql_material.get_id_from_name(material_name)
                    if material_id:  # existing type
                        self.sql_material.update_by_id(
                            id=material_id,
                            columns_and_values={
                                "component_id_1": component_id_1,
                                "component_id_2": component_id_2,
                                "model_name": model_name,
                                "difficulty": difficulty,
                                "reference_name": reference_name,
                                "reference": reference,
                                "reference_url": reference_url,
                                "model_id": model_id,
                                "context_type": context_type,
                                "context_type_iri": context_type_iri,
                                "emmo_relation": emmo_relation,
                                "display_name": display_name,
                                "number_of_components": number_of_components,
                                "component_name_1": component_name_1,
                                "component_name_2": component_name_2,
                                "description": description,
                                "default_material": default_material
                            }
                        )
                        updated_types.append(material_name)
                        existing_ids_to_be_deleted.remove(material_id)

                    else:  # non-existing type, create it
                        self.sql_material.insert_value(
                            name=material_name,
                            component_id_1=component_id_1,
                            component_id_2=component_id_2,
                            model_name=model_name,
                            difficulty=difficulty,
                            reference_name = reference_name,
                            reference = reference,
                            reference_url = reference_url,
                            model_id = model_id,
                            context_type=context_type,
                            context_type_iri=context_type_iri,
                            emmo_relation=emmo_relation,
                            display_name=display_name,
                            number_of_components = number_of_components,
                            component_name_1 = component_name_1,
                            component_name_2 = component_name_2,
                            description=description,
                            default_material=default_material
                        )
                        new_types.append(material_name)
            if number_of_components == 1:

                component_name_1 = details.get("component_name_1")
                component_id_1 = self.sql_component.get_id_from_name(component_name_1)
            
                if component_id_1:
                    model_name = details.get("model_name")
                    difficulty = details.get("difficulty")
                    reference_name = details.get("reference_name")
                    reference = details.get("reference")
                    reference_url = details.get("reference_url")
                    context_type = details.get("context_type")
                    context_type_iri = details.get("context_type_iri")
                    emmo_relation = details.get("emmo_relation")
                    description = details.get("description")
                    display_name = details.get("display_name")
                    number_of_components = details.get("number_of_components")
                    component_name_1 = details.get("component_name_1")
                    default_material = details.get("default_material")


                    material_id = self.sql_material.get_id_from_name(material_name)
                    if material_id:  # existing type
                        self.sql_material.update_by_id(
                            id=material_id,
                            columns_and_values={
                                "component_id_1": component_id_1,
                                "model_name": model_name,
                                "difficulty": difficulty,
                                "reference_name": reference_name,
                                "reference": reference,
                                "reference_url": reference_url,
                                "model_id": model_id,
                                "context_type": context_type,
                                "context_type_iri": context_type_iri,
                                "emmo_relation": emmo_relation,
                                "display_name": display_name,
                                "number_of_components": number_of_components,
                                "component_name_1": component_name_1,
                                "description": description,
                                "default_material": default_material
                            }
                        )
                        updated_types.append(material_name)
                        existing_ids_to_be_deleted.remove(material_id)

                    else:  # non-existing type, create it
                        self.sql_material.insert_value(
                            name=material_name,
                            component_id_1=component_id_1,
                            model_name=model_name,
                            difficulty=difficulty,
                            reference_name = reference_name,
                            reference = reference,
                            reference_url = reference_url,
                            model_id = model_id,
                            context_type=context_type,
                            context_type_iri=context_type_iri,
                            emmo_relation=emmo_relation,
                            display_name=display_name,
                            number_of_components = number_of_components,
                            component_name_1 = component_name_1,
                            description=description,
                            default_material=default_material
                        )
                        new_types.append(material_name)
            else:
                print("component name = {} is not specified in the SQL table component".format(component_name_1))
                print("material {} has not be saved in db since component_name {} is not in db".format(material_name, component_name_1))

        # Delete unused types which remain in the sql table
        deleted_types = []
        for id_to_delete in existing_ids_to_be_deleted:
            deleted_types.append(self.sql_material.get_name_from_id(id_to_delete))
            self.sql_material.delete_by_id(id_to_delete)

        print("\n SQL table component is up to date according to the resource file materials.json")
        if updated_types:
            print(" Updated materials : ", updated_types)
        if new_types:
            print(" New materials: ", new_types)
        if deleted_types:
            print(" Deleted materials: ", deleted_types)

    def execute_script(self):
        return self.update_material_from_json(self.get_resource_as_json())


if __name__ == "__main__":
    UpdateMaterials().execute_script()