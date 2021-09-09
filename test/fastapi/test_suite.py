import time

from fastapi.testclient import TestClient
from icecream import ic
from .src.server import api
from decouple import config
from .project import VERSION
import pytest
from httpx import AsyncClient, Headers


# temp storage to hold values during testing
class StorageTest:
    scenario = 1
    client = TestClient(api)
    base_path = "api"
    base_url = "http://localhost:8000"
    api_key = ""


# use this to pass value from one test to another
storage = StorageTest()


def parse_path(endpoint):
    """
    Parse endpoint to the url
    :param endpoint: the selected endpoint
    :return: parsed endpoint string
    """
    return f"{storage.base_path}/{VERSION}/{endpoint}"


@pytest.mark.asyncio
async def test_get_connection():
    """
    Test the connection end point
    :return: True if connected else False
    """
    async with AsyncClient(app=api, base_url=storage.base_url) as ac:
        res = await ac.get(parse_path("connection"))

    assert res.status_code == 200
    assert res.json() == {
        "connected": True
    }


@pytest.mark.asyncio
async def test_get_api_key():
    """
    Async test to get the api key
    :return: The api key
    """

    # body with client access token
    body = {config("TEST_TOKEN_KEY"): config("TEST_API_KEY")}

    # async request
    async with AsyncClient(app=api, base_url=storage.base_url) as ac:
        res = await ac.post(parse_path("auth/key"), json=body)

    # debug
    ic(res)
    ic(res.json())
    assert res.status_code == 200
    data = res.json()
    if "key" in data:
        assert type(data["key"]) == str
        assert len(data["key"]) > 10
        # Set this to the api key
        storage.api_key = data["key"]


@pytest.mark.asyncio
async def test_get_all_task():
    """
    Get all of task
    :return: None
    """
    headers = Headers({config("TEST_TOKEN_KEY"): storage.api_key})
    async with AsyncClient(app=api, base_url=storage.base_url) as ac:
        res = await ac.get(parse_path("day"), headers=headers)

    # debug
    ic(res)
    ic(res.json())
    assert res.status_code == 200
    data = res.json()

    if "_id" in data:
        assert type(data["_id"]) == str

    if "records" in data:
        assert type(data["records"]) == list
        assert len(data["records"]) > 0


@pytest.mark.asyncio
async def test_get_task_day():
    """
    Get all of task for the day
    :return: None
    """
    headers = Headers({config("TEST_TOKEN_KEY"): storage.api_key})
    async with AsyncClient(app=api, base_url=storage.base_url) as ac:
        res = await ac.get(parse_path("day/01_01_2020"), headers=headers)

    # debug
    ic(res)
    ic(res.json())
    assert res.status_code == 200
    data = res.json()

    if "_id" in data:
        assert type(data["_id"]) == str

    if "records" in data:
        assert type(data["records"]) == list
        assert len(data["records"]) > 0

    assert data == {
        "data": {
            "_id": "01/01/2020",
            "records": [
                {
                    "id": 1,
                    "task": "Unit test",
                    "start": "00:00:00",
                    "end": "12:00:00",
                    "delta": 12.0,
                    "platform": "Unit test",
                    "notes": "Unit testing"
                },
                {
                    "id": 2,
                    "task": "Unit test2",
                    "start": "12:00:00",
                    "end": "00:00:00",
                    "delta": 12.0,
                    "platform": "Unit test",
                    "notes": "Unit testing"
                }
            ]
        }
    }


@pytest.mark.asyncio
async def test_get_task_most_recent():
    """
    Get most recent task
    :return: None
    """
    headers = Headers({config("TEST_TOKEN_KEY"): storage.api_key})
    async with AsyncClient(app=api, base_url=storage.base_url) as ac:
        res = await ac.get(parse_path("day/01_01_2020/latest"), headers=headers)

    # debug
    ic(res)
    ic(res.json())
    assert res.status_code == 200
    data = res.json()

    if "_id" in data:
        assert type(data["_id"]) == str

    if "records" in data:
        assert type(data["records"]) == list
        assert len(data["records"]) > 0

    assert data == {
        "data":
            {
                "id": 2,
                "task": "Unit test2",
                "start": "12:00:00",
                "end": "00:00:00",
                "delta": 12.0,
                "platform": "Unit test",
                "notes": "Unit testing"
            }
    }


@pytest.mark.asyncio
async def test_create_new_day():
    """
    Test create a new day with task record
    :return: None
    """
    body = {
        "id": "01/01/2020",
        "records": [
            {
                "id": 1,
                "task": "Unit test",
                "start": "00:00:00",
                "end": "12:00:00",
                "delta": 12.0,
                "platform": "Unit test",
                "notes": "Unit testing"
            }
        ]
    }

    headers = Headers({config("TEST_TOKEN_KEY"): storage.api_key})

    # async request
    async with AsyncClient(app=api, base_url=storage.base_url) as ac:
        res = await ac.post(parse_path("day"), json=body, headers=headers)

    # debug
    ic(res)
    ic(res.json())
    assert res.status_code == 201
    data = res.json()
    if "message" in data:
        message = data["message"]
        assert type(message) == str
        assert message == "success"


@pytest.mark.asyncio
async def test_update_day():
    """
    Test update day
    :return: None
    """
    body = {
        "id": "01/01/2020",
        "records": [
            {
                "id": 1,
                "task": "Unit test",
                "start": "00:00:00",
                "end": "12:00:00",
                "delta": 12.0,
                "platform": "Unit test",
                "notes": "Unit testing"
            },
            {
                "id": 2,
                "task": "Unit test2",
                "start": "12:00:00",
                "end": "00:00:00",
                "delta": 12.0,
                "platform": "Unit test",
                "notes": "Unit testing"
            }
        ]
    }

    headers = Headers({config("TEST_TOKEN_KEY"): storage.api_key})

    # async request
    async with AsyncClient(app=api, base_url=storage.base_url) as ac:
        res = await ac.put(parse_path("day/01_01_2020"), json=body, headers=headers)

    # debug
    ic(res)
    ic(res.json())
    assert res.status_code == 200
    data = res.json()
    if "message" in data:
        message = data["message"]
        assert type(message) == str
        assert message == "success"


@pytest.mark.asyncio
async def test_delete_day():
    """
    Test delete day
    :return: None
    """
    headers = Headers({config("TEST_TOKEN_KEY"): storage.api_key})

    # async request
    async with AsyncClient(app=api, base_url=storage.base_url) as ac:
        res = await ac.delete(parse_path("day/01_01_2020"), headers=headers)

    # debug
    ic(res)
    ic(res.json())
    assert res.status_code == 200
    data = res.json()
    if "message" in data:
        message = data["message"]
        assert type(message) == str
        assert message == "success day deleted"


@pytest.mark.asyncio
async def test_delete_day_task():
    """
    Test delete specific task on id
    :return: None
    """
    headers = Headers({config("TEST_TOKEN_KEY"): storage.api_key})

    # async request
    async with AsyncClient(app=api, base_url=storage.base_url) as ac:
        res = await ac.delete(parse_path("day/01_01_2020/task/1"), headers=headers)

    # debug
    ic(res)
    ic(res.json())
    assert res.status_code == 200
    data = res.json()
    if "message" in data:
        message = data["message"]
        assert type(message) == str
        assert message == "success task deleted"


@pytest.mark.asyncio
async def test_setup():
    """
    Check connection and get the key
    :return:
    """
    await test_get_connection()
    await test_get_api_key()


@pytest.mark.asyncio
async def test_suite_get():
    """
    Creation and update
    :return: None
    """
    await test_get_all_task()
    time.sleep(2)
    await test_get_task_day()
    time.sleep(2)
    await test_get_task_most_recent()


@pytest.mark.asyncio
async def test_suite_post_put():
    """
    Creation and update
    :return: None
    """
    await test_create_new_day()
    time.sleep(2)
    await test_update_day()


@pytest.mark.asyncio
async def test_suite_delete():
    """
    Deletion
    :return: None
    """
    await test_delete_day_task()
    await test_delete_day()


@pytest.mark.asyncio
async def test_wrapper():
    # start with the setup
    await test_setup()

    if storage.scenario == 1:
        await test_suite_post_put()
    elif storage.scenario == 2:
        await test_suite_get()
    elif storage.scenario == 3:
        await test_suite_delete()


@pytest.mark.asyncio
async def test_run():
    """
    Run test based on given scenario
    :return: None

    Start with setup then each scenario consist of:
        1. creation and update of record
        2. fetching of test data
        3. deletion of data
    """
    storage.scenario = 1
    await test_wrapper()
