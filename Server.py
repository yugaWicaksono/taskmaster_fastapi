from fastapi import FastAPI
from db.MongoDB import get_database

api = FastAPI()
db = get_database()


@api.get("/")
def get_records():
    records = db.find()
    res = []
    for item in records:
        res.append(item)

    return {"data": res}


@api.get("/{id}")
def get_record(id):

    record = db.find_one({"_id": id})


def create_record():
    pass


def update_record():
    pass
