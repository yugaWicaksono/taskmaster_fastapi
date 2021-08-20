from fastapi import FastAPI
from db.MongoDB import MongoAPI
from helpers.StringFormatter import StringFormatter
from interface.body import BodyObject

api = FastAPI()
mongo = MongoAPI()


def convert_to_mongo_doc(record):
    """
    Convert Record object back to dictionary to be sent to mongo
    :param record: record representation of task
    :return:  dictionary of task record suitable for mongo
    """
    return {
        "id": record.id,
        "task": record.task,
        "start": record.start,
        "end": record.end,
        "delta": record.delta
    }


def convert_records(records):
    _records = []
    for record in records:
        temp = convert_to_mongo_doc(record)
        _records.append(temp)
    return _records


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
    records = convert_records(body.records)
    mongo.create_record_for_day(body.id, records)
    return {"status": 201, "data": []}



@api.put("/api/task/{task_id}")
def update_record(task_id: str, put: BodyObject):
    records = convert_records(put.records)
    mongo.update_record_for_day(task_id, records)
    return {"status": 200, "data": []}
