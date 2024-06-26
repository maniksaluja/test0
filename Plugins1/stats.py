from pyrogram import Client, filters
from config import SUDO_USERS
from Database.users import get_users_count_2
from Plugins import startTime, grt
from time import time

@Client.on_message(filters.command('users') & filters.user(SUDO_USERS))
async def users(_, m):
    count = await get_users_count_2()
    await m.reply(f'Users: {count}.')

@Client.on_message(filters.command('uptime') & filters.user(SUDO_USERS))
async def uptime(_, m):
    txt = 'Uptime: {}.'
    txt = txt.format(grt(int(time()-startTime)))
    await m.reply(txt)
