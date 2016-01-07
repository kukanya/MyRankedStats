import pymysql
from functools import reduce


def sqlp(p):
    if type(p) is str:
        return "\"{}\"".format(p)
    else:
        return p


class DB(object):
    def __init__(self):
        self.connection = pymysql.connect(host='localhost', port=3306, user='root', passwd='', db='MyRankedStats')
        self.cursor = self.connection.cursor(pymysql.cursors.DictCursor)

    def __del__(self):
        self.cursor.close()
        self.connection.close()

    def get_version(self):
        self.cursor.execute("SELECT version FROM meta")
        return self.cursor.fetchone()["version"]

    def set_version(self, version):
        self.cursor.execute("UPDATE meta SET version = {}".format(sqlp(version)))
        self.connection.commit()

    def clear_table(self, table):
        self.cursor.execute("DELETE FROM {}".format(table))
        self.connection.commit()

    # Expects list of dictionaries as 'data' argument
    def refill_table(self, table, data: list):
        self.cursor.execute("DELETE FROM {}".format(table))
        self.cursor.execute(
                "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = {}".format(sqlp(table))
        )
        columns = tuple(map(lambda x: x["COLUMN_NAME"], self.cursor.fetchall()))
        for row in data:
            self.cursor.execute("INSERT INTO {} VALUES ({})".format(
                    table, reduce(lambda x, y: "{}, {}".format(x, y), map(lambda c: sqlp(row[c]), columns)))
            )
        self.connection.commit()

    # Expects dictionary with NON-EMPTY lists as values as 'params' argument
    def get_data(self, table, params={}):
        param_str = ""
        if len(params):
            param_str = " WHERE " + reduce(lambda x, y: "{} AND {}".format(x, y), map(lambda p: "({})".format(
                reduce(lambda x, y: "{} OR {}".format(x, y), map(lambda v: "{} = {}".format(p, sqlp(v)), params[p]))
            ), params))
        self.cursor.execute("SELECT * FROM {}".format(table)+param_str)
        return self.cursor.fetchall()

if __name__ == '__main__':
    db = DB()
    print(db.get_data("matches", {"role": ["Support", "Middle"], "championId": [267, 143]}))
