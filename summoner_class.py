from functools import reduce
from api_requests import PersonalAPI
from db_requests import DB
from stats_class import Stats

roles_dict = {
    "MID": "Middle",
    "MIDDLE": "Middle",
    "TOP": "Top",
    "JUNGLE": "Jungle",
    "DUO_SUPPORT": "Support",
    "DUO_CARRY": "Carry"
}


class Summoner(object):
    def __init__(self, api: PersonalAPI, db: DB, region, name):
        self.region = region
        self.name = name
        try:
            (self.summonerId, self.name) = api.get_summoner_id_and_name(self.__dict__)
        except api.SummonerNotFound:
            print("Summoner named {} doesn't exist in {} region".format(self.name, self.region))
            return
        in_db = self._search_summoner(db)
        if not in_db:
            self.timestamp = 0
            self._add_summoner(db)
        else:
            self.timestamp = self._get_timestamp(db)
        self._get_matches(api, db)
        self._set_timestamp(db)

    def __str__(self):
        str_ = "Region: {}\nName: {}".format(self.region, self.name)
        return str_

    def _set_timestamp(self, db):
        self.__dict__['timestamp'] = db.get_max("matches", "timestamp", self._as_param_dict())
        if type(self.__dict__["timestamp"]) is int:
            self.__dict__["timestamp"] += 1
        else:
            self.__dict__["timestamp"] = 0
        db.update("summoners", [self.__dict__])

    def _get_timestamp(self, db):
        return db.get_data("summoners", self._as_param_dict())[0]['timestamp']

    def _as_param_dict(self):
        return {"summonerId": [self.summonerId], "region": [self.region]}

    def _search_summoner(self, db):
        sum_info = db.get_data("summoners", self._as_param_dict())
        if len(sum_info):
            return True
        else:
            return False

    def _add_summoner(self, db):
        db.insert("summoners", [self.__dict__])

    def _get_matches(self, api: PersonalAPI, db: DB):
        params = self.__dict__.copy()
        (params["seasons"], params["queues"]) = db.get_seasons_and_queues()
        riot_matches = api.get_matches_list(params)
        matches = []
        print("New matches:", len(riot_matches))
        if len(riot_matches):
            not_found = []
            cannot_analyse = []
            offmeta = []
            for riot_match in riot_matches:
                match = {
                    "summonerRegion": self.region,
                    "summonerId": self.summonerId,
                    "region": riot_match["region"].lower(),
                    "matchId": riot_match["matchId"],
                    "championId": riot_match["champion"],
                    "season": riot_match["season"],
                    "timestamp": riot_match["timestamp"],
                }

                if "role" not in riot_match or "lane" not in riot_match:
                    cannot_analyse.append(match)
                    continue

                try:
                    if riot_match["role"] in roles_dict:
                        role = roles_dict[riot_match["role"]]
                    else:
                        role = roles_dict[riot_match["lane"]]
                except:
                    print(match["championId"], riot_match["lane"], riot_match["role"])
                    offmeta.append(match)
                    continue

                match["role"] = role

                try:
                    match_stats = api.get_match_info(match)
                except api.MatchNotFound:
                    not_found.append(match)
                    continue
                match["winner"] = match_stats["winner"]
                match["kills"] = match_stats["kills"]
                match["deaths"] = match_stats["deaths"]
                match["assists"] = match_stats["assists"]
                matches.append(match)

            print("Processed:", len(matches))
            print("Not found:", len(not_found))
            print("Cannot analyse:", len(cannot_analyse))
            print("Offmeta:", len(offmeta))
            db.insert("matches", matches)

    def get_stats(self, db, roles):
        params = self._as_param_dict()
        params["role"] = roles
        matches = db.get_data("matches", params)
        stats = Stats(matches)
        print("ROLE(S):", reduce(lambda x, y: "{}, {}".format(x, y), roles))
        print("ROLE(S) STATS:")
        print(stats)

