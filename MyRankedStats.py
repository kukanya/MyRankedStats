import sys
from app_functions import *

api_key = sys.argv[1]
api = PersonalAPI(api_key)
db = DB()

target = {
    "region": "euw",
    "summoner_name": "Wulgrimm",
}
(target["summoner_id"], target["summoner_name"]) = api.get_summoner_id_and_name(target)

print(target["summoner_id"])

# process_champions_data(api, db)
process_matches_data(api, db, target)

# if __name__ == '__main__':
#     get_role_stats(db, ["Support"])
