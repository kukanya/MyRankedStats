import sys
from app_functions import *
from summoner_class import Summoner

api_key = sys.argv[1]
api = PersonalAPI(api_key)
db = DB()

process_champions_data(api, db)

summoner = Summoner(api, db, "euw", "ecatta")
print(summoner)

summoner.get_stats(db, ["Support"])

