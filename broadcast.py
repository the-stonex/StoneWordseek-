import asyncio

from pyrogram import Client
from pyrogram.errors import FloodWait, UserIsBlocked, PeerIdInvalid

from database import (
    get_started_users,
    get_active_groups,
    save_broadcast,
)

broadcast_running = False
broadcast_cancelled = False

broadcast_stats = {
    "type": None,
    "total": 0,
    "success": 0,
    "failed": 0,
}


async def send_one(app, chat_id, message):
    global broadcast_stats

    try:
        await message.copy(chat_id)

        broadcast_stats["success"] += 1
        return True

    except FloodWait as e:
        await asyncio.sleep(e.value)

        try:
            await message.copy(chat_id)
            broadcast_stats["success"] += 1
            return True
        except Exception:
            broadcast_stats["failed"] += 1
            return False

    except (
        UserIsBlocked,
        PeerIdInvalid,
    ):
        broadcast_stats["failed"] += 1
        return False

    except Exception as e:
        print(f"Broadcast error {chat_id}: {e}")
        broadcast_stats["failed"] += 1
        return False


async def start_broadcast(app, message, target_type):
    global broadcast_running
    global broadcast_cancelled
    global broadcast_stats

    if broadcast_running:
        return "⚠️ एक broadcast पहले से चल रहा है"

    broadcast_running = True
    broadcast_cancelled = False

    if target_type == "bot":
        targets = await get_started_users()

    elif target_type == "group":
        targets = await get_active_groups()

    elif target_type == "gu":
        users = await get_started_users()
        groups = await get_active_groups()

        targets = list(dict.fromkeys(users + groups))

    else:
        broadcast_running = False
        return "❌ Invalid broadcast type"

    broadcast_stats = {
        "type": target_type,
        "total": len(targets),
        "success": 0,
        "failed": 0,
    }

    for chat_id in targets:

        if broadcast_cancelled:
            break

        await send_one(app, chat_id, message)

        await asyncio.sleep(0.05)

    broadcast_running = False

    await save_broadcast(
        target_type,
        broadcast_stats["total"],
        broadcast_stats["success"],
        broadcast_stats["failed"],
    )

    return (
        f"📢 <b>Broadcast Completed</b>\n\n"
        f"🎯 <b>Type:</b> {target_type}\n"
        f"📊 <b>Total:</b> {broadcast_stats['total']}\n"
        f"✅ <b>Success:</b> {broadcast_stats['success']}\n"
        f"❌ <b>Failed:</b> {broadcast_stats['failed']}"
    )


def cancel_broadcast():
    global broadcast_cancelled

    if not broadcast_running:
        return False

    broadcast_cancelled = True
    return True


def get_status():
    return (
        f"📊 <b>Broadcast Status</b>\n\n"
        f"📌 Type: {broadcast_stats['type']}\n"
        f"🎯 Total: {broadcast_stats['total']}\n"
        f"✅ Success: {broadcast_stats['success']}\n"
        f"❌ Failed: {broadcast_stats['failed']}\n"
        f"⚙️ Running: {'Yes' if broadcast_running else 'No'}"
    )
