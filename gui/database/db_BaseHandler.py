import os
import sys
import streamlit as st
from threading import Lock

db_lock = Lock()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app_scripts import app_access


class BaseHandler:
    """
    Base class for all handlers (every handler refers to a precise table, this one is common to all)
    """

    def __init__(self):
        self._table_name = ""
        self._columns = ""
        assert False, "must be overridden"

    def insert_value(self, **kwargs):
        assert False, "must be overridden"

    def _insert_value_query(self, columns_and_values):
        assert columns_and_values, "must specify columns_and_values arg"
        columns = []
        values = []
        for column in columns_and_values:
            value = columns_and_values.get(column)

            if value is not None:
                columns.append(column)
                values.append(value)

        query = "INSERT INTO {} ({}) VALUES ({})".format(
            self._table_name,
            # column,
            ", ".join(columns),
            ", ".join(["?"] * len(values)),
        )

        # Convert values to strings
        string_values = [str(val) for val in values]
        with db_lock:
            con, cur = app_access.get_sqlite_con_and_cur()
            try:

                cur.execute(query, tuple(string_values))
            finally:
                cur.close()
                con.commit()
                con.close()
            return cur.lastrowid

    def thread_safe_db_access(_self, query, params=None, fetch=None):
        with db_lock:
            con, cur = None, None
            try:
                con, cur = app_access.get_sqlite_con_and_cur()
                if params:
                    cur.execute(query, params)
                else:
                    cur.execute(query)

                if fetch == "fetchall":
                    results = cur.fetchall()
                elif fetch == "fetchone":
                    results = cur.fetchone()
                else:
                    results = None

                return results

            except Exception as e:
                st.write("Error during database operation: %s", str(e))
                raise

            finally:
                # if cur:
                #     cur.close()
                if con:
                    con.commit()
                    # con.close()

    def _create_index(_self, index_name, table_name, columns):
        if isinstance(columns, (list, tuple)):
            columns = ", ".join(columns)
        query = """
            CREATE INDEX IF NOT EXISTS {} ON {} ({})
            """.format(
            index_name, table_name, columns
        )
        return _self.thread_safe_db_access(query)

    def select(_self, values, where=None, like=None, params=None):
        if where:
            if like:
                query = """
                    SELECT %s FROM %s WHERE %s LIKE %s
                """ % (
                    values,
                    _self._table_name,
                    where,
                    like,
                )
            else:
                query = """
                    SELECT %s FROM %s WHERE %s
                """ % (
                    values,
                    _self._table_name,
                    where,
                )
        else:
            query = """
                SELECT %s FROM %s 
            """ % (
                values,
                _self._table_name,
            )
        return _self.thread_safe_db_access(query, fetch="fetchall", params=params)

    def select_one(_self, values, where=None, like=None):
        if where:
            if like:
                query = """
                    SELECT %s FROM %s WHERE %s LIKE %s
                """ % (
                    values,
                    _self._table_name,
                    where,
                    like,
                )
            else:
                query = """
                    SELECT %s FROM %s WHERE %s
                """ % (
                    values,
                    _self._table_name,
                    where,
                )
        else:
            query = """
                SELECT %s FROM %s 
            """ % (
                _self._table_name,
                values,
            )
        return _self.thread_safe_db_access(query, fetch="fetchone")

    def select_by_id(self, id):
        res = self.select("*", "id=%d" % id)
        return res[0] if res else None

    def select_all(self):
        query = "SELECT * FROM %s" % self._table_name
        return self.thread_safe_db_access(query, fetch="fetchone")

    def select_shown_to_user(self):
        query = "SELECT * FROM %s WHERE show_to_user= %d" % (self._table_name, 1)
        return self.thread_safe_db_access(query, fetch="fetchone")

    def update_by_id(_self, id, columns_and_values):
        """
        columns_and_values: {"value": 1.1, "value_type": "float"}
        """
        sql_set = []
        for column in columns_and_values:

            value = columns_and_values.get(column)

            if value is not None:
                if isinstance(value, list):
                    value = ",".join(value)
                if isinstance(value, str):
                    sql_set.append("{} = '{}'".format(column, value))

                else:
                    sql_set.append("{} = {}".format(column, value))

        if bool(sql_set):  # else, nothing to update
            sql_query = "UPDATE {} SET {} WHERE id={}".format(
                _self._table_name, ", ".join(sql_set), id
            )
            _self.thread_safe_db_access(sql_query)

    def update(self, set, where=None):
        if where:
            query = """
                        UPDATE {} SET {} WHERE {}
                    """.format(
                self._table_name, set, where
            )
        else:
            query = """
                        UPDATE {} SET {}
                    """.format(
                self._table_name, set
            )
        self.thread_safe_db_access(query)

    def update_thread_safe(self, set, where=None):
        with db_lock:
            if where:
                query = """
                            UPDATE {} SET {} WHERE {}
                        """.format(
                    self._table_name, set, where
                )
            else:
                query = """
                            UPDATE {} SET {}
                        """.format(
                    self._table_name, set
                )
            self.thread_safe_db_access(query)

    def delete_by_id(self, id):
        self.thread_safe_db_access("DELETE FROM %s WHERE id=%d" % (self._table_name, id))

    def get_id_from_name(self, name):
        res = self.select_one(values="id", where="name='%s'" % name)
        return res[0] if res else None

    def get_name_from_id(self, id):
        res = self.select_one(values="name", where="id=%d" % id)
        return res[0] if res else None

    def get_all_ids(self):
        res = self.select(values="id")
        return [a[0] for a in res] if res else None

    def drop_table(self, other_table=None, confirm=False):
        if other_table:
            if confirm:
                self.thread_safe_db_access("DROP TABLE %s" % other_table)
            else:
                print("Please set confirm parameter as True to delete the table '%s'" % other_table)
        else:
            if confirm:
                self.thread_safe_db_access("DROP TABLE %s" % self._table_name)
            else:
                print(
                    "Please set confirm parameter as True to delete the table '%s'"
                    % self._table_name
                )

    def show_content(self):
        print("\n \n SQL Table - {}".format(self._table_name))
        for item in self.select_all():
            print("\n", item)

    def show_tables(self):
        for table in self.thread_safe_db_access(
            "SELECT name, sql FROM sqlite_schema", fetch="fetchall"
        ):
            name, structure = table
            print(name, "\n", structure, "\n")
