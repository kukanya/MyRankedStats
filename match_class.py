import global_state as glb

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


def identify_role(lane, role):
    key = "{} {}".format(lane, role)
    if key in roles_dict:
        return roles_dict[key]
    else:
        return "Offmeta"


class Match(object):

    class MatchException(BaseException):
        def __init__(self, match):
            self.match = match

    class CannotAnalyse(MatchException):
        def __init__(self, match):
            super().__init__(match)

    class OffMeta(MatchException):
        def __init__(self, match):
            super().__init__(match)

    class NotFound(MatchException):
        def __init__(self, match):
            super().__init__(match)

    class OpponentError(MatchException):
        def __init__(self, match, opp):
            super().__init__(match)
            self.opp = opp

    def _get_opponents(self, match_info, team):
        opps = tuple(map(lambda p: {"championId": p["championId"],
                                    "role": identify_role(p["timeline"]["lane"], p["timeline"]["role"])},
                         filter(lambda p: p["teamId"] != team, match_info["participants"])))
        if self.role != "Offmeta":
            t = tuple(map(lambda o: o["championId"], filter(lambda o: o["role"] == self.role, opps)))
            if len(t) != 1:
                raise self.OpponentError(self, "primary")
            self.primaryOpponent = t[0]
        else:
            self.primaryOpponent = None

        if self.role == "Support" or self.role == "Carry":
            if self.role == "Support":
                t = tuple(map(lambda o: o["championId"], filter(lambda o: o["role"] == "Carry", opps)))
            else:
                t = tuple(map(lambda o: o["championId"], filter(lambda o: o["role"] == "Support", opps)))
            if len(t) != 1:
                raise self.OpponentError(self, "secondary")
            self.secondaryOpponent = t[0]
        else:
            self.secondaryOpponent = None

    def __init__(self, summoner, raw_match):
        self.summonerRegion = summoner.region
        self.summonerId = summoner.summonerId
        self.region = raw_match["region"].lower()
        self.matchId = raw_match["matchId"]
        self.championId = raw_match["champion"]
        self.season = raw_match["season"]
        self.timestamp = raw_match["timestamp"]

        if "role" not in raw_match or "lane" not in raw_match:
            print("cannot analyse")
            raise self.CannotAnalyse(self)

        try:
            match_info = glb.api.get_match_info(self.__dict__)
        except glb.api.MatchNotFound:
            print("not found")
            raise self.NotFound(self)

        target_info = tuple(filter(lambda p: p["championId"] == self.championId, match_info["participants"]))[0]
        self.winner = target_info["stats"]["winner"]
        self.kills = target_info["stats"]["kills"]
        self.deaths = target_info["stats"]["deaths"]
        self.assists = target_info["stats"]["assists"]

        self.role = identify_role(raw_match["lane"], raw_match["role"])
        if self.role == "Offmeta":
            self.primaryOpponent = None
            self.secondaryOpponent = None
            print(glb.champions[str(self.championId)]["name"], raw_match["lane"], raw_match["role"])
            raise self.OffMeta(self)

        try:
            self._get_opponents(match_info, target_info["teamId"])
        except self.OpponentError as err:
            print("opp error")
            if err.opp == "primary":
                self.primaryOpponent = None
            self.secondaryOpponent = None
            raise

