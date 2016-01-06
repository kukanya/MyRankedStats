import sys
from api_requests import *
from match_class import Match

api_key = sys.argv[1]
my_api = PersonalAPI(api_key)

region = "euw"
sumName = "Ecatta"
seasons = "SEASON2015"
sumId = my_api.get_summoner_id(region, sumName)

champions_dict = my_api.get_champions_info(region)
riot_matches = my_api.get_rankeds_list(region, sumId, seasons)

matches = []
for riot_match in riot_matches:
    matches.append(Match(riot_match, champions_dict))

my_stats = {}
for match in matches:
    if match.role in my_stats:
        my_stats[match.role]["games_number"] += 1
        if match.champion in my_stats[match.role]:
            my_stats[match.role][match.champion]["games_number"] += 1
        else:
            my_stats[match.role][match.champion] = {}
            my_stats[match.role][match.champion]["games_number"] = 1
    else:
        my_stats[match.role] = {}
        my_stats[match.role]["games_number"] = 1

for role in my_stats:
    print("{}: {} games played".format(role, my_stats[role]["games_number"]))
