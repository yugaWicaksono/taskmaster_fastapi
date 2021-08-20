from pydantic import BaseModel
from .record import Record
from typing import List


class BodyObject(BaseModel):
    """
    Body  Object to be sent in POST and PUT requests
    """
    id: str
    records: List[Record] = []
