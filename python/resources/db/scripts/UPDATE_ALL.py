from update_templates import UpdateTemplates
from update_models import UpdateModels
from update_tabs import UpdateTabs
from update_components import UpdateComponents
from update_materials import UpdateMaterials
from update_categories import UpdateCategories
from update_all_parameter_sets import UpdateParameterSets
import os

import python.resources.db.db_handler as db_handler
import python.resources.db.db_access as  db_access


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

    # 1. Models (independent)
    UpdateModels().execute_script()
    

    # 2. Templates (depends on models)
    UpdateTemplates().execute_script()

    

    # 3. Tabs (depends on models)
    UpdateTabs().execute_script()

    # 4. Categories (depend on models, templates and tabs)
    UpdateCategories().execute_script()

    # 5. Components (depend on models, templates and categories)
    UpdateComponents().execute_script()

    # 6. Materials (depend on models, components)
    UpdateMaterials().execute_script()

   

    # 5. Parameter sets (depend on templates and components)
    UpdateParameterSets().execute_script()

    

# Uncomment to see data in material table:

# con, cur = db_access.get_sqlite_con_and_cur()
# data=cur.execute('''SELECT * FROM material''')
# # Fetch all rows from the result
# data = cur.fetchall()

# # Check if there are columns to describe
# if cur.description:
#     # Print the column information
#     print("Column names:", [col[0] for col in cur.description])
# else:
#     print("No columns to describe (empty result set)")

# # Print the retrieved data
# for row in data:
#     print(row)
    
# # Don't forget to close the cursor and connection when done
# cur.close()
# con.close()