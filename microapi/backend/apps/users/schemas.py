from pydantic import BaseModel, UUID4
from datetime import datetime


class TokenData(BaseModel):
    user_id: str
    token_type: str
    exp: str


class TokenRequest(BaseModel):
    event: str
    uuid: UUID4


class TokenResponse(BaseModel):
    success: bool
    token: str
    token_type: str
    expires_in: int


class UserCreateInput(BaseModel):
    username: str


class UserOutput(BaseModel):
    username: str
    balance: int
    xp: int
