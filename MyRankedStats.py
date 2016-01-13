import sys
from app_functions import *
from summoner_class import Summoner

api_key = sys.argv[1]
api = PersonalAPI(api_key)
db = DB()

summoner = Summoner(api, db, "euw", "wulgrimm")
print(summoner)

# process_champions_data(api, db)

# if __name__ == '__main__':
#     get_role_stats(db, ["Support"])
