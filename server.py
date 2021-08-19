from typing import List, Optional
from fastapi import FastAPI
from db.MongoDB import MongoAPI
from helpers.StringFormatter import StringFormatter
from pydantic import BaseModel

api = FastAPI()
mongo = MongoAPI()


def convert_to_mongo_doc(record):
    return {
        "id": record.id,
        "task": record.task,
        "start": record.start,
        "end": record.end,
        "delta": record.delta
    }


class Record(BaseModel):
    id: int
    task: str
    start: str
    end: str
    delta: float


class BodyObject(BaseModel):
    id: str
    records: List[Record] = []


@api.get("/api")
def get_records():
    records = mongo.get_all_records()
    return {"status": 200, "data": records}


@api.get("/api/task/{task_id}")
def get_record(task_id: str):
    _id = StringFormatter.convert_underscore_to_slash(task_id)
    record = mongo.get_record_for_day(_id)
    return {"status": 200, "data": record}


@api.post("/api")
async def create_record(body: BodyObject):
    records = []
    for record in body.records:
        temp = convert_to_mongo_doc(record)
        records.append(temp)

    mongo.create_record_for_day(body.id, records)
    return {"status": 201, "data": []}


# TODO
@api.put("/api/task/{task_id}")
def update_record(task_id: str, put: BodyObject):
    mongo.update_record_for_day(put.id, put.records)
    return {"status": 200, "data": []}
