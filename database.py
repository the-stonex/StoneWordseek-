from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorClient

from config import MONGO_URL, DATABASE_NAME


if not MONGO_URL:
    raise RuntimeError("MONGO_URL is not set")

client = AsyncIOMotorClient(MONGO_URL)

db = client[DATABASE_NAME]

users = db["users"]
chats = db["chats"]
games = db["games"]
guesses = db["guesses"]
scores = db["scores"]
broadcast_logs = db["broadcast_logs"]


def now():
    return datetime.now(timezone.utc)


# =========================
# USERS
# =========================

async def add_user(user_id, name, username=None):
    existing = await users.find_one({"user_id": user_id})

    await users.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "name": name,
                "username": username,
                "updated_at": now(),
            },
            "$setOnInsert": {
                "user_id": user_id,
                "started": True,
                "games": 0,
                "wins": 0,
                "score": 0,
                "streak": 0,
                "created_at": now(),
            },
        },
        upsert=True,
    )

    return existing is None


async def get_started_users():
    cursor = users.find(
        {"started": True},
        {"user_id": 1},
    )

    return [doc["user_id"] async for doc in cursor]


async def total_users():
    return await users.count_documents({"started": True})


# =========================
# GROUPS
# =========================

async def add_chat(
    chat_id,
    title,
    username=None,
    invite_link=None,
    added_by=None,
    added_by_name=None,
    added_by_username=None,
):
    existing = await chats.find_one({"chat_id": chat_id})

    await chats.update_one(
        {"chat_id": chat_id},
        {
            "$set": {
                "title": title,
                "username": username,
                "invite_link": invite_link,
                "added_by": added_by,
                "added_by_name": added_by_name,
                "added_by_username": added_by_username,
                "active": True,
                "updated_at": now(),
            },
            "$setOnInsert": {
                "chat_id": chat_id,
                "created_at": now(),
            },
        },
        upsert=True,
    )

    return existing is None


async def remove_chat(chat_id):
    await chats.update_one(
        {"chat_id": chat_id},
        {
            "$set": {
                "active": False,
                "updated_at": now(),
            }
        },
    )


async def get_active_groups():
    cursor = chats.find(
        {"active": True},
        {"chat_id": 1},
    )

    return [doc["chat_id"] async for doc in cursor]


async def total_groups():
    return await chats.count_documents({"active": True})


# =========================
# GAME
# =========================

async def save_game(chat_id, word, length, started_by):
    await games.update_one(
        {"chat_id": chat_id},
        {
            "$set": {
                "chat_id": chat_id,
                "word": word,
                "length": length,
                "started_by": started_by,
                "attempts": 0,
                "active": True,
                "started_at": now(),
            }
        },
        upsert=True,
    )


async def get_game(chat_id):
    return await games.find_one(
        {
            "chat_id": chat_id,
            "active": True,
        }
    )


async def update_attempts(chat_id, attempts):
    await games.update_one(
        {"chat_id": chat_id},
        {
            "$set": {
                "attempts": attempts,
            }
        },
    )


async def end_game(chat_id):
    await games.update_one(
        {"chat_id": chat_id},
        {
            "$set": {
                "active": False,
                "ended_at": now(),
            }
        },
    )


# =========================
# SCORE
# =========================

async def update_score(user_id, win=False):
    update = {
        "$inc": {
            "games": 1,
            "score": 10 if win else 0,
        }
    }

    if win:
        update["$inc"]["wins"] = 1

    await users.update_one(
        {"user_id": user_id},
        update,
        upsert=True,
    )


async def get_user_stats(user_id):
    return await users.find_one(
        {"user_id": user_id}
    )


# =========================
# BROADCAST LOG
# =========================

async def save_broadcast(
    broadcast_type,
    total,
    success,
    failed,
):
    await broadcast_logs.insert_one(
        {
            "type": broadcast_type,
            "total": total,
            "success": success,
            "failed": failed,
            "created_at": now(),
        }
    )
