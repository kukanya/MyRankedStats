from api_requests import PersonalAPI
from db_requests import DB
from functools import reduce

roles_dict = {
    "MID": "Middle",
    "MIDDLE": "Middle",
    "TOP": "Top",
    "JUNGLE": "Jungle",
    "DUO_SUPPORT": "Support",
    "DUO_CARRY": "Carry"
}


def process_champions_data(api: PersonalAPI, db: DB):
    champions_dict = api.get_champions_info()
    db_version = db.get_version()
    api_version = champions_dict["version"]
    if db_version != api_version:
        champions_new = []
        for champ in champions_dict["champions"]:
            champions_new.append({
                "championId": int(champ),
                "name": champions_dict["champions"][champ]["name"],
                "title": champions_dict["champions"][champ]["title"]
            })
        champions_new.sort(key=lambda k: k['championId'])
        champions_old = db.get_data("champions")
        champions_old.sort(key=lambda k: k['championId'])
        champions_update = list(filter(
                lambda c: c["championId"] in set(map(lambda co: co["championId"], champions_old)), champions_new))
        champions_insert = list(filter(
                lambda c: c["championId"] not in set(map(lambda co: co["championId"], champions_old)), champions_new))
        db.update("champions", champions_update)
        db.insert("champions", champions_insert)
        db.set_version(api_version)


def process_matches_data(api: PersonalAPI, db: DB, target: dict):
    riot_matches = api.get_matches_list(target)
    matches = []
    for match in riot_matches:
        match_stats = api.get_match_info(target, match["matchId"])
        if match["role"] in roles_dict:
            role = roles_dict[match["role"]]
        else:
            role = roles_dict[match["lane"]]
        matches.append({
            "matchId": match["matchId"],
            "season": match["season"],
            "championId": match["champion"],
            "role": role,
            "winner": match_stats["winner"],
            "kills": match_stats["kills"],
            "deaths": match_stats["deaths"],
            "assists": match_stats["assists"]
        })
def get_stats(db: DB, params={}):
    matches = db.get_data("matches", params)
    if len(params):
        print(reduce(lambda x, y: "{}, {}".format(x, y), map(lambda p: "{} = {}".format(p, params[p]), params)))
    print(len(matches), "games played: ", end="")
    wins = reduce(lambda x, y: x+y, map(lambda m: m["winner"], matches))
    print(wins, "wins,", len(matches)-wins, "losses")
    print("{0:.0f}% win rate".format(wins/len(matches)*100))
    kills = reduce(lambda x, y: x+y, map(lambda m: m["kills"], matches))
    deaths = reduce(lambda x, y: x+y, map(lambda m: m["deaths"], matches))
    assists = reduce(lambda x, y: x+y, map(lambda m: m["assists"], matches))
    print("KDA: {0:.2f}".format((kills+assists)/deaths))

# if __name__ == '__main__':
#     db = DB()
#     get_stats(db, {"championId": [267]})
