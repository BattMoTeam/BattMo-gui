import sys
import os

##############################
# Set page directory to base level to allow for module import from different folder
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
##############################

from app_scripts import app_access

"""
Important links between tables:

- a template has template_parameters
- a parameter has parameters
- a parameter refers to a template_parameter (which contains its metadata)

- a category pertains to a tab
- a category has an assigned default template

- a model can have custom templates for each category; if not, default template is used
- a model has model_parameters

"""

if __name__ == "__main__":

    con, cur = app_access.get_sqlite_con_and_cur()

    cur.execute("DROP TABLE parameter")
    cur.execute("DROP TABLE parameter_set")
    cur.execute("DROP TABLE template")
    cur.execute("DROP TABLE template_parameter")
    cur.execute("DROP TABLE model")
    # cur.execute("DROP TABLE model_parameter")
    cur.execute("DROP TABLE tab")
    cur.execute("DROP TABLE category")
    cur.execute("DROP TABLE component")
    cur.execute("DROP TABLE material")

    ########################################################
    #       parameter
    #       name, parameter_set_id, template_parameter_id, value
    ########################################################
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS parameter(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name VARCHAR(255) NOT NULL,
            parameter_set_id INT NOT NULL,
            template_parameter_id INT NOT NULL,
            value VARCHAR(255) DEFAULT NULL
            
        )
    """
    )

    ########################################################
    #       parameter_set
    #       name, category_id
    ########################################################
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS parameter_set(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name VARCHAR(40) NOT NULL,
            component_id INT DEFAULT NULL,
            material VARCHAR(40) DEFAULT NULL,
            model_name VARCHAR(255) DEFAULT NULL,
            material_id INTEGER DEFAULT NULL
            
        )
    """
    )

    ########################################################
    #       template
    #       name
    ########################################################
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS template(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name VARCHAR(255) NOT NULL
        )
    """
    )

    ########################################################
    #       template_parameter
    #       name, template_id, context_type, context_type_iri, type, unit, unit_name, unit_iri, max_value, min_value, is_shown_to_user, description
    ########################################################
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS template_parameter(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name VARCHAR(255) NOT NULL,
            model_name VARCHAR(255) DEFAULT NULL,
            par_class VARCHAR(40) DEFAULT NULL,
            difficulty VARCHAR(40) DEFAULT NULL,
            template_id INT NOT NULL,
            context_type VARCHAR(40) DEFAULT NULL,
            context_type_iri VARCHAR(40) DEFAULT NULL,
            type VARCHAR(40) DEFAULT NULL,
            unit VARCHAR(40) DEFAULT NULL,
            unit_name VARCHAR(40) DEFAULT NULL,
            unit_iri VARCHAR(40) DEFAULT NULL,
            max_value VARCHAR(255) DEFAULT NULL,
            min_value VARCHAR(255) DEFAULT NULL,
            is_shown_to_user BOOLEAN NOT NULL DEFAULT 1,
            description VARCHAR(255) NULL DEFAULT "",
            display_name VARCHAR(255) DEFAULT NULL
        )
    """
    )

    ########################################################
    #       model
    #       name, description
    ########################################################
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS model(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name VARCHAR(40) NOT NULL,
            model_name VARCHAR(255) DEFAULT NULL,
            is_shown_to_user BOOLEAN DEFAULT NULL,
            default_template VARCHAR(40) DEFAULT NULL,
            description VARCHAR(255) NULL DEFAULT ""
        )
    """
    )

    ########################################################
    #       model_parameter
    #       name, model_id, value, type, unit, unit_name, unit_iri, description
    ########################################################
    # cur.execute("""
    #     CREATE TABLE IF NOT EXISTS model_parameter(
    #         id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    #         name VARCHAR(255) NOT NULL,
    #         value VARCHAR(255) DEFAULT NULL,
    #         type VARCHAR(40) DEFAULT NULL,
    #         unit VARCHAR(40) DEFAULT NULL,
    #         unit_name VARCHAR(40) DEFAULT NULL,
    #         unit_iri VARCHAR(40) DEFAULT NULL,
    #         description VARCHAR(255) NULL DEFAULT ""
    #     )
    # """)

    ########################################################
    #       tab
    #       name, display_name, context_type, context_type_iri, description
    ########################################################
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tab(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name VARCHAR(40) NOT NULL,
            model_name VARCHAR(255) DEFAULT NULL,
            difficulty VARCHAR(40) DEFAULT NULL,
            display_name VARCHAR(40) NOT NULL,
            context_type VARCHAR(40) DEFAULT NULL,
            context_type_iri VARCHAR(40) DEFAULT NULL,
            description VARCHAR(255) NULL DEFAULT ""
        )
    """
    )

    ########################################################
    #       category
    #       name, context_type, context_type_iri, emmo_relation, display_name, tab_id, default_template_id, description
    ########################################################
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS category(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name VARCHAR(40) NOT NULL,
            model_name VARCHAR(255) DEFAULT NULL,
            difficulty VARCHAR(40) DEFAULT NULL,
            context_type VARCHAR(40) DEFAULT NULL,
            context_type_iri VARCHAR(40) DEFAULT NULL,
            emmo_relation VARCHAR(40) DEFAULT NULL,
            display_name VARCHAR(40) NOT NULL DEFAULT " ",
            tab_id INT NOT NULL,
            default_template_id INT NOT NULL,
            description VARCHAR(255) NULL DEFAULT ""
        )
    """
    )

    ########################################################
    #       component
    #       name, display_name, context_type, context_type_iri, description
    ########################################################
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS component(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name VARCHAR(40) NOT NULL,
            model_name VARCHAR(255) DEFAULT NULL,
            difficulty VARCHAR(40) DEFAULT NULL,
            material BOOLEAN DEFAULT NULL,
            default_template VARCHAR(40) DEFAULT NULL,
            display_name VARCHAR(40) NOT NULL,
            emmo_relation VARCHAR(40) DEFAULT NULL,
            category_id INT DEFAULT NULL,
            tab_id INT DEFAULT NULL,
            default_template_id INT NOT NULL,
            context_type VARCHAR(40) DEFAULT NULL,
            context_type_iri VARCHAR(40) DEFAULT NULL,
            description VARCHAR(255) NULL DEFAULT ""
        )
    """
    )
    ########################################################
    #       material
    #       name, model_name, difficulty, display_name, context_type, context_type_iri, description
    ########################################################
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS material(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name VARCHAR(40) NOT NULL,
            model_name VARCHAR(255) DEFAULT NULL,
            difficulty VARCHAR(40) DEFAULT NULL,
            is_shown_to_user BOOLEAN NOT NULL DEFAULT 1,
            reference_name VARCHAR(40) DEFAULT NULL,
            reference VARCHAR(40) DEFAULT NULL,
            reference_url VARCHAR(40) DEFAULT NULL,
            category_id INT DEFAULT NULL,
            display_name VARCHAR(40) NOT NULL,
            number_of_components INTEGER DEFAULT NULL,
            component_name_1 VARCHAR(40) DEFAULT NULL,
            component_name_2 VARCHAR(40) DEFAULT NULL,
            default_material BOOLEAN DEFAULT NULL,
            context_type VARCHAR(40) DEFAULT NULL,
            component_id_1 INT DEFAULT NULL,
            component_id_2 INT DEFAULT NULL,
            context_type_iri VARCHAR(40) DEFAULT NULL,
            description VARCHAR(255) NULL DEFAULT ""
        )
    """
    )

    data = cur.execute("""SELECT * FROM component""")
    print(data.description)
