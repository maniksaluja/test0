"""
from pyrogram import Client, filters
from config import FSUB
from Database.settings import get_settings

@Client.on_chat_join_request(filters.chat(FSUB))
async def cjr(_: Client, r):
    if not (await get_settings())['auto_approval']:
        return
    await _.approve_chat_join_request(
        r.chat.id,
        r.from_user.id
    )
    await _.send_message(r.from_user.id, "Hi")
"""
