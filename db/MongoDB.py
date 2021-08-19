from pymongo import MongoClient
from dotenv import dotenv_values
from helpers.StringFormatter import StringFormatter

config = dotenv_values(".env")
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


class MongoError:
    def __init__(self, error):
        self.error = error


class MongoPost:
    """
    Records has to be array of tasks record
    """
    def __init__(self, _id,  records):
        self.mongo_rep = {"_id": _id,  "records": records}


class MongoAPI:
    def __init__(self):
        self.collection = get_database()
        self.active_record = None

    def get_all_records(self):
        data = []
        records = self.collection.find()
        for item in records:
            data.append(item)
        return data

    def get_record_for_day(self, day):
        this = {"_id": day}
        record_day = self.collection.find_one(this)
        if record_day is None:
            return None
        else:
            # if the latest record is active then set  that record
            # as active record
            last = record_day["records"][-1]
            if "active" in last:
                is_active = last["active"]
                self.active_record = last if is_active is True else None

            # return record of day
            return record_day

    def create_record_for_day(self, day,  records):
        post = MongoPost(day,  records)
        self.collection.insert_one(post.mongo_rep)

    def update_record_for_day(self, day, records):
        existing = self.get_record_for_day(day)
        if existing is None:
            return MongoError("Record not found - update cancelled")
        else:
            self.collection.update_one({"_id": day}, {"$set": {"records": records}})