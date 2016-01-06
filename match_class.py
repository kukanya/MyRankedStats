roles_dict = {
    "MID": "Middle",
    "MIDDLE": "Middle",
    "TOP": "Top",
    "JUNGLE": "Jungle",
    "DUO_SUPPORT": "Support",
    "DUO_CARRY": "Carry"
}


class Match:
    def __init__(self, riot_match: dict, champion_dict):
        self.matchId = riot_match["matchId"]
        self.championId = riot_match["champion"]
        self.champion = champion_dict[str(self.championId)]["name"]
        if riot_match["role"] in roles_dict:
            self.role = roles_dict[riot_match["role"]]
        else:
            self.role = roles_dict[riot_match["lane"]]

    def print(self):
        print(', '.join("%s: %s" % item for item in vars(self).items()))
