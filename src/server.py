from fastapi import Security, Depends, FastAPI, HTTPException, Response
from fastapi.security.api_key import APIKeyCookie, APIKeyHeader, APIKey
from db.MongoDB import MongoAPI
from helpers.StringFormatter import StringFormatter
from interface.body import BodyObject
from interface.access_key import AccessKey

# import crypt to verify signature
from helpers.crypt import CryptoHelper, SECRET

# response
import src.http_response as res

# errors
import src.error as error
from starlette.status import HTTP_403_FORBIDDEN

# get the decouple
from decouple import config

# import project detail
from project import VERSION

api = FastAPI()
mongo = MongoAPI()


def check_version(response: Response, version: str):
    if float(version) < VERSION:
        set_status_code(response, False, 400)
        return res.set_object(version=res.VERSION_WARNING)


def convert_to_mongo_doc(record) -> dict:
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
        "delta": record.delta,
        "platform": record.platform
    }


def convert_records(records) -> list:
    """
    Convert records from body to mongo documents
    :param records: Records receive from the req.body
    :return: list of mongo documents
    """
    _records = []
    for record in records:
        temp = convert_to_mongo_doc(record)
        _records.append(temp)
    return _records


# START OF THE SERVER DEFINITION

API_KEY = mongo.get_key() if not None else ""
API_KEY_NAME = config("API_KEY_NAME")

api_key_cookie = APIKeyCookie(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


# noinspection PyShadowingNames
async def get_api_key(
        api_key_header: str = Security(api_key_header),
        api_key_cookie: str = Security(api_key_cookie),
):
    """
    Check the header/cookie for existence of api key
    :param api_key_cookie: cookie with api key
    :param api_key_header: header with api key
    :return: api key header
    """
    if api_key_header == API_KEY:
        if CryptoHelper.verify_token(api_key_header, SECRET):
            return api_key_header
        else:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail=error.AUTH
            )
    elif api_key_cookie == API_KEY:
        if CryptoHelper.verify_token(api_key_cookie, SECRET):
            return api_key_header
        else:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail=error.AUTH
            )
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail=error.AUTH
        )


def set_status_code(response: Response, ok_condition, code: int):
    response.status_code = 200 if ok_condition else code


# Keys are now saved serverside and has to be fetch before connection can be established
@api.post("/api/{version}/auth/key")
async def get_key(version: str, body: AccessKey, response: Response):
    """
    Get the keys saved in database
    :return: dict with key
    """
    ver = check_version(response, version)
    if ver is not None:
        return ver

    key = mongo.get_client_key(body)

    if key is None:
        if mongo.isConnected:
            # assuming key is not found thus
            set_status_code(response, False, 400)
        else:
            # server is unavailable
            set_status_code(response, False, 503)
        return res.set_object(key=None)
    else:
        return res.set_object(key=key)


@api.get("/api/{version}/connection")
async def get_connection(version: str, response: Response):
    ver = check_version(response, version)
    if ver is not None:
        return ver
    else:
        connected = mongo.get_connection()
        set_status_code(response, connected, 503)
        return res.set_object(connected=connected)


@api.get("/api/{version}/tasks")
async def get_records(version: str, response: Response, api_key: APIKey = Depends(get_api_key)):
    ver = check_version(response, version)
    if ver is not None:
        return ver
    else:
        records = mongo.get_all_records()
        if records is None:
            set_status_code(response, False, 503)
        return res.set_data(records)


@api.get("/api/{version}/tasks/{date_id}")
async def get_record(version: str, date_id: str, response: Response, api_key: APIKey = Depends(get_api_key)):
    ver = check_version(response, version)
    if ver is not None:
        return ver
    else:
        correct_day = StringFormatter.convert_underscore_to_slash(date_id)
        record = mongo.get_record_for_day(correct_day)
        if record is None:
            set_status_code(response, False, 503)
        return res.set_data(record)


@api.get("/api/{version}/tasks/{date_id}/latest")
async def get_most_recent_record(version: str, date_id: str, response: Response,
                                 api_key: APIKey = Depends(get_api_key)):
    ver = check_version(response, version)
    if ver is not None:
        return ver
    else:
        correct_day = StringFormatter.convert_underscore_to_slash(date_id)
        record = mongo.get_record_for_day(correct_day)
        if record is None:
            set_status_code(response, False, 503)
        return res.set_data(record)


@api.post("/api/{version}/tasks")
async def create_record(version: str, body: BodyObject, response: Response, api_key: APIKey = Depends(get_api_key)):
    ver = check_version(response, version)
    if ver is not None:
        return ver
    else:
        records = convert_records(body.records)
        created = mongo.create_record_for_day(body.id, records)
        if created is None:
            set_status_code(response, False, 503)
            return res.FAILED_CREATE_UPDATE
        else:
            return created


@api.put("/api/{version}/tasks/{date_id}")
async def update_record(version: str, date_id: str, body: BodyObject, response: Response,
                        api_key: APIKey = Depends(get_api_key)):
    ver = check_version(response, version)
    if ver is not None:
        return ver
    else:
        correct_day = StringFormatter.convert_underscore_to_slash(date_id)
        records = convert_records(body.records)
        updated = mongo.update_record_for_day(correct_day, records)
        if updated is None:
            set_status_code(response, False, 503)
            return res.FAILED_CREATE_UPDATE
        else:
            return updated
