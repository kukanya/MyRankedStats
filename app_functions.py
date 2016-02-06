import global_state as glb
from summoner_class import Summoner


def update_champions_data():
    champions_dict = glb.api.get_champions_info()
    api_version = champions_dict["version"]
    db_version = glb.db.get_version()

    if db_version != api_version:
        api_champions_list = []
        for champ in champions_dict["champions"]:
            api_champions_list.append({
                "championId": int(champ),
                "name": champions_dict["champions"][champ]["name"],
                "title": champions_dict["champions"][champ]["title"]
            })
        api_champions_list.sort(key=lambda k: k['championId'])

        db_champions_list = glb.db.get_data("champions")
        db_champions_list.sort(key=lambda k: k['championId'])

        champions_update = list(filter(
                lambda c: c["championId"] in set(map(lambda co: co["championId"], db_champions_list)),
                api_champions_list))
        champions_insert = list(filter(
                lambda c: c["championId"] not in set(map(lambda co: co["championId"], db_champions_list)),
                api_champions_list))

        glb.db.update("champions", champions_update)
        glb.db.insert("champions", champions_insert)
        glb.db.set_version(api_version)

    glb.champions = champions_dict["champions"]


def initialize_summoners():
    for row in glb.db.get_data("summoners"):
        glb.summoners.add(Summoner(row))


def update_matches_list():
    for summoner in glb.summoners:
        print(summoner)
        summoner.update_matches()


def add_summoner(region, name):
    try:
        summoner = Summoner({"region": region, "name": name})
    except glb.api.SummonerNotFound:
        return
    if not summoner.in_db():
        summoner.add_to_db()
        print("Summoner {} is now tracked".format(summoner))
        summoner.update_matches()
        glb.summoners.add(summoner)
    else:
        print("Summoner {} is already tracked".format(summoner))

