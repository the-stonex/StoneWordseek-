from pyrogram import Client
from pyrogram.types import ChatMemberUpdated

from config import LOGGER_GROUP_ID
from database import total_groups, total_users


async def send_logger(app: Client, text: str):
    if not LOGGER_GROUP_ID:
        return

    try:
        await app.send_message(
            LOGGER_GROUP_ID,
            text,
            disable_web_page_preview=True,
        )
    except Exception as e:
        print(f"Logger error: {e}")


async def log_new_user(app, user):
    users = await total_users()
    groups = await total_groups()

    username = f"@{user.username}" if user.username else "None"

    text = f"""
🚀 <b>New User Started StoneWordseek</b>

👤 <b>Name:</b> {user.first_name}
🔹 <b>Username:</b> {username}
🆔 <b>User ID:</b> <code>{user.id}</code>

👤 <b>Total Started Users:</b> {users}
👥 <b>Total Active Groups:</b> {groups}
"""

    await send_logger(app, text)


async def log_bot_added(app, chat, adder):
    groups = await total_groups()
    users = await total_users()

    chat_username = getattr(chat, "username", None)

    if chat_username:
        group_link = f"https://t.me/{chat_username}"
    else:
        group_link = "Private group / Link unavailable"

    adder_username = (
        f"@{adder.username}"
        if adder and adder.username
        else "None"
    )

    adder_name = (
        adder.first_name
        if adder
        else "Unknown"
    )

    adder_id = adder.id if adder else "Unknown"

    text = f"""
🤖 <b>StoneWordseek — Bot Added</b>

💬 <b>Group:</b> {chat.title}
🆔 <b>Group ID:</b> <code>{chat.id}</code>
🔗 <b>Group Link:</b> {group_link}

👤 <b>Added By:</b> {adder_name}
🔹 <b>Username:</b> {adder_username}
🆔 <b>User ID:</b> <code>{adder_id}</code>

👥 <b>Total Active Groups:</b> {groups}
👤 <b>Total Started Users:</b> {users}
"""

    await send_logger(app, text)


async def log_bot_removed(app, chat):
    groups = await total_groups()
    users = await total_users()

    text = f"""
❌ <b>StoneWordseek — Bot Removed</b>

💬 <b>Group:</b> {chat.title}
🆔 <b>Group ID:</b> <code>{chat.id}</code>

👥 <b>Total Active Groups:</b> {groups}
👤 <b>Total Started Users:</b> {users}
"""

    await send_logger(app, text)
