from pymongo import MongoClient
from decouple import config
from helpers.crypt import CryptoHelper
from interface.access_key import AccessKey
from helpers.crypt import SECRET, CLIENT_SECRET
from pymongo.errors import ConnectionFailure, OperationFailure

# logging and internal error messages
import logging
import src.error as error

# import response
import src.http_response as res

db_user = config("USER")
db_pass = config("PASS")
db_name = config("DB")
coll_task = config("COLL_TASK")
coll_keys = config("COLL_KEYS")
db_host = config("HOST")
URI = f"mongodb+srv://{db_user}:{db_pass}{db_host}/{db_name}?retryWrites=true&w=majority"


def set_record_to_active(record_day):
    # if the latest record is active then set that record
    # as active record
    last = record_day["records"][-1]
    if "active" in last:
        is_active = last["active"]
        # self.active_record = last if is_active is True else None


class MongoConnection(object):

    @staticmethod
    def handle_not_connected(client: MongoClient):
        """
        Check if the client is connected
        :param client:
        :return: None if client is not connected
        """
        if client is None:
            logging.error(error.MONGO_DB_TASKS)
            return None

    @staticmethod
    def get_database():
        """
        Get the database
        :return: MongoClient or none if connection error
        """
        # see https://stackoverflow.com/a/49381588 for initiation of mongoclient
        client = MongoClient(URI)
        try:
            # check connection with ismaster command
            client.admin.command("ismaster")
            return client
        except ConnectionFailure:
            # log no connection error and return None
            logging.error(error.MONGO_CONNECTION)
            return None
        except OperationFailure as e:
            # log no connection error and return None
            logging.error(e)
            return None

    @staticmethod
    def get_tasks_collection(client: MongoClient):
        """
        Get the tasks
        :param client: MongoClient or None if not connected
        :return: collection of tasks
        """
        # check the client
        MongoConnection.handle_not_connected(client)
        # else assigned collection
        collection = client[db_name][coll_task]
        return collection

    @staticmethod
    def get_keys_collection(client: MongoClient):
        """
        Get the keys
        :param client: MongoClient or None if not connected
        :return: collection of keys
        """
        # check the client
        MongoConnection.handle_not_connected(client)
        # else assigned collection
        collection = client[db_name][coll_keys]
        return collection


class MongoError(BaseException):
    """
    Mongo error inherit base exception
    """

    def __init__(self, caught_error):
        self.error = caught_error


class MongoPost:
    """
    Records has to be array of tasks record
    """
    def __init__(self, _id, records):
        self.mongo_rep = {"_id": _id, "records": records}


class MongoAPI:
    # based check on connection
    isConnected = False
    tasks = None
    keys = None

    def __init__(self):
        try:
            self.client = MongoConnection.get_database()
            # set is connected to this instance if it is not None
            if self.client is None:
                self.isConnected = False
            else:
                self.isConnected = True

            if self.isConnected:
                # get the tasks collection
                self.tasks = MongoConnection.get_tasks_collection(self.client)

                # get the keys collection
                self.keys = MongoConnection.get_keys_collection(self.client)

                # check if the tasks has error
                if self.tasks is MongoError:
                    self.tasks = None

                # check if the keys has error
                if self.keys is MongoError:
                    self.keys = None

        except ConnectionFailure:
            # all of the handling has been done in the try block
            pass

    def check_tasks_exist(self) -> bool:
        """
        Check if the tasks is set
        :return: None if tasks is not exist
        """
        return self.tasks is not None

    def check_keys_exist(self) -> bool:
        """
        Check if keys exists
        :return: None if keys does not exists
        """
        return self.keys is not None

    def get_connection(self):
        """
        GET the connection status of the database connection
        :return: True if mongo is connected, False otherwise
        """
        return self.isConnected

    def get_key(self):
        """
        GET the API key
        :return: API key as string or None if keys is not connected
        """
        # 1. check if key exists
        if self.check_keys_exist():
            # 2. return token if it does
            token = self.keys.find_one({"type": config("AUTH_USER")})["key"]
            if CryptoHelper.verify_token(token, SECRET):
                # if token is verified return token
                return token
        else:
            return None

    def get_client_key(self, body: AccessKey):
        client_token = body.access_token
        if CryptoHelper.verify_token(client_token, CLIENT_SECRET):
            # if it is verified get the key from the database
            return self.get_key()

    def get_all_records(self):
        """
        GET all records
        :return: records or None if does not exits
        """
        # check if tasks exist
        if self.check_tasks_exist():
            # return all data
            data = []
            records = self.tasks.find()
            for item in records:
                data.append(item)
            return data
        else:
            return None

    def get_record_for_day(self, day):
        """
        GET record of the day
        :param day: day in format of `dd_mm_yyyy`
        :return: record the day
        """
        # check if tasks exist
        if self.check_tasks_exist():
            # return day data
            this = {"_id": day}
            record_day = self.tasks.find_one(this)
            if record_day is None:
                return None
            else:
                # return record of day
                return record_day
        else:
            return None

    def get_most_recent_record(self, day):
        """
        GET the latest record
        :param day: day in format of `dd_mm_yyyy`
        :return: record the day - the latest
        """

        # check if tasks exist
        if self.check_tasks_exist():
            # return most recent record
            this = {"_id": day}
            record_day = self.tasks.find_one(this)
            if record_day is None:
                return None
            else:
                records = record_day["records"]
                if len(records) > 0:
                    # return last element in the record
                    return records.pop()
        else:
            return None

    def create_record_for_day(self, day, records):
        """
        POST create record for the day
        :param day: day in format of `dd_mm_yyyy`
        :param records: array of record
        :return: dict if success
        """

        # check if tasks exist
        if self.check_tasks_exist():
            # create the post
            post = MongoPost(day, records)
            self.tasks.insert_one(post.mongo_rep)
            return res.SUCCESS_CREATE_UPDATE
        else:
            return None

    def update_record_for_day(self, day, records):
        """
        PUT update the record of day
        :param day: day in format of `dd_mm_yyyy`
        :param records: array of record
        :return: dict of success
        """

        # check if tasks exist
        if self.check_tasks_exist():
            # update
            existing = self.get_record_for_day(day)
            if existing is None:
                return MongoError("Record not found - update cancelled")
            else:
                self.tasks.update_one({"_id": day}, {"$set": {"records": records}})
                return res.SUCCESS_CREATE_UPDATE
        else:
            return None
