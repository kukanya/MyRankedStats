from api_requests import PersonalAPI
from db_requests import DB
from functools import reduce


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
