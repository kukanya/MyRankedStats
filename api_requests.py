from my_api_key import *

import json
from urllib.request import urlopen

API = "https://{}.api.pvp.net/api/lol/"


def url_response_as_json(region, query):
    response = urlopen(API.format(region)+query)
    str_res = response.read().decode()
    json_res = json.loads(str_res)
    return json_res


def get_summoner_id(region, summoner_name):
    summoner_info = url_response_as_json(
        region,
        "{}/v1.4/summoner/by-name/{}?api_key={}".format(region, summoner_name, api_key)
    )
    summoner_id = summoner_info[summoner_name.lower()]['id']
    return summoner_id


def get_rankeds_list(region, summoner_id, seasons):
    matches_dict = url_response_as_json(
        region,
        "{}/v2.2/matchlist/by-summoner/{}?rankedQueues=RANKED_SOLO_5x5&seasons={}&api_key={}".format(
            region, summoner_id, seasons, api_key)
    )
    matches = sorted(matches_dict["matches"], key=lambda k: k['matchId'])
    return matches


# def get_match_info(region, match_id):

def get_champions_info(region):
    champions_dict = url_response_as_json(
        "global",
        "static-data/{}/v1.2/champion?dataById=true&api_key={}".format(region, api_key)
    )
    return champions_dict["data"]
