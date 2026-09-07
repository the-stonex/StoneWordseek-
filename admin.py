from config import OWNER_ID


def is_owner(user_id):
    return user_id == OWNER_ID


async def is_admin(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(
            chat_id,
            user_id,
        )

        return member.status in (
            "administrator",
            "owner",
        )

    except Exception:
        return False
