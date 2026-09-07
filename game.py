import random

from config import MAX_ATTEMPTS
from database import (
    save_game,
    get_game,
    update_attempts,
    end_game,
    update_score,
)


WORDS = {
    4: [
        "GAME",
        "WORD",
        "PLAY",
        "KING",
        "STAR",
        "MOON",
        "LOVE",
        "FIRE",
        "TIME",
        "LIFE",
    ],
    5: [
        "STONE",
        "WORDS",
        "MUSIC",
        "LIGHT",
        "HEART",
        "DREAM",
        "WORLD",
        "NIGHT",
        "SMILE",
        "HOUSE",
    ],
    6: [
        "PYTHON",
        "PUZZLE",
        "PLAYER",
        "WINNER",
        "FRIEND",
        "GAMING",
        "CODING",
        "PLANET",
        "SCHOOL",
        "MASTER",
    ],
}


def choose_word(length):
    return random.choice(WORDS[length]).upper()


def check_guess(word, guess):
    result = []

    for index, letter in enumerate(guess):
        if index < len(word) and letter == word[index]:
            result.append(f"🟩 {letter}")
        elif letter in word:
            result.append(f"🟨 {letter}")
        else:
            result.append(f"⬛ {letter}")

    return " ".join(result)


async def start_game(chat_id, user_id, length=5):
    if length not in (4, 5, 6):
        length = 5

    existing = await get_game(chat_id)

    if existing:
        return None, "⚠️ इस group में पहले से game चल रहा है"

    word = choose_word(length)

    await save_game(
        chat_id,
        word,
        length,
        user_id,
    )

    return word, (
        f"🎮 <b>StoneWordseek Started!</b>\n\n"
        f"🔤 Word Length: <b>{length}</b>\n"
        f"🎯 Attempts: <b>{MAX_ATTEMPTS}</b>\n\n"
        f"अपना word भेजो और puzzle solve करो 🧩"
    )


async def process_guess(chat_id, user_id, guess):
    game = await get_game(chat_id)

    if not game:
        return "❌ अभी कोई game नहीं चल रहा"

    word = game["word"]
    length = game["length"]

    guess = guess.upper().strip()

    if len(guess) != length:
        return f"❌ केवल {length} अक्षर का word भेजें"

    attempts = game.get("attempts", 0) + 1

    await update_attempts(chat_id, attempts)

    if guess == word:
        await end_game(chat_id)
        await update_score(user_id, True)

        return (
            f"🎉 <b>Correct!</b>\n\n"
            f"🏆 Winner: <b>{user_id}</b>\n"
            f"🔤 Word: <code>{word}</code>\n"
            f"🎯 Attempts: <b>{attempts}</b>"
        )

    if attempts >= MAX_ATTEMPTS:
        await end_game(chat_id)

        return (
            f"💀 <b>Game Over!</b>\n\n"
            f"🔤 Correct Word: <code>{word}</code>"
        )

    return (
        f"{check_guess(word, guess)}\n\n"
        f"🎯 Attempt: <b>{attempts}/{MAX_ATTEMPTS}</b>"
    )


async def stop_game(chat_id):
    game = await get_game(chat_id)

    if not game:
        return "❌ कोई active game नहीं है"

    word = game["word"]

    await end_game(chat_id)

    return (
        f"🛑 <b>Game Stopped</b>\n\n"
        f"🔤 Word था: <code>{word}</code>"
    )
