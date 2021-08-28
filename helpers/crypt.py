import jwt
from jwt import InvalidSignatureError
from decouple import config
import logging

SECRET = config("SECRET")
CLIENT_SECRET = config("CLIENT_SECRET")


class CryptoHelper(object):
    """
     helper class to decode or encode jwt
    """

    @staticmethod
    def verify_token(token: str, secret: str) -> bool:
        """
        verify JWT
        :param token: JWT as string
        :return: True if the payload match
        """
        try:
            byte_string = token.encode('UTF-8')
            payload = jwt.decode(byte_string, secret, algorithms=["HS256"], options={"verify_signature": True})
            if payload is not None:
                if payload["name"] == config("AUTH_USER"):
                    return True

        except InvalidSignatureError as error:
            logging.error(error)
            return False
