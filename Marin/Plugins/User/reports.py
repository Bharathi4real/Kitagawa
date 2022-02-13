import os

from loguru import logger
from pyrogram import filters
from pyrogram.errors import BadRequest
from pyrogram.types import Message
from Marin import client

@Client.on_message(
    filters.command(['report', f'report@MarinAnimeBot'], ['/', '!']) |
    filters.command(['admin', 'admins'], '@') & ~filters.private,
    group=303
)
async def on_report(client: Client, message: Message):
    admins = client.iter_chat_members(message.chat.id, filter='administrators')
    if admins is None:
        await message.reply('Something went wrong. Please try again later.')
        return
    async for admin in admins:
        if admin.user.is_self or admin.user.is_bot:
            continue
        try:
            await client.send_message(admin.user.id,
                                      f'New Report from the chat: '
                                      f'https://t.me/c/{message.chat.id * -1 - 1000000000000}/{message.message_id}')
        except BadRequest as e:
            logger.error(f'[{message.chat.id} ({message.message_id})] '
                         f'Tried to report to {admin.user.id} ({admin.user.username}), but got {e}')
    await message.reply('Reported to Admins.')
    return
