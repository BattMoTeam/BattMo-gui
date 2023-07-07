from update_templates import UpdateTemplates
from update_models import UpdateModels
from update_tabs import UpdateTabs
from update_categories import UpdateCategories
from update_all_parameter_sets import UpdateParameterSets



"""
Update all db tables, according to the information stored in the different json files.
Those files are located in the directory python/resources/db/resources
"""

if __name__ == "__main__":
    # IF NEEDED, uncomment following lines to reset table, in order to update template parameters' order
    #
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
