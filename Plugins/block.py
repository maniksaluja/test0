from config import SUDO_USERS
from pyrogram import Client, filters
from Database.block import *

@Client.on_message(filters.command('block') & filters.user(SUDO_USERS))
async def bl(_, m):
    try:
        id = int(m.text.split()[1])
    except:
        return await m.reply('Usage: /block user_id')
    if await is_blocked(id):
        return await m.reply('**This User Already BANNED.**')
    await block(id)
    await m.reply('**This User Can\'t Access Me Now ...**')

@Client.on_message(filters.command('unblock') & filters.user(SUDO_USERS))
async def unbl(_, m):
    try:
        id = int(m.text.split()[1])
    except:
        return await m.reply('Usage: /unblock user_id')
    if not await is_blocked(id):
        return await m.reply('**This User Have My Access...**')
    await unblock(id)
    await m.reply('**This User Can Use BOT ...**')

def block_dec(func):
    async def wrapper(_, m):
        if not m.from_user:
            return
        if await is_blocked(m.from_user.id):
            return
        return await func(_, m)
    return wrapper
