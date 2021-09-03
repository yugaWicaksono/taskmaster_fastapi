"""
HTTP response module
contains the basic set data and object data to document
also the constants for messages
"""

# failed message

FAILED_CREATE_UPDATE = {"message": "failed creating / updating"}
FAILED_DELETED_DAY = {"message": "failed to delete day"}
FAILED_DELETED_TASK = {"message": "failed to delete task"}
FAILED_DELETED_TASK_NON = {"message": "task not found"}

# server unavailable
SERVER_UNAVAILABLE = {"message": "server unavailable"}

# success message
SUCCESS_CREATE_UPDATE = {"message": "success"}
SUCCESS_DELETED_DAY = {"message": "success day deleted"}
SUCCESS_DELETED_TASK = {"message": "success task deleted"}


# version warning
VERSION_WARNING = "You are using an outdated version, aborted"


def set_data(data: list):
    """
    Set data to object data before sending it as response

    :param data: data object from Mongo
    :return: dict with key "data" and data value
    """
    return {"data": data}


def set_object(**kwargs):
    """
    Set defined as key words argument data to dict rep.

    :param kwargs: your keywords arguments
    :return: dict with your keywords arguments
    """
    this_dict = {}
    for key, value in kwargs.items():
        this_dict[key] = value
    return this_dict
