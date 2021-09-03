from fastapi import Security, Depends, FastAPI, HTTPException, Response
from fastapi.security.api_key import APIKeyCookie, APIKeyHeader, APIKey
from db.MongoDB import MongoAPI
from helpers.string_formatter import StringFormatter
from interface.body import BodyObject
from interface.access_key import AccessKey
from helpers.crypt import CryptoHelper, SECRET  # import crypt to verify signature
import src.http_response as http_res  # response
import src.error as error  # errors
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
from decouple import config  # get the decouple for .env
from project import VERSION  # import project detail

api = FastAPI()
mongo = MongoAPI()

# START OF THE SERVER DEFINITION

API_KEY = mongo.get_key() if not None else ""
API_KEY_NAME = config("API_KEY_NAME")

api_key_cookie = APIKeyCookie(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def check_version(response: Response, version: str):
    """
    Check the version of the API

    :param response: response object to be send
    :param version: the API version
    :return: return the version or transform the response to send error
    """
    if version != VERSION:
        set_status_code(response, False, 400)
        # set the message in response
        return http_res.set_object(version=http_res.VERSION_WARNING)
    else:
        return VERSION


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
        "platform": record.platform,
        "notes": record.notes
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


# noinspection PyShadowingNames
async def get_api_key(
        p_header: str = Security(api_key_header),
        p_cookie: str = Security(api_key_cookie),
):
    """
    Check the header/cookie for existence of api key

    :param p_header: header with api key
    :param p_cookie: cookie with api key
    :return: api key header
    """
    if p_header == API_KEY:
        if CryptoHelper.verify_token(p_header, SECRET):
            return p_header
        else:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail=error.AUTH
            )
    elif p_cookie == API_KEY:
        if CryptoHelper.verify_token(p_cookie, SECRET):
            return p_cookie
        else:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail=error.AUTH
            )
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail=error.AUTH
        )


def set_status_code(response: Response, ok_condition, code: int):
    """
    Set the status code in the response object

    :param response: response object to be send to client
    :param ok_condition: Truthy condition to be evaluated
    :param code: the status code to be set
    :return: transform response with the new code
    """
    response.status_code = 200 if ok_condition else code


# Keys are now saved serverside and has to be fetch before connection can be established
@api.post("/api/{version}/auth/key")
async def get_key(version: str, body: AccessKey, response: Response):
    """
    Get the keys saved in database

    :return: dict with key
    """
    # check the version 
    ver = check_version(response, version)
    if ver is not VERSION:
        return ver

    key = mongo.get_client_key(body)

    if key is None:
        if mongo.isConnected:
            # assuming key is not found thus
            set_status_code(response, False, 400)
        else:
            # server is unavailable
            set_status_code(response, False, 503)
        return http_res.set_object(key=None)
    else:
        return http_res.set_object(key=key)


@api.get("/api/{version}/connection")
async def get_connection(version: str, response: Response):
    """
    Check if the database is connected

    :param version: version of the API to be evaluated
    :param response: response object to be send to client
    :return: return version or transform response
    """
    # check the version 
    ver = check_version(response, version)
    if ver is not VERSION:
        return ver
    else:
        connected = mongo.get_connection()
        set_status_code(response, connected, 503)
        return http_res.set_object(connected=connected)


@api.get("/api/{version}/day")
async def get_records(version: str, response: Response, api_key: APIKey = Depends(get_api_key)):
    """
    Get the records
    :param version: version of the API to be evaluated
    :param response: response object to be send to client
    :param api_key: api key to be evaluated
    :return: all records
    """

    # check the version 
    ver = check_version(response, version)
    if ver is not VERSION:
        return ver
    else:
        records = mongo.get_all_records()
        if records is None:
            set_status_code(response, False, 503)
        return http_res.set_data(records)


@api.get("/api/{version}/day/{date_id}")
async def get_record(version: str, date_id: str, response: Response, api_key: APIKey = Depends(get_api_key)):
    """
    Get the record of the day
    :param version: version of the API to be evaluated
    :param date_id: the date id to be fetch
    :param response: response object to be send to client
    :param api_key: api key to be evaluated
    :return: record of the day
    """
    # check the version 
    ver = check_version(response, version)
    if ver is not VERSION:
        return ver
    else:
        correct_day = StringFormatter.convert_underscore_to_slash(date_id)
        record = mongo.get_record_for_day(correct_day)
        if record is None:
            set_status_code(response, False, 400)
        return http_res.set_data(record)


@api.get("/api/{version}/day/{date_id}/latest")
async def get_most_recent_record(version: str, date_id: str, response: Response,
                                 api_key: APIKey = Depends(get_api_key)):
    """
    Get the most recent task

    :param version: version of the API to be evaluated
    :param date_id: the date id to be fetch
    :param response: response object to be send to client
    :param api_key: api key to be evaluated
    :return: the most recent task
    """

    # check the version 
    ver = check_version(response, version)
    if ver is not VERSION:
        return ver
    else:
        correct_day = StringFormatter.convert_underscore_to_slash(date_id)
        record = mongo.get_most_recent_record(correct_day)
        if record is None:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail=error.NOT_FOUND
            )

        return http_res.set_data(record)


@api.post("/api/{version}/day")
async def create_record(version: str, body: BodyObject, response: Response, api_key: APIKey = Depends(get_api_key)):
    """
    Create record of the day

    :param version: version of the API to be evaluated
    :param body: the body record object to be saved in the database
    :param response: response object to be send to client
    :param api_key: api key to be evaluated
    :return: message string
    """

    # check the version 
    ver = check_version(response, version)
    if ver is not VERSION:
        return ver
    else:
        records = convert_records(body.records)
        created = mongo.create_record_for_day(body.id, records)
        if created is None:
            set_status_code(response, False, 503)
            return http_res.SERVER_UNAVAILABLE
        elif created == http_res.FAILED_CREATE_UPDATE:
            set_status_code(response, False, 400)
            return created
        else:
            set_status_code(response, False, 201)
            return created


@api.put("/api/{version}/day/{date_id}")
async def update_record(version: str, date_id: str, body: BodyObject, response: Response,
                        api_key: APIKey = Depends(get_api_key)):
    """
    Update the record of the day

    :param version: version of the API to be evaluated
    :param date_id: the date id to be fetch
    :param response: response object to be send to client
    :param api_key: api key to be evaluated
    :return: message string
    """

    # check the version 
    ver = check_version(response, version)
    if ver is not VERSION:
        return ver
    else:
        correct_day = StringFormatter.convert_underscore_to_slash(date_id)
        records = convert_records(body.records)
        updated = mongo.update_record_for_day(correct_day, records)
        if updated is None:
            set_status_code(response, False, 503)
            return http_res.SERVER_UNAVAILABLE
        elif updated == http_res.FAILED_CREATE_UPDATE:
            set_status_code(response, False, 400)
            return updated
        else:
            set_status_code(response, True, 200)
            return updated


@api.delete("/api/{version}/day/{date_id}")
async def delete_record(version: str, date_id: str, response: Response,
                        api_key: APIKey = Depends(get_api_key)):
    """
    Delete the record for the day

    :param version: version of the API to be evaluated
    :param date_id: the date id to be fetch
    :param response: response object to be send to client
    :param api_key: api key to be evaluated
    :return: message string
    """

    # check the version
    ver = check_version(response, version)
    if ver is not VERSION:
        return ver
    else:
        correct_day = StringFormatter.convert_underscore_to_slash(date_id)
        deleted = mongo.delete_record_for_day(correct_day)
        if deleted is None:
            set_status_code(response, False, 503)
            return http_res.SERVER_UNAVAILABLE
        elif deleted == http_res.FAILED_DELETED_DAY:
            set_status_code(response, False, 400)
            return deleted
        else:
            set_status_code(response, True, 200)
            return deleted


@api.delete("/api/{version}/day/{date_id}/task/{task_id}")
async def delete_task_for_record(version: str, date_id: str, task_id: str, response: Response,
                                 api_key: APIKey = Depends(get_api_key)):
    """
    Delete the task for the day

    :param version: version of the API to be evaluated
    :param date_id: the date id to be fetch
    :param task_id: the task id to be deleted
    :param response: response object to be send to client
    :param api_key: api key to be evaluated
    :return:
    """

    # check the version
    ver = check_version(response, version)
    if ver is not VERSION:
        return ver
    else:
        correct_day = StringFormatter.convert_underscore_to_slash(date_id)
        deleted = mongo.delete_task(correct_day, int(task_id))
        if deleted is None:
            set_status_code(response, False, 503)
            return http_res.SERVER_UNAVAILABLE
        elif deleted == http_res.FAILED_DELETED_DAY:
            set_status_code(response, False, 400)
            return deleted
        elif deleted == http_res.FAILED_DELETED_TASK_NON:
            set_status_code(response, False, 404)
            return deleted
        else:
            set_status_code(response, True, 200)
            return deleted
