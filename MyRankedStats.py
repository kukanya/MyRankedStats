import sys
from api_requests import PersonalAPI
from db_requests import DB
from match_class import Match

api_key = sys.argv[1]
api = PersonalAPI(api_key)
db = DB()

target = {
    "region": "euw",
    "summoner_name": "Ecatta",
    "seasons": "SEASON2015",
}
(target["summoner_id"], target["summoner_name"]) = api.get_summoner_id_and_name(target)


def process_champions_data(api: PersonalAPI, db: DB):
    champions_dict = api.get_champions_info(target)
    champions = {}
    for champ in champions_dict:
        champions[champ] = {
            "name": champions_dict[champ]["name"],
            "title": champions_dict[champ]["title"]
        }
    print(champions)
    db.refill_champions_table(champions)


process_champions_data(api, db)
# riot_matches = api.get_rankeds_list(target)
#
# matches = []
# for riot_match in riot_matches:
#     matches.append(Match(riot_match, champions_dict))
#
# my_stats = {}
# for match in matches:
#     if match.role in my_stats:
#         my_stats[match.role]["games_number"] += 1
#         if match.champion in my_stats[match.role]:
#             my_stats[match.role][match.champion]["games_number"] += 1
#         else:
#             my_stats[match.role][match.champion] = {}
#             my_stats[match.role][match.champion]["games_number"] = 1
#     else:
#         my_stats[match.role] = {}
#         my_stats[match.role]["games_number"] = 1
#
# for role in my_stats:
#     print("{}: {} games played".format(role, my_stats[role]["games_number"]))

# if __name__ == '__main__':
