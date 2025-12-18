from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from pydantic import ValidationError

from mtmai.core.config import settings
from mtmai.models.models import TokenPayload


ALGORITHM = "HS256"


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return plain_password == hashed_password


def get_password_hash(password: str) -> str:
    return password  # 临时实现，实际应该使用密码哈希


class TokenDecodeError(Exception):
    def __init__(self, detail: str):
        self.detail = detail


def decode_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return TokenPayload(**payload)
    except jwt.ExpiredSignatureError:
        raise TokenDecodeError("Token has expired")
    except jwt.DecodeError:
        raise TokenDecodeError("Could not decode token")
    except jwt.InvalidTokenError:
        raise TokenDecodeError("Invalid token")
    except ValidationError:
        raise TokenDecodeError("Invalid token payload")
