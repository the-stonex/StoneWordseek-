from pyrogram import Client, filters
from pyrogram.types import Message

from config import (
    BOT_TOKEN,
    API_ID,
    API_HASH,
    OWNER_ID,
)

from database import (
    add_user,
    add_chat,
    remove_chat,
    get_user_stats,
    total_users,
    total_groups,
)

from logger import (
    log_new_user,
    log_bot_added,
    log_bot_removed,
)

from game import (
    start_game,
    process_guess,
    stop_game,
)

from admin import is_owner

from broadcast import (
    start_broadcast,
    cancel_broadcast,
    get_status,
)


app = Client(
    "StoneWordseek",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)


# =========================
# START
# =========================

@app.on_message(filters.command("start"))
async def start_command(client, message: Message):

    if message.from_user:
        is_new = await add_user(
            message.from_user.id,
            message.from_user.first_name,
            message.from_user.username,
        )

        if is_new:
            await log_new_user(
                client,
                message.from_user,
            )

    await message.reply_text(
        "👋 <b>Welcome to StoneWordseek!</b>\n\n"
        "🧩 Word Puzzle Game\n\n"
        "🎮 /game - Start Game\n"
        "📜 /rules - Rules\n"
        "📊 /mystats - My Stats\n"
        "🏆 /ranking - Ranking"
    )


# =========================
# GAME
# =========================

@app.on_message(filters.command("game"))
async def game_command(client, message):

    if not message.chat:
        return

    user_id = message.from_user.id

    text = message.text.split()

    length = 5

    if len(text) > 1:
        try:
            length = int(text[1])
        except ValueError:
            length = 5

    _, response = await start_game(
        message.chat.id,
        user_id,
        length,
    )

    await message.reply_text(response)


@app.on_message(
    filters.text
    & ~filters.command(
        [
            "start",
            "game",
            "stop",
            "rules",
            "mystats",
            "ranking",
            "broadcast_bot",
            "broadcast_group",
            "broadcast_Gu",
            "broadcast_status",
            "broadcast_cancel",
        ]
    )
)
async def guess_handler(client, message):

    if not message.from_user:
        return

    response = await process_guess(
        message.chat.id,
        message.from_user.id,
        message.text,
    )

    if response:
        await message.reply_text(response)


@app.on_message(filters.command("stop"))
async def stop_command(client, message):

    response = await stop_game(
        message.chat.id
    )

    await message.reply_text(response)


@app.on_message(filters.command("rules"))
async def rules_command(client, message):

    await message.reply_text(
        "📜 <b>StoneWordseek Rules</b>\n\n"
        "1️⃣ /game से game शुरू करें\n"
        "2️⃣ सही length का word भेजें\n"
        "3️⃣ 🟩 सही position\n"
        "4️⃣ 🟨 Word में है लेकिन position गलत\n"
        "5️⃣ ⬛ Word में नहीं है\n"
        "6️⃣ Maximum 30 attempts"
    )


@app.on_message(filters.command("mystats"))
async def mystats_command(client, message):

    stats = await get_user_stats(
        message.from_user.id
    )

    if not stats:
        await message.reply_text(
            "❌ पहले /start करें"
        )
        return

    await message.reply_text(
        f"📊 <b>Your Stats</b>\n\n"
        f"🎮 Games: {stats.get('games', 0)}\n"
        f"🏆 Wins: {stats.get('wins', 0)}\n"
        f"💰 Score: {stats.get('score', 0)}\n"
        f"🔥 Streak: {stats.get('streak', 0)}"
    )


# =========================
# BOT STATS
# =========================

@app.on_message(filters.command("botstats"))
async def botstats_command(client, message):

    if not is_owner(message.from_user.id):
        return

    users = await total_users()
    groups = await total_groups()

    await message.reply_text(
        f"📊 <b>StoneWordseek Stats</b>\n\n"
        f"👤 Started Users: <b>{users}</b>\n"
        f"👥 Active Groups: <b>{groups}</b>"
    )


# =========================
# BROADCAST BOT
# =========================

@app.on_message(filters.command("broadcast_bot"))
async def broadcast_bot(client, message):

    if not is_owner(message.from_user.id):
        return

    if message.chat.type != "private":
        await message.reply_text(
            "❌ /broadcast_bot केवल Bot के private chat में use करें"
        )
        return

    if not message.reply_to_message:
        await message.reply_text(
            "❌ जिस message को broadcast करना है उस पर reply करके\n"
            "/broadcast_bot भेजें"
        )
        return

    status = await message.reply_text(
        "📢 User broadcast शुरू हो रहा है..."
    )

    result = await start_broadcast(
        client,
        message.reply_to_message,
        "bot",
    )

    await status.edit_text(result)


# =========================
# BROADCAST GROUP
# =========================

@app.on_message(filters.command("broadcast_group"))
async def broadcast_group(client, message):

    if not is_owner(message.from_user.id):
        return

    if not message.reply_to_message:
        await message.reply_text(
            "❌ Message पर reply करके /broadcast_group भेजें"
        )
        return

    status = await message.reply_text(
        "📢 Group broadcast शुरू हो रहा है..."
    )

    result = await start_broadcast(
        client,
        message.reply_to_message,
        "group",
    )

    await status.edit_text(result)


# =========================
# BROADCAST GU
# =========================

@app.on_message(filters.command("broadcast_Gu"))
async def broadcast_gu(client, message):

    if not is_owner(message.from_user.id):
        return

    if not message.reply_to_message:
        await message.reply_text(
            "❌ Message पर reply करके /broadcast_Gu भेजें"
        )
        return

    status = await message.reply_text(
        "📢 User + Group broadcast शुरू हो रहा है..."
    )

    result = await start_broadcast(
        client,
        message.reply_to_message,
        "gu",
    )

    await status.edit_text(result)


# =========================
# BROADCAST STATUS
# =========================

@app.on_message(filters.command("broadcast_status"))
async def broadcast_status(client, message):

    if not is_owner(message.from_user.id):
        return

    await message.reply_text(
        get_status()
    )


# =========================
# BROADCAST CANCEL
# =========================

@app.on_message(filters.command("broadcast_cancel"))
async def broadcast_cancel_command(client, message):

    if not is_owner(message.from_user.id):
        return

    if cancel_broadcast():
        await message.reply_text(
            "🛑 Broadcast cancel कर दिया गया"
        )
    else:
        await message.reply_text(
            "ℹ️ कोई broadcast चल नहीं रहा"
        )


# =========================
# NEW CHAT MEMBER
# =========================

@app.on_message(filters.new_chat_members)
async def bot_added(client, message):

    for member in message.new_chat_members:

        if member.id != (await client.get_me()).id:
            continue

        adder = message.from_user

        invite_link = None

        try:
            if message.chat.username:
                invite_link = (
                    f"https://t.me/{message.chat.username}"
                )
        except Exception:
            pass

        is_new = await add_chat(
            chat_id=message.chat.id,
            title=message.chat.title or "Unknown",
            username=message.chat.username,
            invite_link=invite_link,
            added_by=adder.id if adder else None,
            added_by_name=(
                adder.first_name
                if adder
                else None
            ),
            added_by_username=(
                adder.username
                if adder
                else None
            ),
        )

        if is_new:
            await log_bot_added(
                client,
                message.chat,
                adder,
            )


# =========================
# BOT REMOVED
# =========================

@app.on_message(filters.left_chat_member)
async def bot_removed(client, message):

    me = await client.get_me()

    if message.left_chat_member.id == me.id:

        await remove_chat(
            message.chat.id
        )

        await log_bot_removed(
            client,
            message.chat,
        )


# =========================
# RUN
# =========================

print("StoneWordseek is starting...")

app.run()
