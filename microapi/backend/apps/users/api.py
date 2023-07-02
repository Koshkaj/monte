import json

from fastapi import APIRouter, HTTPException, Request
from .models import User
from fastapi.responses import RedirectResponse
from .services import create_jwt_token, validate_token
from .schemas import TokenRequest, TokenResponse, UserCreateInput, UserOutput
from core.config import settings
from urllib.parse import urlencode
from aiohttp import ClientSession
import re


router = APIRouter()

STEAM_OPENID_URL = 'https://steamcommunity.com/openid/login'


@router.post("/generate_token", response_model=TokenResponse)
async def generate_token(request: Request, data: TokenRequest):
    redis = request.app.redis

    user = await User.get_or_none(id=data.uuid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_token = create_jwt_token(data.uuid)
    await redis.setex(f"token:{data.uuid}", 300, user_token)

    return TokenResponse(
        success=True,
        token=user_token,
        token_type="standard",
        expires_in=settings.TOKEN_EXPIRE_SECONDS
    )


@router.post("/users", response_model=UserCreateInput)
async def create_user(user: UserCreateInput):
    user_obj = User(id='30ddc383-07d2-4ff0-919e-c1fe01384df1', **user.dict())
    await user_obj.save()
    return user_obj


@router.get("/metadata")
async def metadata(request: Request):
    cache = request.app.redis
    # if data := await cache.hgetall(f"user_data:30ddc383-07d2-4ff0-919e-c1fe01384df1"):
    if data := await cache.hgetall(f"user_data:30ddc383-07d2-4ff0-919e-c1fe01384df1"):
        return data
    user = await User.get(id='30ddc383-07d2-4ff0-919e-c1fe01384df1').only("xp", "balance", "username")
    await cache.hset(f"user_data:30ddc383-07d2-4ff0-919e-c1fe01384df1", "xp", user.xp)
    await cache.hset(f"user_data:30ddc383-07d2-4ff0-919e-c1fe01384df1", "balance", user.balance + 200)
    await cache.hset(f"user_data:30ddc383-07d2-4ff0-919e-c1fe01384df1", "username", user.username)
    await cache.expire(f"user_data:30ddc383-07d2-4ff0-919e-c1fe01384df1", 900)
    return user

@router.get('/login')
async def login():
    params = {
        'openid.ns': 'http://specs.openid.net/auth/2.0',
        'openid.mode': 'checkid_setup',
        'openid.return_to': 'http://localhost/api/process_openid',
        'openid.realm': 'http://localhost',
        'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select',
    }

    return RedirectResponse(url=STEAM_OPENID_URL + '?' + urlencode(params))


@router.get('/process_openid')
async def process_openid(request: Request):
    query_params = request.query_params
    print('here')

    params = {
        'openid.assoc_handle': query_params.get('openid.assoc_handle'),
        'openid.signed': query_params.get('openid.signed'),
        'openid.sig': query_params.get('openid.sig'),
        'openid.ns': 'http://specs.openid.net/auth/2.0',
        'openid.mode': 'check_authentication',
    }

    signed = query_params.get('openid.signed').split(',')
    for item in signed:
        val = query_params.get(f'openid.{item.replace(".", "_")}')
        params[f'openid.{item}'] = val

    async with ClientSession() as session:
        async with session.post(STEAM_OPENID_URL, data=params) as resp:
            response_text = await resp.text()

    if re.search(r"is_valid\s*:\s*true", response_text):
        match = re.match(r"^https://steamcommunity.com/openid/id/([0-9]{17,25})$",
                         query_params.get('openid.claimed_id'))
        steam_id = match.group(1) if match else None
        print(f'request has been validated by open id, returning the client id (steam id) of: {steam_id}')

        STEAM_API_KEY = 'C39045D6B4802B444E75774754440158'

        async with ClientSession() as session:
            async with session.get(
                    f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_API_KEY}&steamids={steam_id}') as resp:
                user_data = await resp.json()

        user_data = user_data['response']['players'][0]

        print(user_data)  #shevinaxot db-shi

    else:
        print('error: unable to validate your request')

    return RedirectResponse(url="/")
