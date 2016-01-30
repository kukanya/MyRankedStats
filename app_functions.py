from api_requests import PersonalAPI
from db_requests import DB
from functools import reduce

roles_dict = {
    "MID SOLO": "Middle",
    "MIDDLE SOLO": "Middle",
    "TOP SOLO": "Top",
    "JUNGLE NONE": "Jungle",
    "BOT DUO_SUPPORT": "Support",
    "BOTTOM DUO_SUPPORT": "Support",
    "BOT DUO_CARRY": "Carry",
    "BOTTOM DUO_CARRY": "Carry"
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


def identify_role(lane, role):
    key = "{} {}".format(lane, role)
    if key in roles_dict:
        return roles_dict[key]
    else:
        return "Offmeta"


class CannotAnalyse(BaseException):
    pass


class OffMeta(BaseException):
    pass


class NotFound(BaseException):
    pass


class OpponentError(BaseException):
    def __init__(self, opp):
        self.opp = opp


def get_opponents(match_info, team, role):
    opps = tuple(map(lambda p: {"championId": p["championId"],
                                "role": identify_role(p["timeline"]["lane"], p["timeline"]["role"])},
                     filter(lambda p: p["teamId"] != team, match_info["participants"])))
    opponents = {}
    if role != "Offmeta":
        t = tuple(map(lambda o: o["championId"], filter(lambda o: o["role"] == role, opps)))
        if len(t) != 1:
            raise OpponentError("primary")
        opponents["primary"] = t[0]
    else:
        opponents["primary"] = None

    if role == "Support" or role == "Carry":
        if role == "Support":
            t = tuple(map(lambda o: o["championId"], filter(lambda o: o["role"] == "Carry", opps)))
        else:
            t = tuple(map(lambda o: o["championId"], filter(lambda o: o["role"] == "Support", opps)))
        if len(t) != 1:
            raise OpponentError("secondary")
        opponents["secondary"] = t[0]
    else:
        opponents["secondary"] = None

    return opponents


def process_match_data(api, match, raw_match):
    match["region"] = raw_match["region"].lower()
    match["matchId"] = raw_match["matchId"]
    match["championId"] = raw_match["champion"]
    match["season"] = raw_match["season"]
    match["timestamp"] = raw_match["timestamp"]

    if "role" not in raw_match or "lane" not in raw_match:
        raise CannotAnalyse()

    match["role"] = identify_role(raw_match["lane"], raw_match["role"])
    if match["role"] == "Offmeta":
        print(match["championId"], raw_match["lane"], raw_match["role"])
        raise OffMeta()

    try:
        match_info = api.get_match_info(match)
    except api.MatchNotFound:
        raise NotFound()

    target_info = tuple(filter(lambda p: p["championId"] == match["championId"],
                               match_info["participants"]))[0]
    match["winner"] = target_info["stats"]["winner"]
    match["kills"] = target_info["stats"]["kills"]
    match["deaths"] = target_info["stats"]["deaths"]
    match["assists"] = target_info["stats"]["assists"]
    try:
        opponents = get_opponents(match_info, target_info["teamId"], match["role"])
        match["primaryOpponent"] = opponents["primary"]
        match["secondaryOpponent"] = opponents["secondary"]
    except OpponentError as err:
        if err.opp == "primary":
            match["primaryOpponent"] = None
        match["secondaryOpponent"] = None
        raise

# def calc_champions_stats(matches):
#     champ_stats = []
#     for champ_id in set(map(lambda m: m["championId"], matches)):
#         champ_stats.append({
#             "championId": champ_id,
#             "stats": calc_basic_stats(list(filter(lambda m: m["championId"] == champ_id, matches)))
#         })
#     return champ_stats
#
#
# def get_role_stats(db: DB, roles: list):
#     matches = db.get_data("matches", {"role": roles})
#     stats = calc_basic_stats(matches)
#     stats["champions_stats"] = calc_champions_stats(matches)
#     print("ROLE(S):", reduce(lambda x, y: x+", "+y, roles))
#     print("ROLE(S) STATS:")
#     print_basic_stats(stats)
#     print("BY CHAMPION:")
#     for champ in stats["champions_stats"]:
#         print("championId:", champ["championId"])
#         print_basic_stats(champ["stats"])
