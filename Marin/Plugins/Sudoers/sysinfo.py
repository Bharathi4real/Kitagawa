import datetime
import platform
import time
from platform import python_version

import requests
import speedtest
import telegram
from psutil import cpu_percent, virtual_memory, disk_usage, boot_time
from telegram import ParseMode, Update
from telegram.ext import CommandHandler, Filters, CallbackContext

from Marin import dispatcher, OWNER_ID
from Marin.Handlers.alternate import typing_action
from Marin.Handlers.filters import CustomFilters


@typing_action
def ping(update: Update, _):
    msg = update.effective_message
    start_time = time.time()
    message = msg.reply_text("Pinging...")
    end_time = time.time()
    ping_time = round((end_time - start_time) * 1000, 3)
    message.edit_text(
        "*PONG!!!*\n`{}ms`".format(ping_time), parse_mode=ParseMode.MARKDOWN
    )


# Kanged from PaperPlane Extended userbot
def speed_convert(size):
    """
    Hi human, you can't read bytes?
    """
    power = 2**10
    zero = 0
    units = {0: "", 1: "Kb/s", 2: "Mb/s", 3: "Gb/s", 4: "Tb/s"}
    while size > power:
        size /= power
        zero += 1
    return f"{round(size, 2)} {units[zero]}"


@typing_action
def get_bot_ip(update, _):
    """Sends the bot's IP address, so as to be able to ssh in if necessary.
    OWNER ONLY.
    """
    res = requests.get("http://ipinfo.io/ip")
    update.message.reply_text(res.text)


@typing_action
def speedtst(update: Update, context: CallbackContext):
    message = update.effective_message
    ed_msg = message.reply_text("Running speed test . . .")
    test = speedtest.Speedtest()
    test.get_best_server()
    test.download()
    test.upload()
    test.results.share()
    result = test.results.dict()
    context.bot.editMessageText(
        "Download "
        f"{speed_convert(result['download'])} \n"
        "Upload "
        f"{speed_convert(result['upload'])} \n"
        "Ping "
        f"{result['ping']} \n"
        "ISP "
        f"{result['client']['isp']}",
        update.effective_chat.id,
        ed_msg.message_id,
    )


@typing_action
def system_status(update: Update, context: CallbackContext):
    uptime = datetime.datetime.fromtimestamp(boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    status = "<b> System Info 🔧 </b>\n\n"
    status += "<b>⚙️ Uptime:</b> <code>" + str(uptime) + "</code>\n\n"

    uname = platform.uname()
    status += "<b>    ‣ 𝚂𝚢𝚜𝚝𝚎𝚖 :</b> <code>" + str(uname.system) + "</code>\n"
    status += "<b>    ‣ 𝚁𝚎𝚕𝚎𝚊𝚜𝚎 :</b> <code>" + str(uname.release) + "</code>\n"
    status += "<b>    ‣ 𝙼𝚊𝚌𝚑𝚒𝚗𝚎 :</b> <code>" + str(uname.machine) + "</code>\n"
    status += "<b>    ‣ 𝙿𝚛𝚘𝚌𝚎𝚜𝚜𝚘𝚛 :</b> <code>" + str(uname.processor) + "</code>\n"
    status += "<b>    ‣ 𝙽𝚘𝚍𝚎 𝚗𝚊𝚖𝚎 :</b> <code>" + str(uname.node) + "</code>\n"
    status += "<b>    ‣ 𝚅𝚎𝚛𝚜𝚒𝚘𝚗 :</b> <code>" + str(uname.version) + "</code>\n\n"

    mem = virtual_memory()
    cpu = cpu_percent()
    disk = disk_usage("/")
    status += "<b>    ‣ 𝙲𝙿𝚄 𝚞𝚜𝚊𝚐𝚎 :</b> <code>" + str(cpu) + " %</code>\n"
    status += "<b>    ‣ 𝚁𝚊𝚖 𝚞𝚜𝚊𝚐𝚎 :</b> <code>" + str(mem[2]) + " %</code>\n"
    status += "<b>    ‣ 𝚂𝚝𝚘𝚛𝚊𝚐𝚎 𝚞𝚜𝚎𝚍 :</b> <code>" + str(disk[3]) + " %</code>\n\n"
    status += "<b>    ‣ 𝙿𝚢𝚝𝚑𝚘𝚗 𝚟𝚎𝚛𝚜𝚒𝚘𝚗 :</b> <code>" + python_version() + "</code>\n"
    status += (
        "<b>    ‣ 𝙻𝚒𝚋𝚛𝚊𝚛𝚢 𝚟𝚎𝚛𝚜𝚒𝚘𝚗 :</b> <code>"
        + str(telegram.__version__)
        + "</code>\n"
    )
    update.message.reply_text(
        status, update.effective_chat.id, parse_mode=ParseMode.HTML
    )


IP_HANDLER = CommandHandler(
    "ip", get_bot_ip, filters=Filters.chat(OWNER_ID), run_async=True
)
PING_HANDLER = CommandHandler(
    "ping", ping, filters=CustomFilters.support_filter, run_async=True
)
SPEED_HANDLER = CommandHandler(
    "speedtest", speedtst, filters=CustomFilters.support_filter, run_async=True
)
SYS_STATUS_HANDLER = CommandHandler(
    "sysinfo", system_status, filters=CustomFilters.support_filter, run_async=True
)

dispatcher.add_handler(IP_HANDLER)
dispatcher.add_handler(SPEED_HANDLER)
dispatcher.add_handler(PING_HANDLER)
dispatcher.add_handler(SYS_STATUS_HANDLER)

__help__ = """Get Marin's System Infos

‣ /ip : get Marin's Ip.
‣ /ping : get Marin's server ping.
‣ /speedtest : get Marin's Ul and Dl speed information.
‣ /sysinfo : get Marins overall System Info."""

__mod_name__ = "Sys Info"
