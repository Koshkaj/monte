from typing import Union

from jose import jwt
import os
from dataclasses import dataclass
from types import FunctionType
from functools import wraps
import logging
from grpc import ServerInterceptor

@dataclass
class TokenData:
    user_id: str
    token_type: str
    exp: str


SEKRET = "mysekretpassword" #os.getenv("SECRET_KEY")


def validate_token(token: str) -> Union[None, str]:
    try:
        payload = jwt.decode(token, SEKRET, algorithms=["HS256"])
        token_data = TokenData(**payload)
        if token_data.token_type != "standard":
            return None
    except jwt.JWTError as e:
        return None
    # user = await User.get_or_none(id=token_data.user_id)
    # if user is None:
    #     raise validation_error
    return token_data.user_id


def validate_balance_bet(user_id: str, bet_amount: int, redis_nbc_client) -> bool:
    user_balance = redis_nbc_client.hget(f"user_data:{user_id}", "balance")
    if not (user_balance is None) and int(user_balance) >= bet_amount:
        return True
    return False
