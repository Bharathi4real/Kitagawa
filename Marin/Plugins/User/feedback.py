import random

from telegram import ParseMode
from telethon import Button

from Marin import OWNER_ID, SUPPORT_CHAT
from Marin import telethn as tbot

from Marin.events import register


@register(pattern="/feedback ?(.*)")
async def feedback(e):
    quew = e.pattern_match.group(1)
    user_id = e.sender.id
    user_name = e.sender.first_name
    mention = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    Marin = (
        "https://telegra.ph/file/878f2fc6b940d8b9b5322.jpg",
        "https://telegra.ph/file/12a7d0a0c4db257f6ab5b.jpg",
        "https://telegra.ph/file/976de92dc3f124509cc6e.jpg",
        "https://telegra.ph/file/34334a43fb17f1dec9fce.jpg",
        "https://telegra.ph/file/fa1c7c944c0c3314fbaa1.jpg",
        "https://telegra.ph/file/08410b8b057782d6f59f7.jpg",
    )
    NoText = (
        "https://telegra.ph/file/2dd04f407b16bc2cfdf76.jpg",
        "https://telegra.ph/file/08410b8b057782d6f59f7.jpg",
    )
    BUTTON = [[Button.url("Go To Support Group", f"https://t.me/{SUPPORT_CHAT}")]]
    TEXT = "Thanks For Your Feedback, I Hope You Happy With Our Service"
    GIVE = "Give Some Text For Feedback ✨"
    logger_text = f"""
**New Feedback**

**From User:** {mention}
**Username:** @{e.sender.username}
**User ID:** `{e.sender.id}`
**Feedback:** `{e.text}`
"""
    if e.sender_id != OWNER_ID and not quew:
        await e.reply(
            GIVE,
            parse_mode=ParseMode.MARKDOWN,
            buttons=BUTTON,
            file=random.choice(NoText),
        ),
        return

    await tbot.send_message(
        SUPPORT_CHAT,
        f"{logger_text}",
        file=random.choice(Marin),
        link_preview=False,
    )
    await e.reply(TEXT, file=random.choice(Marin), buttons=BUTTON)


__help__ = """Give Us a Feedback Or Request a Feature.
‣ /feedback <your feedback>
‣ /feedback #Req <your request> """

__mod_name__ = "Feedback"
