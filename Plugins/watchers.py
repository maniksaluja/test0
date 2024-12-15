from pyrogram import Client, filters
from pyrogram.types import (
    Message, InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM
)
from config import (
    SUDO_USERS, DB_CHANNEL_ID, DB_CHANNEL_2_ID,
    LOG_CHANNEL_ID, LINK_GENERATE_IMAGE,
    USELESS_IMAGE,
    TUTORIAL_LINK
)
from templates import USELESS_MESSAGE, LINK_GEN
from .encode_decode import encrypt, Int2Char
from Database.count import incr_count
from Database.settings import get_settings
from .batch import in_batch, batch_cwf as bcwf
from .block import block_dec
from . import alpha_grt, tryer
from pyrogram.errors import FloodWait
import threading
import asyncio
from .connect import in_work
from .get import get
from . import build

watch = 1

me = None
async def get_me(_):
    global me
    if not me:
        me = await _.get_me()
    return me

@Client.on_message(filters.private, group=watch)
@block_dec
async def cwf(_: Client, m: Message):
    if in_work(m.from_user.id):
        return
    if in_batch(m.from_user.id):
        return await bcwf(_, m)
    if m.text and m.text.startswith("https://t.me/"):
        ret = await get(_, m)
        if ret:
            return
    if not m.from_user.id in SUDO_USERS:
        if m.text:
            if not m.text.lower().startswith(('/start', '/terminate', '/connect', '/bot', '..', '/batch', '/id')):
                markup = await build(_)
                if USELESS_IMAGE:
                    await m.reply_photo(USELESS_IMAGE, caption=USELESS_MESSAGE, reply_markup=markup)
                else:
                    await m.reply(USELESS_MESSAGE, reply_markup=markup)
        else:
            markup = await build(_)
            if USELESS_IMAGE:
                await m.reply_photo(USELESS_IMAGE, caption=USELESS_MESSAGE, reply_markup=markup)
            else:
                await m.reply(USELESS_MESSAGE, reply_markup=markup)
        return
    if m.text and m.text.startswith('/'):
        return
    
    # Getting settings and message information
    settings = await get_settings()
    if not m.sticker:
        return
    
    # Forwarding message to DB_CHANNEL_ID and DB_CHANNEL_2_ID
    res = await asyncio.gather(
        tryer(m.copy, DB_CHANNEL_ID),
        tryer(m.copy, DB_CHANNEL_2_ID)
    )
    
    # Creating the caption and "Download" button
    caption = "Test Hello"  # Custom caption text
    download_button = IKB("Download", callback_data="download")  # Creating download button
    markup = IKM([[download_button]])  # Creating inline keyboard with the button

    # Forwarding the sticker message to both DB channels with the caption and download button
    await tryer(res[0].edit_caption, caption=caption, reply_markup=markup)  # For DB_CHANNEL_ID
    await tryer(res[1].edit_caption, caption=caption, reply_markup=markup)  # For DB_CHANNEL_2_ID

    # Incrementing the count and creating encrypted link
    count = await incr_count()
    encr = encrypt(f'{Int2Char(res[0].id)}|{Int2Char(count)}|{Int2Char(res[1].id)}')
    link = f'https://t.me/{(await get_me(_)).username}?start=get{encr}'

    # Handling additional message for the user
    if LOG_CHANNEL_ID and settings.get('logs', True):
        await tryer(res[0].copy, LOG_CHANNEL_ID)  # Forwarding to log channel if enabled
