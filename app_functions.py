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
    print(len(riot_matches))
    for match in riot_matches:
        match_stats = api.get_match_info(match["region"].lower(), match["matchId"], match["champion"])
        print(match["champion"], match["lane"], match["role"])
        try:
            if match["role"] in roles_dict:
                role = roles_dict[match["role"]]
            else:
                role = roles_dict[match["lane"]]
        except:
            # print(match["champion"], match["lane"], match["role"])
            role = match["lane"]+":"+match["role"]
        matches.append({
            "matchId": match["matchId"],
            "season": match["season"],
            "timestamp": match["timestamp"],
            "championId": match["champion"],
            "role": role,
            "winner": match_stats["winner"],
            "kills": match_stats["kills"],
            "deaths": match_stats["deaths"],
            "assists": match_stats["assists"]
        })
    db.clear_table("matches")
    db.insert("matches", matches)


def sum_stat(stat, matches):
    return reduce(lambda x, y: x+y, map(lambda m: m[stat], matches))


def calc_kda(k, d, a):
    if d:
        return (k+a)/d
    else:
        return k+a


def calc_basic_stats(matches):
    stats = dict()
    stats["games"] = len(matches)
    stats["wins"] = sum_stat("winner", matches)
    stats["losses"] = stats["games"] - stats["wins"]
    stats["win_rate"] = stats["wins"]/stats["games"]*100
    stats["kills"] = sum_stat("kills", matches)
    stats["deaths"] = sum_stat("deaths", matches)
    stats["assists"] = sum_stat("assists", matches)
    stats["kda"] = calc_kda(stats["kills"], stats["deaths"], stats["assists"])
    stats["av_kills"] = stats["kills"]/stats["games"]
    stats["av_deaths"] = stats["deaths"]/stats["games"]
    stats["av_assists"] = stats["assists"]/stats["games"]
    return stats


def print_basic_stats(stats):
    print(stats["games"], "games played: ", end="")
    print(stats["wins"], "wins,", stats["losses"], "losses")
    print("{0:.0f}% win rate".format(stats["win_rate"]))
    print("KDA: {0:.2f}".format(stats["kda"]))
    print("Average K/D/A: {0:.1f}/".format(stats["av_kills"]) +
          "{0:.1f}/".format(stats["av_deaths"]) + "{0:.1f}".format(stats["av_assists"]))
    print("Total K/D/A: {}/{}/{}".format(stats["kills"], stats["deaths"], stats["assists"]))


def calc_champions_stats(matches):
    champ_stats = []
    for champ_id in set(map(lambda m: m["championId"], matches)):
        champ_stats.append({
            "championId": champ_id,
            "stats": calc_basic_stats(list(filter(lambda m: m["championId"] == champ_id, matches)))
        })
    return champ_stats


def get_role_stats(db: DB, roles: list):
    matches = db.get_data("matches", {"role": roles})
    stats = calc_basic_stats(matches)
    stats["champions_stats"] = calc_champions_stats(matches)
    print("ROLE(S):", reduce(lambda x, y: x+", "+y, roles))
    print("ROLE(S) STATS:")
    print_basic_stats(stats)
    print("BY CHAMPION:")
    for champ in stats["champions_stats"]:
        print("championId:", champ["championId"])
        print_basic_stats(champ["stats"])
