from api_requests import PersonalAPI
from db_requests import DB

roles_dict = {
    "MID": "Middle",
    "MIDDLE": "Middle",
    "TOP": "Top",
    "JUNGLE": "Jungle",
    "DUO_SUPPORT": "Support",
    "DUO_CARRY": "Carry"
}


def process_champions_data(api: PersonalAPI, db: DB, target: dict):
    champions_dict = api.get_champions_info(target)
    db_version = db.get_version()
    api_version = champions_dict["version"]
    if db_version != api_version:
        champions = []
        for champ in champions_dict["champions"]:
            champions.append({
                "championId": champ,
                "name": champions_dict["champions"][champ]["name"],
                "title": champions_dict["champions"][champ]["title"]
            })
        champions.sort(key=lambda k: k['championId'])
        db.clear_table("matches")
        db.refill_table("champions", champions)
        db.set_version(api_version)


def process_matches_data(api: PersonalAPI, db: DB, target: dict):
    riot_matches = api.get_matches_list(target)
    matches = []
    for match in riot_matches:
        if match["role"] in roles_dict:
            role = roles_dict[match["role"]]
        else:
            role = roles_dict[match["lane"]]
        matches.append({
            "matchId": match["matchId"],
            "season": match["season"],
            "championId": match["champion"],
            "role": role
        })
    db.refill_table("matches", matches)
