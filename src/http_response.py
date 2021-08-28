FAILED_CREATE_UPDATE = {"message": "failed creating / updating"}
SUCCESS_CREATE_UPDATE = {"message": "success"}
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
