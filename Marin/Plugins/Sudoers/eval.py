import ast
import subprocess
import os, logging, asyncio, io, sys, traceback
import textwrap
import traceback
from contextlib import redirect_stdout

from telegram import ParseMode, Update
from telegram.ext import CallbackContext, CommandHandler

from Marin import LOGGER, dispatcher
from Marin.Handlers.validation import dev_plus

from Marin import telethn as client

from datetime import datetime
from os import environ, execle
from telethon.sync import events

namespaces = {}


def namespace_of(chat, update, bot):
    if chat not in namespaces:
        namespaces[chat] = {
            "__builtins__": globals()["__builtins__"],
            "bot": bot,
            "effective_message": update.effective_message,
            "effective_user": update.effective_user,
            "effective_chat": update.effective_chat,
            "update": update,
        }

    return namespaces[chat]


def log_input(update):
    user = update.effective_user.id
    chat = update.effective_chat.id
    LOGGER.info(f"IN: {update.effective_message.text} (user={user}, chat={chat})")


def send(msg, bot, update):
    if len(str(msg)) > 2000:
        with io.BytesIO(str.encode(msg)) as out_file:
            out_file.name = "output.txt"
            bot.send_document(chat_id=update.effective_chat.id, document=out_file)
    else:
        LOGGER.info(f"OUT: '{msg}'")
        bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"<b>Result</b>:\n<code>{msg}</code>",
            parse_mode=ParseMode.HTML,
        )


@dev_plus
def evaluate(update: Update, context: CallbackContext):
    bot = context.bot
    send(do(eval, bot, update), bot, update)


@dev_plus
def execute(update: Update, context: CallbackContext):
    bot = context.bot
    send(do(exec, bot, update), bot, update)


def cleanup_code(code):
    if code.startswith("```") and code.endswith("```"):
        return "\n".join(code.split("\n")[1:-1])
    return code.strip("` \n")


def do(func, bot, update):
    log_input(update)
    content = update.message.text.split(" ", 1)[-1]
    body = cleanup_code(content)
    env = namespace_of(update.message.chat_id, update, bot)

    os.chdir(os.getcwd())
    with open(
        os.path.join(os.getcwd(), "Marin/Handlers/temp.txt"),
        "w",
    ) as temp:
        temp.write(body)

    stdout = io.StringIO()

    to_compile = f'def func():\n{textwrap.indent(body, "  ")}'

    try:
        exec(to_compile, env)
    except Exception as e:
        return f"{e.__class__.__name__}: {e}"

    func = env["func"]

    try:
        with redirect_stdout(stdout):
            func_return = func()
    except Exception:
        value = stdout.getvalue()
        return f"{value}{traceback.format_exc()}"
    else:
        value = stdout.getvalue()
        result = None
        if func_return is None:
            if value:
                result = f"{value}"
            else:
                try:
                    result = f"{repr(ast.literal_eval(body, env))}"
                except:
                    pass
        else:
            result = f"{value}{func_return}"
        if result:
            return result


@dev_plus
def shell(update: Update, context: CallbackContext):
    message = update.effective_message
    cmd = message.text.split(" ", 1)
    if len(cmd) == 1:
        message.reply_text("No command to execute was given.")
        return
    cmd = cmd[1]
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    stdout, stderr = process.communicate()
    reply = ""
    stderr = stderr.decode()
    if stdout := stdout.decode():
        reply += f"*Stdout*\n`{stdout}`\n"
        LOGGER.info(f"Shell - {cmd} - {stdout}")
    if stderr:
        reply += f"*Stderr*\n`{stderr}`\n"
        LOGGER.error(f"Shell - {cmd} - {stderr}")
    if len(reply) > 3000:
        with open("shell_output.txt", "w") as file:
            file.write(reply)
        with open("shell_output.txt", "rb") as doc:
            context.bot.send_document(
                document=doc,
                filename=doc.name,
                reply_to_message_id=message.message_id,
                chat_id=message.chat_id,
            )
    else:
        message.reply_text(reply, parse_mode=ParseMode.MARKDOWN)


@dev_plus
def clear(update: Update, context: CallbackContext):
    bot = context.bot
    log_input(update)
    global namespaces
    if update.message.chat_id in namespaces:
        del namespaces[update.message.chat_id]
    send("Cleared locals.", bot, update)


# telethon eval
TEVAL_AUTH = list(5161578942, 5161578942)


@client.on(events.NewMessage(from_users=[TEVAL_AUTH], pattern="^/te ?(.*)"))
async def eval(event):
    if event.fwd_from:
        return
    cmd = "".join(event.message.message.split(maxsplit=1)[1:])
    if not cmd:
        return
    catevent = await client.send_message(event.chat.id, "`Running ...`", reply_to=event)
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, event)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    final_output = f"**•  Eval : **\n`{cmd}` \n\n**•  Result : **\n`{evaluation}` \n"
    MAX_MESSAGE_SIZE_LIMIT = 4095
    if len(final_output) > MAX_MESSAGE_SIZE_LIMIT:
        with io.BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "eval.text"
            await client.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                caption=cmd,
            )
    else:
        await catevent.edit(final_output)


async def aexec(code, smessatatus):
    message = event = smessatatus

    def p(_x):
        return print(slitu.yaml_format(_x))

    reply = await event.get_reply_message()
    exec(
        "async def __aexec(message, reply, client, p): "
        + "\n event = smessatatus = message"
        + "".join(f"\n {l}" for l in code.split("\n"))
    )
    return await locals()["__aexec"](message, reply, client, p)


EVAL_HANDLER = CommandHandler(
    ("e", "ev", "eva", "eval"),
    evaluate,
    run_async=True,
)
EXEC_HANDLER = CommandHandler(
    ("x", "ex", "exe", "exec", "py"),
    execute,
    run_async=True,
)
SHELL_HANDLER = CommandHandler(["sh"], shell, run_async=True)

CLEAR_HANDLER = CommandHandler("clearlocals", clear, run_async=True)

dispatcher.add_handler(EVAL_HANDLER)
dispatcher.add_handler(EXEC_HANDLER)
dispatcher.add_handler(CLEAR_HANDLER)
dispatcher.add_handler(SHELL_HANDLER)

__help__ = """
*The Following commands are Developer Restricted*
× /sh
× /ev
× /py
× /Clearlocals
"""
__mod_name__ = "Evals"
