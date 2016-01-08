import sys
from app_functions import *
# from match_class import Match

api_key = sys.argv[1]
api = PersonalAPI(api_key)
db = DB()

target = {
    "region": "euw",
    "summoner_name": "Ecatta",
}
(target["summoner_id"], target["summoner_name"]) = api.get_summoner_id_and_name(target)

# process_champions_data(api, db)
# process_matches_data(api, db, target)

# if __name__ == '__main__':
