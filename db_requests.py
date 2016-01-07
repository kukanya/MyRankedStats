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

    # def get_matches(self, params: dict):
    #     if len(params):
    #         param_str = " WHERE " + reduce(lambda x, y: "{}, {}".format(x, y),
    #                                        map(lambda p: "{} = {}".format(p, sqlp(params[p])), params))
    #         print(param_str)
    #     #self.cursor.execute("SELECT * FROM matches")
#
# if __name__ == '__main__':
#     pass
