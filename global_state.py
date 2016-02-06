import sys
from api_requests import PersonalAPI
from db_requests import DB

api = PersonalAPI(sys.argv[1])
db = DB()
champions = {}
summoners = set()
