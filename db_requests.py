import pymysql


class DB(object):
    def __init__(self):
        self.connection = pymysql.connect(host='localhost', port=3306, user='root', passwd='', db='MyRankedStats')
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.cursor.close()
        self.connection.close()

    def refill_champions_table(self, champions):
        self.cursor.execute("DELETE FROM champions;")
        for champ_id in champions:
            self.cursor.execute("INSERT INTO champions VALUES ({}, \"{}\", \"{}\");".format(
                    champ_id, champions[champ_id]["name"], champions[champ_id]["title"])
            )
            self.connection.commit()
