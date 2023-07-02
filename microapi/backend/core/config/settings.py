import os

PROJECT_NAME = "Microservice"
SECRET_KEY = os.environ['SECRET_KEY']

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

API_VERSION = "/v1"

CORS = ["*"]  # change this

TOKEN_EXPIRE_SECONDS = 300

REDIS_BROKER_URL = f"redis://{os.environ.get('REDIS_HOST')}:{os.environ.get('REDIS_PORT')}/{os.environ.get('REDIS_BROKER_DB')}"

DATABASE_URL = f"postgres://{os.environ.get('POSTGRES_USER')}:" \
               f"{os.environ.get('POSTGRES_PASSWORD')}@" \
               f"{os.environ.get('POSTGRES_HOST')}:" \
               f"{os.environ.get('POSTGRES_PORT')}/" \
               f"{os.environ.get('POSTGRES_DB')}"

APP_MODELS = ["apps.users.models", "aerich.models"]

TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": APP_MODELS,
            "default_connection": "default",
        }
    },
}

DATABASE_TEST_URL = f"postgres://{os.environ.get('POSTGRES_USER')}:" \
                    f"{os.environ.get('POSTGRES_PASSWORD')}@" \
                    f"{os.environ.get('POSTGRES_HOST')}:" \
                    f"{os.environ.get('POSTGRES_PORT')}/" + "test_{}"


main_redis_url = f"redis://{os.environ.get('REDIS_HOST')}:{os.environ.get('REDIS_PORT')}/{os.environ.get('REDIS_DB')}"
test_redis_url = f"redis://{os.environ.get('REDIS_HOST')}:{os.environ.get('REDIS_PORT')}/{os.environ.get('REDIS_TEST_DB')}"
