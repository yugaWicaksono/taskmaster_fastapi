from fastapi import Security, Depends, FastAPI, HTTPException
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader, APIKey
from db.MongoDB import MongoAPI
from helpers.StringFormatter import StringFormatter
from interface.body import BodyObject

from starlette.status import HTTP_403_FORBIDDEN
from starlette.responses import RedirectResponse, JSONResponse

from decouple import config

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


# START OF THE SERVER DEFINITION

"""
Only using header for now
"""
API_KEY = config("API_KEY")
API_KEY_NAME = config("API_KEY_NAME")

# api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
# api_key_cookie = APIKeyCookie(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


# noinspection PyShadowingNames
async def get_api_key(
        # api_key_query: str = Security(api_key_query),
        api_key_header: str = Security(api_key_header),
        # api_key_cookie: str = Security(api_key_cookie),
):
    """
    Check the header for existence of api key
    :param api_key_header: header with api key
    :return: api key header
    """
    if api_key_header == API_KEY:
        return api_key_header
    # if api_key_query == API_KEY:
    #     return api_key_query
    # elif api_key_cookie == API_KEY:
    #     return api_key_cookie
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )


# Keys are now saved serverside and has to be fetch before connection can be established
@api.post("/api/auth")
async def get_keys():
    connected = mongo.get_connection()
    return {"status": 200, "connected": connected}


# TODO add check of jwt here
@api.get("/api/connection")
async def get_connection():
    connected = mongo.get_connection()
    return {"status": 200, "connected": connected}


@api.get("/api/tasks")
async def get_records(api_key: APIKey = Depends(get_api_key)):
    records = mongo.get_all_records()
    return {"status": 200, "data": records}


@api.get("/api/tasks/{date_id}")
async def get_record(date_id: str, api_key: APIKey = Depends(get_api_key)):
    correct_day = StringFormatter.convert_underscore_to_slash(date_id)
    record = mongo.get_record_for_day(correct_day)
    return {"status": 200, "data": record}


@api.post("/api/tasks")
async def create_record(body: BodyObject, api_key: APIKey = Depends(get_api_key)):
    records = convert_records(body.records)
    mongo.create_record_for_day(body.id, records)
    return {"status": 201, "data": []}


@api.put("/api/tasks/{date_id}")
async def update_record(date_id: str, put: BodyObject, api_key: APIKey = Depends(get_api_key)):
    correct_day = StringFormatter.convert_underscore_to_slash(date_id)
    records = convert_records(put.records)
    mongo.update_record_for_day(correct_day, records)
    return {"status": 200, "data": []}
