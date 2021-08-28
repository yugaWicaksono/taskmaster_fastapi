from pydantic import BaseModel


class AccessKey(BaseModel):
    """
    Access token post body that contains client key
    """
    access_token: str
