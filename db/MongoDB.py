from pymongo import MongoClient
from dotenv import dotenv_values

config = dotenv_values("../.env")
_user = config["USER"]
_pass = config["PASS"]
_db = config["DB"]
_collection = config["COLL"]
_host = config["HOST"]
URI = f"mongodb+srv://{_user}:{_pass}{_host}/{_db}?retryWrites=true&w=majority"


def get_database():
    try:
        client = MongoClient(URI)
        collection = client[_db][_collection]
        return collection
    except ConnectionError:
        raise ConnectionError('Cannot connect to the database')
