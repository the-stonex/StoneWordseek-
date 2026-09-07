import os


BOT_TOKEN = os.getenv("BOT_TOKEN", "")
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")

OWNER_ID = int(os.getenv("OWNER_ID", "0"))
LOGGER_GROUP_ID = int(os.getenv("LOGGER_GROUP_ID", "0"))

MONGO_URL = os.getenv("MONGO_URL", "")

MAX_ATTEMPTS = int(os.getenv("MAX_ATTEMPTS", "30"))

DATABASE_NAME = "StoneWordseek"
