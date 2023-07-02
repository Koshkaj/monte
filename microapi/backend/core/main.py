from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from core.config import settings
from tortoise.contrib.fastapi import register_tortoise
from redis import asyncio as aioredis
from apps.users.api import router


app = FastAPI()
app.redis = aioredis.Redis(host="redis_nbc", port=6379, db=0, decode_responses=True)
app.include_router(router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])


register_tortoise(
    app,
    config=settings.TORTOISE_ORM,
    generate_schemas=False,
    add_exception_handlers=True,
)


@app.get("/")
async def ping():
    return {"status": "ok"}


