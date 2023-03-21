from . import db_access
con, cur = db_access.get_sqlite_con_and_cur()


class BaseHandler:
    def __init__(self):
        self._table_name = ""
        self._columns = ""
        assert False, "must be overridden"

    def insert_value(self, **kwargs):
        assert False, "must be overridden"

    def _insert_value_query(self, values, specify_columns=False, columns_and_values=None):
        if specify_columns:
            assert columns_and_values, "must specify columns_and_values arg"
            columns = []
            values = []
            for column in columns_and_values:
                value = columns_and_values.get(column)
                if value is not None:
                    columns.append(column)
                    values.append(value)

            query = "INSERT INTO {} ({}) VALUES {}".format(
                self._table_name,
                ", ".join(columns),
                tuple(values)
            )
        else:
            if len(values) == 1:
                query = "INSERT INTO {} ({}) VALUES ({})".format(self._table_name, self._columns, values[0])
            else:
                query = "INSERT INTO {} ({}) VALUES {}".format(self._table_name, self._columns, values)

        cur.execute(query)
        con.commit()
        return cur.lastrowid

    def select(self, values, where=None):
        if where:
            query = """
                SELECT %s FROM %s WHERE %s
            """ % (values, self._table_name, where)
        else:
            query = """
                SELECT %s FROM %s 
            """ % (values, self._table_name)
        return cur.execute(query).fetchall()

    def select_one(self, values, where=None):
        if where:
            query = """
                SELECT %s FROM %s WHERE %s
            """ % (values, self._table_name, where)
        else:
            query = """
                SELECT %s FROM %s 
            """ % (self._table_name, values)
        return cur.execute(query).fetchone()

    def select_by_id(self, id):
        res = self.select('*', 'id=%d' % id)
        return res[0] if res else None

    def select_all(self):
        return cur.execute("SELECT * FROM %s" % self._table_name).fetchall()

    def update_by_id(self, id, columns_and_values):
        """
        columns_and_values: {"value": 1.1, "value_type": "float"}
        """
        sql_set = []
        for column in columns_and_values:
            value = columns_and_values.get(column)
            if value is not None:
                if isinstance(value, str):
                    sql_set.append("{} = '{}'".format(column, value))
                else:
                    sql_set.append("{} = {}".format(column, value))

        if bool(sql_set):  # else, nothing to update
            sql_query = "UPDATE {} SET {} WHERE id={}".format(self._table_name, ', '.join(sql_set), id)
            cur.execute(sql_query)
            con.commit()

    def delete_by_id(self, id):
        cur.execute("DELETE FROM %s WHERE id=%d" % (self._table_name, id))
        con.commit()

    def get_id_from_name(self, name):
        res = self.select_one(
            values="id",
            where="name='%s'" % name
        )
        return res[0] if res else None

    def get_name_from_id(self, id):
        res = self.select_one(
            values="name",
            where="id=%d" % id
        )
        return res[0] if res else None

    def get_all_ids(self):
        res = self.select(values='id')
        return [a[0] for a in res]

    def drop_table(self, other_table=None, confirm=False):
        if other_table:
            if confirm:
                cur.execute("DROP TABLE %s" % other_table)
            else:
                print("Please set confirm parameter as True to delete the table '%s'" % other_table)
        else:
            if confirm:
                cur.execute("DROP TABLE %s" % self._table_name)
            else:
                print("Please set confirm parameter as True to delete the table '%s'" % self._table_name)

    def show_content(self):
        print("\n \n SQL Table - {}".format(self._table_name))
        for item in self.select_all():
            print("\n", item)

    def show_tables(self):
        for table in cur.execute("SELECT name, sql FROM sqlite_schema").fetchall():
            name, structure = table
            print(name, "\n", structure, "\n")
