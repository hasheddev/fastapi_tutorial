import logging
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
import uuid
from itsdangerous import URLSafeTimedSerializer

from src.config import Config

password_context = CryptContext(schemes=["bcrypt"])
ACCESS_TOKEN_EXPIRY = 30000

serializer = URLSafeTimedSerializer(
    secret_key=Config.JWT_SECRET, salt="email-configuration"
)


def generate_passord_hash(password: str) -> str:
    hash = password_context.hash(password)
    return hash


def verify_password(password: str, hash: str) -> bool:
    return password_context.verify(password, hash)


Expiry = timedelta | None


def create_access_token(
    user_data: dict, expiry: Expiry = None, is_refresh: bool = False
):
    payload = {}
    payload["user"] = user_data
    expiration_duration = (
        expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY)
    )
    payload["exp"] = datetime.now() + expiration_duration
    payload["jti"] = str(uuid.uuid4())
    payload["is_refresh"] = is_refresh

    token = jwt.encode(
        payload=payload, key=Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM
    )
    return token


def decode_token(token: str) -> dict | None:
    try:
        token_data = jwt.decode(
            jwt=token, key=Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM]
        )
        return token_data
    except jwt.PyJWTError as e:
        logging.exception(e)
        return None


def create_url_safe_token(data: dict):
    token = serializer.dumps(data)
    return token


def decode_url_safe_token(token: str):
    try:
        tokendata: dict[str, str] = serializer.loads(token, max_age=3600)
        return tokendata
    except Exception as e:
        logging.error(str(e))
        return None
