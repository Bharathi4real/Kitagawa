from requests import post, get
from Marin import bot
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton



def paste(text):
    url = "https://spaceb.in/api/v1/documents/"
    res = post(url, data={"content": text, "extension": "txt"})
    return f"https://spaceb.in/{res.json()['payload']['id']}"

@bot.on_message(filters.command('paste'))
def pastex(_, message):
    text = message.reply_to_message
    if text:
        x = paste(text.text)
        message.reply(x,
                      reply_markup=InlineKeyboardMarkup(
                          [[InlineKeyboardButton("Open", url=x)]]),
                      disable_web_page_preview=True)

    else:
        message.reply_text("Reply to a message!")


PASTE_HANDLER = DisableAbleCommandHandler("paste", paste, run_async=True)
dispatcher.add_handler(PASTE_HANDLER)

__command_list__ = ["paste"]
__handlers__ = [PASTE_HANDLER]
