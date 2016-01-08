import json
from urllib.request import urlopen


class PersonalAPI:
    API = "https://{}.api.pvp.net/api/lol/"

    def __init__(self, api_key):
        self.api_key = api_key

    def url_response_as_json(self, region, query):
        while True:
            try:
                response = urlopen(self.API.format(region) + query)
                break
            except: pass
        str_res = response.read().decode()
        json_res = json.loads(str_res)
        return json_res

    def get_summoner_id_and_name(self, target: dict):
        summoner_info = self.url_response_as_json(
                target["region"],
                "{}/v1.4/summoner/by-name/{}?api_key={}".format(target["region"], target["summoner_name"], self.api_key)
        )
        summoner_id = summoner_info[target["summoner_name"].lower()]['id']
        summoner_name = summoner_info[target["summoner_name"].lower()]['name']
        return summoner_id, summoner_name

    def get_matches_list(self, target: dict):
        matches_dict = self.url_response_as_json(
                target["region"],
                "{}/v2.2/matchlist/by-summoner/{}?rankedQueues=RANKED_SOLO_5x5&api_key={}".format(
                        target["region"], target["summoner_id"], self.api_key)
        )
        matches = sorted(matches_dict["matches"], key=lambda k: k['matchId'])
        return matches

    def get_match_info(self, target: dict, match_id):
        all_match_info = self.url_response_as_json(
                target["region"],
                "{}/v2.2/match/{}?api_key={}".format(target["region"], match_id, self.api_key)
        )
        participant_id = tuple(filter(lambda p: p["player"]["summonerId"] == target["summoner_id"],
                                      all_match_info["participantIdentities"]))[0]["participantId"]
        target_info = tuple(filter(lambda p: p["participantId"] == participant_id,
                                   all_match_info["participants"]))[0]["stats"]
        return target_info


    def get_champions_info(self):
        champions_dict = self.url_response_as_json(
                "global",
                "static-data/euw/v1.2/champion?dataById=true&api_key={}".format(self.api_key)
        )
        return {"version": champions_dict["version"], "champions": champions_dict["data"]}
