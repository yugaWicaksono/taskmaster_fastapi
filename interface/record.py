from pydantic import BaseModel


class Record(BaseModel):
    """
    Record representation
    """
    id: int
    task: str
    start: str
    end: str
    delta: float

