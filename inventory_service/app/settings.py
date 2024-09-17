from starlette.config import Config
from starlette.datastructures import Secret
from datetime import timedelta

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()

DATABASE_URL = config("DATABASE_URL", cast=Secret)

ALGORITHM = config.get("ALGORITHM")
SECRET_KEY = config.get("SECRET_KEY")

ACCESS_TOKEN_EXPIRE_TIME = timedelta(
    minutes=int(config.get("ACCESS_TOKEN_EXPIRE_TIME")))

ADMIN_SECRET_KEY = config.get("ADMIN_SECRET_KEY")

ADMIN_EXPIRE_TIME = timedelta(minutes=int(
    config.get("ACCESS_TOKEN_EXPIRE_TIME")))


# Kong url
KONG_ADMIN_URL = config.get("KONG_ADMIN_URL")

# topics for produce and consume messages
USER_TOPIC = config.get("USER_TOPIC")
ADMIN_TOPIC = config.get("ADMIN_TOPIC")
