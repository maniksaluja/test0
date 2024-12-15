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
    settings = await get_settings()
    res = await asyncio.gather(
        tryer(m.copy, DB_CHANNEL_ID),
        tryer(m.copy, DB_CHANNEL_2_ID)
    )
    count = await incr_count()
    encr = encrypt(f'{Int2Char(res[0].id)}|{Int2Char(count)}|{Int2Char(res[1].id)}')
    link = f'https://t.me/{(await get_me(_)).username}?start=get{encr}'
    if m.video:
        dur = "⋞⋮⋟ " + alpha_grt(m.video.duration)
    else:
        dur = ''
    txt = LINK_GEN.format(str(count), dur, link)
    
    # Add the download button and caption to forwarded messages
    markup = IKM([[IKB('Download', url=link)]])  # Download button
    
    # Forward message with custom caption and button
    if LINK_GENERATE_IMAGE and settings['image']:
        msg = await tryer(m.reply_photo, LINK_GENERATE_IMAGE, caption=f"Hello, this is your forwarded message.\n{txt}", reply_markup=markup)
    else:
        msg = await tryer(m.reply, f"Hello, this is your forwarded message.\n{txt}", reply_markup=markup)

    # Forward message to both DB channels
    if DB_CHANNEL_ID:
        await tryer(msg.copy, DB_CHANNEL_ID, caption="Hello, this is your forwarded message with download button.", reply_markup=markup)
    if DB_CHANNEL_2_ID:
        await tryer(msg.copy, DB_CHANNEL_2_ID, caption="Hello, this is your forwarded message with download button.", reply_markup=markup)
    
    # Log to log channel if necessary
    if LOG_CHANNEL_ID and settings.get('logs', True):
        await tryer(msg.copy, LOG_CHANNEL_ID)
