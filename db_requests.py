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

    def get_seasons_and_queues(self):
        self.cursor.execute("SELECT seasons, queues FROM meta")
        meta = self.cursor.fetchone()
        return meta["seasons"], meta["queues"]

    def clear_table(self, table):
        self.cursor.execute("TRUNCATE {}".format(table))
        self.connection.commit()

    def _get_primary_keys(self, table):
        self.cursor.execute("SHOW KEYS FROM {} WHERE Key_name = 'PRIMARY'".format(table))
        keys = set(map(lambda k: k["Column_name"], self.cursor.fetchall()))
        return keys

    def _get_columns(self, table):
        self.cursor.execute(
                "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = {}".format(sqlp(table))
        )
        columns = set(map(lambda x: x["COLUMN_NAME"], self.cursor.fetchall()))
        return columns

    # Expects list of dictionaries as 'data' argument
    def insert(self, table, data: list):
        columns = self._get_columns(table)
        for row in data:
            query = "INSERT INTO {} ({}) VALUES ({})".format(
                    table, reduce(lambda x, y: "{}, {}".format(x, y), columns),
                    reduce(lambda x, y: "{}, {}".format(x, y), map(lambda c: sqlp(row[c]), columns)))
            # print(query)
            self.cursor.execute(query)
        self.connection.commit()

    # Expects list of dictionaries as 'data' argument
    def update(self, table, data: list):
        keys = self._get_primary_keys(table)
        columns = self._get_columns(table)
        columns = columns - keys
        for row in data:
            query = "UPDATE {} SET {} WHERE {}".format(
                    table, reduce(lambda x, y: "{}, {}".format(x, y),
                                  map(lambda c: "{} = {}".format(c, sqlp(row[c])), columns)),
                    reduce(lambda x, y: "{} AND {}".format(x, y),
                           map(lambda c: "{} = {}".format(c, sqlp(row[c])), keys))
            )
            # print(query)
            self.cursor.execute(query)
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

    def get_max(self, table, column, params={}):
        param_str = ""
        if len(params):
            param_str = " WHERE " + reduce(lambda x, y: "{} AND {}".format(x, y), map(lambda p: "({})".format(
                reduce(lambda x, y: "{} OR {}".format(x, y), map(lambda v: "{} = {}".format(p, sqlp(v)), params[p]))
            ), params))
        self.cursor.execute("SELECT MAX({}) AS max FROM {}".format(column, table)+param_str)
        return self.cursor.fetchone()["max"]


# if __name__ == '__main__':
#     db = DB()
#     print(db.get_max("matches", "timestamp", {"summonerId": [21630703], "summonerRegion": ["euw"]}))
#     db.insert("matches", [{'winner': True, 'season': "S2014", 'timestamp': 8485888, 'region': "euw", 'deaths': 0,
#                            'matchId': 123123123, 'role': "Support", 'assists': 100, 'kills': 1, 'championId': 1}])
#     db.update("matches", [{'winner': True, 'season': "Sea2014", 'timestamp': 8485888, 'region': "euw", 'deaths': 0,
#                            'matchId': 123123123, 'role': "Support", 'assists': 100, 'kills': 1, 'championId': 1}])
