watch = 69

from pyrogram import Client, filters
from config import SUDO_USERS
from Database.users import add_user_2

@Client.on_message(filters.private, group=watch)
async def cwf(_, m):
    if m.from_user and m.from_user.id in SUDO_USERS:
        return await add_user_2(m.from_user.id)
    await m.reply("**Have Any Queries? @CuteGirlTG**")
    await add_user_2(m.from_user.id)
