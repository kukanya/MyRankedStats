import json
from urllib.request import urlopen


class PersonalAPI:
    API = "https://{}.api.pvp.net/api/lol/"

    def __init__(self, api_key):
        self.api_key = api_key

    def url_response_as_json(self, region, query):
        response = urlopen(self.API.format(region)+query)
        str_res = response.read().decode()
        json_res = json.loads(str_res)
        return json_res

    def get_summoner_id(self, region, summoner_name):
        summoner_info = self.url_response_as_json(
            region,
            "{}/v1.4/summoner/by-name/{}?api_key={}".format(region, summoner_name, self.api_key)
        )
        summoner_id = summoner_info[summoner_name.lower()]['id']
        return summoner_id

    def get_rankeds_list(self, region, summoner_id, seasons):
        matches_dict = self.url_response_as_json(
            region,
            "{}/v2.2/matchlist/by-summoner/{}?rankedQueues=RANKED_SOLO_5x5&seasons={}&api_key={}".format(
                region, summoner_id, seasons, self.api_key)
        )
        matches = sorted(matches_dict["matches"], key=lambda k: k['matchId'])
        return matches

    # def get_match_info(self, region, match_id):

    def get_champions_info(self, region):
        champions_dict = self.url_response_as_json(
            "global",
            "static-data/{}/v1.2/champion?dataById=true&api_key={}".format(region, self.api_key)
        )
        return champions_dict["data"]
