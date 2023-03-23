import os
from python.resources.db import db_handler
from update_templates import UpdateTemplates
from update_models import UpdateModels
from update_tabs import UpdateTabs
from update_categories import UpdateCategories
from update_all_parameter_sets import UpdateParameterSets


if __name__ == "__main__":
    # IF NEEDED Reset table to update template parameters' order
    # sql_template_parameter = db_handler.TemplateParameterHandler()
    # sql_template_parameter.drop_table(confirm=True)
    # os.system("db_model.py")

    # 1. Templates
    UpdateTemplates().execute_script()

    # 2. Models (depend on templates)
    UpdateModels().execute_script()

    # 3. Tabs (independent)
    UpdateTabs().execute_script()

    # 4. Categories (depend on templates and tabs)
    UpdateCategories().execute_script()

    # 5. Parameter sets (depend on templates and categories)
    UpdateParameterSets().execute_script()
