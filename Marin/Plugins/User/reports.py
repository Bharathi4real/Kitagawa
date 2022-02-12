import os

from loguru import logger
from pyrogram import Client, filters
from pyrogram.errors import BadRequest
from pyrogram.types import Message


@Client.on_message(
    filters.command(['report', f'report@{os.environ.get("BOT_USERNAME")}'], ['/', '!']) |
    filters.command(['admin', 'admins'], '@') & ~filters.private,
    group=303
)
async def on_report(client: Client, message: Message):
    admins = client.iter_chat_members(message.chat.id, filter='administrators')
    if admins is None:
        await message.reply('Нешта пайшло не так. Калі ласка, паспрабуйце яшчэ раз ці пазней.')
        return
    async for admin in admins:
        if admin.user.is_self or admin.user.is_bot:
            continue
        try:
            await client.send_message(admin.user.id,
                                      f'Новая скарга з чата: '
                                      f'https://t.me/c/{message.chat.id * -1 - 1000000000000}/{message.message_id}')
        except BadRequest as e:
            logger.error(f'[{message.chat.id} ({message.message_id})] '
                         f'Tried to report to {admin.user.id} ({admin.user.username}), but got {e}')
    await message.reply('Перадана адміністратарам-людзям.')
    return
