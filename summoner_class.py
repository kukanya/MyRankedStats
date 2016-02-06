import global_state as glb
from match_class import Match


class Summoner(object):
    def __init__(self, summoner_dict):
        self.__dict__ = summoner_dict
        if "summonerId" not in summoner_dict:
            try:
                self._look_up()
            except glb.api.SummonerNotFound:
                raise
            self.timestamp = 0

    def __str__(self):
        str_ = "{} [{}]".format(self.name, self.region)
        return str_

    def _look_up(self):
        try:
            (self.summonerId, self.name) = glb.api.get_summoner_id_and_name(self.__dict__)
        except glb.api.SummonerNotFound:
            print("Summoner {} doesn't exist".format(self))
            raise

    def _set_timestamp(self):
        self.timestamp = glb.db.get_max("matches", "timestamp", self._as_param_dict())
        if type(self.timestamp) is int:
            self.timestamp += 1
        else:
            self.timestamp = 0
        glb.db.update("summoners", [self.__dict__])

    # def _get_timestamp(self):
    #     return glb.db.get_data("summoners", self._as_param_dict())[0]['timestamp']

    def _as_param_dict(self):
        return {"summonerId": [self.summonerId], "region": [self.region]}

    def in_db(self):
        sum_info = glb.db.get_data("summoners", self._as_param_dict())
        if len(sum_info):
            return True
        else:
            return False

    def add_to_db(self):
        glb.db.insert("summoners", [self.__dict__])

    def update_matches(self):
        params = self.__dict__.copy()
        (params["seasons"], params["queues"]) = glb.db.get_seasons_and_queues()
        raw_matches = glb.api.get_matches_list(params)
        matches = []
        print("New matches:", len(raw_matches))
        if len(raw_matches):
            not_found = []
            cannot_analyse = []
            offmeta = []
            opp_error = []
            for raw_match in raw_matches:
                try:
                    match = Match(self, raw_match)
                except Match.CannotAnalyse as err:
                    match = err.match
                    cannot_analyse.append(match)
                    continue
                except Match.NotFound as err:
                    match = err.match
                    not_found.append(match)
                    continue
                except Match.OffMeta as err:
                    match = err.match
                    offmeta.append(match)
                except Match.OpponentError as err:
                    match = err.match
                    opp_error.append(match)

                matches.append(match)
            print("Processed:", len(matches))
            print("Not found:", len(not_found))
            print("Cannot analyse:", len(cannot_analyse))
            print("Offmeta:", len(offmeta))
            print("Opponent error:", len(opp_error))
            glb.db.insert("matches", list(map(lambda m: m.__dict__, matches)))
            self._set_timestamp()

    # def get_stats(self, db, roles):
    #     params = self._as_param_dict()
    #     params["role"] = roles
    #     matches = db.get_data("matches", params)
    #     stats = FullStats(matches)
    #     print("ROLE(S):", reduce(lambda x, y: "{}, {}".format(x, y), roles))
    #     print("ROLE(S) STATS:")
    #     print(stats)

