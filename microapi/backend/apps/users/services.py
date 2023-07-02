from fastapi.requests import Request
from fastapi.exceptions import HTTPException
from fastapi import status
from datetime import datetime, timedelta

from apps.users.models import User
from apps.users.schemas import TokenData
from core.config import settings
from pydantic import UUID4
from jose import jwt


def create_jwt_token(user_id: UUID4) -> str:
    payload = {
        "user_id": str(user_id),
        "token_type": "standard",
        "exp": datetime.utcnow() + timedelta(seconds=settings.TOKEN_EXPIRE_SECONDS)
    }
    return jwt.encode(payload, settings.SECRET_KEY)


async def validate_token(token: str) -> bool:
    """ Verifies access token, returns user if it is valid (authenticated) else throws an error"""
    invalid_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="could not validate credentials"
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload['token_type'] != "standard":
            raise invalid_token_exception
        token_data = TokenData(**payload)
    except jwt.JWTError as e:
        raise invalid_token_exception

    # user = await get_user(id=token_data.user_id)  # noqa
    user = await User.get_or_none(id=token_data.user_id)
    if user is None:
        raise invalid_token_exception

    return True
