import html
import json
import os
import psutil
import subprocess
from typing import Optional

from time import sleep
from typing import List
from telegram import TelegramError
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import Filters, CommandHandler
from telegram.ext.dispatcher import run_async, CallbackContext

import random
import Marin.Handlers.readable_time
import Marin.Database.users_sql as sql
from Marin.Handlers.filters import CustomFilters

from Marin.Plugins.Admin.disable import DisableAbleCommandHandler

USERS_GROUP = 4

from Marin import (
    StartTime,
    DEV_USERS,
    OWNER_ID,
    DRAGONS,
    SUPPORT_CHAT,
    DEMONS,
    TIGERS,
    WOLVES,
    LOGGER,
    dispatcher,
)
from Marin.Handlers.validation import (
    dev_plus,
    sudo_plus,
    whitelist_plus,
)
from Marin.Handlers.extraction import extract_user
from Marin.Plugins.Admin.log_channel import gloggable
from telegram import ParseMode
from telegram.utils.helpers import mention_html

ELEVATED_USERS_FILE = os.path.join(os.getcwd(), "Marin/elevated_users.json")


def check_user_id(user_id: int, context: CallbackContext) -> Optional[str]:
    bot = context.bot
    if not user_id:
        reply = "That...is a chat! baka ka omae?"

    elif user_id == bot.id:
        reply = "This does not work that way."

    else:
        reply = None
    return reply


# This can serve as a deeplink example.
# disasters =
# """ Text here """

# do not async, not a handler
# def send_disasters(update):
#    update.effective_message.reply_text(
#        disasters, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

### Deep link example ends

async def sys_stats():
    bot_uptime = int(time.time() - StartTime)
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    process = psutil.Process(os.getpid())
    stats = f"""
{Marin}@MarinAnimeBot
------------------
UPTIME: {readable_time.get_readable_time((bot_uptime))}
BOT: {round(process.memory_info()[0] / 1024 ** 2)} MB
CPU: {cpu}%
RAM: {mem}%
DISK: {disk}%
"""
    return stats

@dev_plus
@gloggable
def addsudo(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        message.reply_text("This member is already a Dragon Disaster")
        return ""

    if user_id in DEMONS:
        rt += "Requested HA to promote a Demon Disaster to Dragon."
        data["supports"].remove(user_id)
        DEMONS.remove(user_id)

    if user_id in WOLVES:
        rt += "Requested HA to promote a Wolf Disaster to Dragon."
        data["whitelists"].remove(user_id)
        WOLVES.remove(user_id)

    data["sudos"].append(user_id)
    DRAGONS.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt
        + "\nSuccessfully set Disaster level of {} to Dragon!".format(
            user_member.first_name,
        ),
    )

    log_message = (
        f"#SUDO\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@sudo_plus
@gloggable
def addsupport(
    update: Update,
    context: CallbackContext,
) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        rt += "Requested HA to demote this Dragon to Demon"
        data["sudos"].remove(user_id)
        DRAGONS.remove(user_id)

    if user_id in DEMONS:
        message.reply_text("This user is already a Demon Disaster.")
        return ""

    if user_id in WOLVES:
        rt += "Requested HA to promote this Wolf Disaster to Demon"
        data["whitelists"].remove(user_id)
        WOLVES.remove(user_id)

    data["supports"].append(user_id)
    DEMONS.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt + f"\n{user_member.first_name} was added as a Demon Disaster!",
    )

    log_message = (
        f"#SUPPORT\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@sudo_plus
@gloggable
def addwhitelist(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        rt += "This member is a Dragon Disaster, Demoting to Wolf."
        data["sudos"].remove(user_id)
        DRAGONS.remove(user_id)

    if user_id in DEMONS:
        rt += "This user is already a Demon Disaster, Demoting to Wolf."
        data["supports"].remove(user_id)
        DEMONS.remove(user_id)

    if user_id in WOLVES:
        message.reply_text("This user is already a Wolf Disaster.")
        return ""

    data["whitelists"].append(user_id)
    WOLVES.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt + f"\nSuccessfully promoted {user_member.first_name} to a Wolf Disaster!",
    )

    log_message = (
        f"#WHITELIST\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))} \n"
        f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@sudo_plus
@gloggable
def addtiger(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        rt += "This member is a Dragon Disaster, Demoting to Tiger."
        data["sudos"].remove(user_id)
        DRAGONS.remove(user_id)

    if user_id in DEMONS:
        rt += "This user is already a Demon Disaster, Demoting to Tiger."
        data["supports"].remove(user_id)
        DEMONS.remove(user_id)

    if user_id in WOLVES:
        rt += "This user is already a Wolf Disaster, Demoting to Tiger."
        data["whitelists"].remove(user_id)
        WOLVES.remove(user_id)

    if user_id in TIGERS:
        message.reply_text("This user is already a Tiger.")
        return ""

    data["tigers"].append(user_id)
    TIGERS.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt + f"\nSuccessfully promoted {user_member.first_name} to a Tiger Disaster!",
    )

    log_message = (
        f"#TIGER\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))} \n"
        f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@dev_plus
@gloggable
def removesudo(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        message.reply_text("Requested HA to demote this user to Civilian")
        DRAGONS.remove(user_id)
        data["sudos"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (
            f"#UNSUDO\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
        )

        if chat.type != "private":
            log_message = "<b>{}:</b>\n".format(html.escape(chat.title)) + log_message

        return log_message

    else:
        message.reply_text("This user is not a Dragon Disaster!")
        return ""


@sudo_plus
@gloggable
def removesupport(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DEMONS:
        message.reply_text("Requested HA to demote this user to Civilian")
        DEMONS.remove(user_id)
        data["supports"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (
            f"#UNSUPPORT\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
        )

        if chat.type != "private":
            log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

        return log_message

    else:
        message.reply_text("This user is not a Demon level Disaster!")
        return ""


@sudo_plus
@gloggable
def removewhitelist(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in WOLVES:
        message.reply_text("Demoting to normal user")
        WOLVES.remove(user_id)
        data["whitelists"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (
            f"#UNWHITELIST\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
        )

        if chat.type != "private":
            log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

        return log_message
    else:
        message.reply_text("This user is not a Wolf Disaster!")
        return ""


@sudo_plus
@gloggable
def removetiger(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in TIGERS:
        message.reply_text("Demoting to normal user")
        TIGERS.remove(user_id)
        data["tigers"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (
            f"#UNTIGER\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
        )

        if chat.type != "private":
            log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

        return log_message
    else:
        message.reply_text("This user is not a Tiger Disaster!")
        return ""


@whitelist_plus
def whitelistlist(update: Update, context: CallbackContext):
    reply = "<b>Known Wolf Disasters 🐺:</b>\n"
    m = update.effective_message.reply_text(
        "<code>Gathering intel..</code>",
        parse_mode=ParseMode.HTML,
    )
    bot = context.bot
    for each_user in WOLVES:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)

            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


@whitelist_plus
def tigerlist(update: Update, context: CallbackContext):
    reply = "<b>Known Tiger Disasters 🐯:</b>\n"
    m = update.effective_message.reply_text(
        "<code>Gathering intel..</code>",
        parse_mode=ParseMode.HTML,
    )
    bot = context.bot
    for each_user in TIGERS:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


@whitelist_plus
def supportlist(update: Update, context: CallbackContext):
    bot = context.bot
    m = update.effective_message.reply_text(
        "<code>Gathering intel..</code>",
        parse_mode=ParseMode.HTML,
    )
    reply = "<b>Known Demon Disasters 👹:</b>\n"
    for each_user in DEMONS:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


@whitelist_plus
def sudolist(update: Update, context: CallbackContext):
    bot = context.bot
    m = update.effective_message.reply_text(
        "<code>Gathering intel..</code>",
        parse_mode=ParseMode.HTML,
    )
    true_sudo = list(set(DRAGONS) - set(DEV_USERS))
    reply = "<b>Known Dragon Disasters 🐉:</b>\n"
    for each_user in true_sudo:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


@whitelist_plus
def devlist(update: Update, context: CallbackContext):
    bot = context.bot
    m = update.effective_message.reply_text(
        "<code>Gathering intel..</code>",
        parse_mode=ParseMode.HTML,
    )
    true_dev = list(set(DEV_USERS) - {OWNER_ID})
    reply = "<b>Hero Association Members ⚡️:</b>\n"
    for each_user in true_dev:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


SUDO_HANDLER = CommandHandler(("addsudo", "adddragon"), addsudo, run_async=True)
SUPPORT_HANDLER = CommandHandler(("addsupport", "adddemon"), addsupport, run_async=True)
TIGER_HANDLER = CommandHandler(("addtiger"), addtiger, run_async=True)
WHITELIST_HANDLER = CommandHandler(
    ("addwhitelist", "addwolf"), addwhitelist, run_async=True
)
UNSUDO_HANDLER = CommandHandler(
    ("removesudo", "removedragon"), removesudo, run_async=True
)
UNSUPPORT_HANDLER = CommandHandler(
    ("removesupport", "removedemon"), removesupport, run_async=True
)
UNTIGER_HANDLER = CommandHandler(("removetiger"), removetiger, run_async=True)
UNWHITELIST_HANDLER = CommandHandler(
    ("removewhitelist", "removewolf"), removewhitelist, run_async=True
)
WHITELISTLIST_HANDLER = CommandHandler(
    ["whitelistlist", "wolves"], whitelistlist, run_async=True
)
TIGERLIST_HANDLER = CommandHandler(["tigers"], tigerlist, run_async=True)
SUPPORTLIST_HANDLER = CommandHandler(
    ["supportlist", "demons"], supportlist, run_async=True
)
SUDOLIST_HANDLER = CommandHandler(["sudolist", "dragons"], sudolist, run_async=True)
DEVLIST_HANDLER = CommandHandler(["devlist", "heroes"], devlist, run_async=True)

dispatcher.add_handler(SUDO_HANDLER)
dispatcher.add_handler(SUPPORT_HANDLER)
dispatcher.add_handler(TIGER_HANDLER)
dispatcher.add_handler(WHITELIST_HANDLER)
dispatcher.add_handler(UNSUDO_HANDLER)
dispatcher.add_handler(UNSUPPORT_HANDLER)
dispatcher.add_handler(UNTIGER_HANDLER)
dispatcher.add_handler(UNWHITELIST_HANDLER)
dispatcher.add_handler(WHITELISTLIST_HANDLER)
dispatcher.add_handler(TIGERLIST_HANDLER)
dispatcher.add_handler(SUPPORTLIST_HANDLER)
dispatcher.add_handler(SUDOLIST_HANDLER)
dispatcher.add_handler(DEVLIST_HANDLER)

__mod_name__ = "Sudoers"
__handlers__ = [
    SUDO_HANDLER,
    SUPPORT_HANDLER,
    TIGER_HANDLER,
    WHITELIST_HANDLER,
    UNSUDO_HANDLER,
    UNSUPPORT_HANDLER,
    UNTIGER_HANDLER,
    UNWHITELIST_HANDLER,
    WHITELISTLIST_HANDLER,
    TIGERLIST_HANDLER,
    SUPPORTLIST_HANDLER,
    SUDOLIST_HANDLER,
    DEVLIST_HANDLER,
]
