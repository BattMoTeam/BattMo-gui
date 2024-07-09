import os
import sys

##############################
# Set page directory to base level to allow for module import from different folder
sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
)
##############################

from database import db_handler
from app_scripts import app_access


class CreateIndexes:

    def __init__(self):
        self.sql_material = db_handler.MaterialHandler()
        self.sql_component = db_handler.ComponentHandler()
        self.sql_model = db_handler.ModelHandler()
        self.sql_template_parameter = db_handler.TemplateParameterHandler()
        self.sql_tab = db_handler.TabHandler()
        self.sql_category = db_handler.CategoryHandler()
        self.sql_parameter_set = db_handler.ParameterSetHandler()
        self.sql_parameter = db_handler.ParameterHandler()

    def execute_script(self):

        self.sql_material.create_index(
            index_name="ind_mat_model_name", columns=("model_name", "component_id_1")
        )

        self.sql_parameter_set.create_index(
            index_name="ind_par_set_material_id", columns=("material_id")
        )

        self.sql_parameter.create_index(
            index_name="ind_par_parameter_set_id", columns=("parameter_set_id")
        )
        self.sql_template_parameter.create_index(
            index_name="ind_temp_par_id_model_name", columns=("id", "model_name")
        )

        self.sql_category.create_index(
            index_name="ind_cat_model_name", columns=("model_name")
        )
        self.sql_tab.create_index(
            index_name="ind_tab_model_name", columns=("model_name")
        )
        self.sql_component.create_index(
            index_name="ind_comp_model_name", columns=("model_name")
        )


if __name__ == "__main__":
    CreateIndexes().execute_script()
