from python.db import db_connect
con, cur = db_connect.get_sqlite_con_and_cur()


########################################################
#       parameter  (name, value, value_type, parameter_set_id, is_shown_to_user)
########################################################
cur.execute("""
    CREATE TABLE IF NOT EXISTS parameter(
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        name VARCHAR(255) NOT NULL,
        value VARCHAR(255) NOT NULL,
        value_type VARCHAR(40) NOT NULL,
        parameter_set_id INT NOT NULL,
        is_shown_to_user TINYINT NOT NULL DEFAULT 1
    )
""")


########################################################
#       parameter_set  (name, category_id, headers_id)
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
#       category  (name, description)
########################################################
cur.execute("""
    CREATE TABLE IF NOT EXISTS category(
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        name VARCHAR(40) NOT NULL,
        description VARCHAR(255) NOT NULL DEFAULT ""
    )
""")


########################################################
#       parameter_set_header  (doi, description)
########################################################
cur.execute("""
    CREATE TABLE IF NOT EXISTS parameter_set_header(
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        doi VARCHAR(40) NOT NULL,
        description VARCHAR(255) NOT NULL
    )
""")
