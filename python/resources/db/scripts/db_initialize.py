from python.resources.db import db_connect

con, cur = db_connect.get_sqlite_con_and_cur()


########################################################
#       parameter
#       name, value, type, unit_name, unit_dimension, max_value, min_value, parameter_set_id, is_shown_to_user, description
########################################################
cur.execute("""
    CREATE TABLE IF NOT EXISTS parameter(
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        name VARCHAR(255) NOT NULL,
        parameter_set_id INT NOT NULL,
        value VARCHAR(255) DEFAULT NULL,
        type VARCHAR(40) DEFAULT NULL,
        unit_name VARCHAR(40) DEFAULT NULL,
        unit_dimension VARCHAR(40) DEFAULT NULL,
        max_value VARCHAR(255) DEFAULT NULL,
        min_value VARCHAR(255) DEFAULT NULL,
        is_shown_to_user TINYINT NOT NULL DEFAULT 1,
        description VARCHAR(255) NULL DEFAULT ""
    )
""")


########################################################
#       parameter_set
#       name, category_id, header_id
########################################################
cur.execute("""
    CREATE TABLE IF NOT EXISTS parameter_set(
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        name VARCHAR(40) NOT NULL,
        category_id INT NOT NULL,
        header_id INT NOT NULL
    )
""")


########################################################
#       category
#       name, tab_id, description
########################################################
cur.execute("""
    CREATE TABLE IF NOT EXISTS category(
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        name VARCHAR(40) NOT NULL,
        tab_id INT NOT NULL,
        description VARCHAR(255) NULL DEFAULT ""
    )
""")


########################################################
#       tab
#       name, display_name, description
########################################################
cur.execute("""
    CREATE TABLE IF NOT EXISTS tab(
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        name VARCHAR(40) NOT NULL,
        display_name VARCHAR(40) NOT NULL,
        description VARCHAR(255) NULL DEFAULT ""
    )
""")


########################################################
#       parameter_set_header
#       doi, description
########################################################
cur.execute("""
    CREATE TABLE IF NOT EXISTS parameter_set_header(
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        doi VARCHAR(40) NOT NULL,
        description VARCHAR(255) NULL DEFAULT ""
    )
""")
