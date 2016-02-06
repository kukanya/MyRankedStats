from functools import reduce
from api_requests import PersonalAPI
from db_requests import DB
from stats_class import FullStats
import app_functions

class Summoner(object):
    def __init__(self, api: PersonalAPI, db: DB, region, name):
        self.region = region
        self.name = name

        try:
            (self.summonerId, self.name) = api.get_summoner_id_and_name(self.__dict__)
        except api.SummonerNotFound:
            print("Summoner named {} doesn't exist in {} region".format(self.name, self.region))
            return
        print(self)
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
            opp_error = []
            for riot_match in riot_matches:
                match = {
                    "summonerRegion": self.region,
                    "summonerId": self.summonerId
                }
                try:
                    app_functions.process_match_data(api, match, riot_match)
                except app_functions.CannotAnalyse:
                    cannot_analyse.append(match)
                    continue
                except app_functions.OffMeta:
                    offmeta.append(match)
                    continue
                except app_functions.NotFound:
                    not_found.append(match)
                    continue
                except app_functions.OpponentError:
                    opp_error.append(match)

                matches.append(match)

            print("Processed:", len(matches))
            print("Not found:", len(not_found))
            print("Cannot analyse:", len(cannot_analyse))
            print("Offmeta:", len(offmeta))
            print("Opponent error:", len(opp_error))
            db.insert("matches", matches)

    def get_stats(self, db, roles):
        params = self._as_param_dict()
        params["role"] = roles
        matches = db.get_data("matches", params)
        stats = FullStats(matches)
        print("ROLE(S):", reduce(lambda x, y: "{}, {}".format(x, y), roles))
        print("ROLE(S) STATS:")
        print(stats)

