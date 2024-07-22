from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup as IKM, InlineKeyboardButton as IKB
from config import SUDO_USERS, DB_CHANNEL_ID, DB_CHANNEL_2_ID, LOG_CHANNEL_ID, LINK_GENERATE_IMAGE
from .encode_decode import encrypt, Int2Char
from templates import LINK_GEN
from . import alpha_grt
from Database.count_2 import incr_count_2
from Database.count import incr_count
from Database.settings import get_settings
from Database.encr import update
from . import tryer
import asyncio

dic = {}

me = None

class bkl:
    @staticmethod
    def done():
        return True

TASK = bkl()

def get_TASK():
    return TASK.done()

async def get_me(client):
    global me
    if not me:
        me = await client.get_me()
    return me

def in_batch(user_id):
    return user_id in dic or not get_TASK()

@Client.on_message(filters.command('b') & filters.user(SUDO_USERS) & filters.private)
async def batch(client, message):
    if message.from_user.id in dic:
        return await message.reply('**Batch Under Process. Use /cancel to stop!**')
    if TASK and not TASK.done():
        return await message.reply('Wait until the current batch is done.')
    dic[message.from_user.id] = []
    await message.reply('**OK. You can now batch links. When done, use /end**', quote=True)

async def batch_cwf(client, message):
    if message.text and message.text.startswith('/'):
        return
    if message.from_user.id in dic:
        dic[message.from_user.id].append(message)

@Client.on_message(filters.command('cancel') & filters.user(SUDO_USERS) & filters.private)
async def cancel(client, message):
    if message.from_user.id not in dic:
        return await message.reply('Nothing to cancel.')
    dic.pop(message.from_user.id)
    await message.reply('Batch cancelled.')

async def process_batch_messages(client, messages, db_channel_id):
    dest_ids = []
    for msg in messages:
        new_msg = await tryer(msg.copy, db_channel_id, caption="#batch")
        dest_ids.append(new_msg.id)
    return dest_ids

async def end(client, message):
    if message.from_user.id not in dic:
        return
    ms = dic[message.from_user.id]
    dic.pop(message.from_user.id)
    if not ms:
        return
    iffff = await message.reply("**Processing... This might take a few minutes.**")
    
    tasks = [
        process_batch_messages(client, ms, DB_CHANNEL_ID),
        process_batch_messages(client, ms, DB_CHANNEL_2_ID)
    ]
    
    dest_ids, dest_ids_2 = await asyncio.gather(*tasks)
    
    all_vid = all(x.video for x in ms)
    duration = "⋞⋮⋟" + alpha_grt(sum(x.video.duration for x in ms)) if all_vid else ''
    
    cur = await incr_count()
    encr = encrypt(f'{Int2Char(dest_ids[0])}-{Int2Char(dest_ids[-1])}|{Int2Char(cur)}')
    encr_2 = encrypt(f'{Int2Char(dest_ids_2[0])}-{Int2Char(dest_ids_2[-1])}|{Int2Char(cur)}')
    await update(encr, encr_2)
    
    link = f'https://t.me/{(await get_me(client)).username}?start=batchone{encr}'
    txt = LINK_GEN.format(f'{cur}', duration, link)
    markup = IKM([[IKB('Share', url=link)]])
    
    settings = await get_settings()
    await iffff.delete()
    
    if LINK_GENERATE_IMAGE and settings['image']:
        await message.reply_photo(LINK_GENERATE_IMAGE, caption=txt, reply_markup=markup, quote=True)
        if LOG_CHANNEL_ID and settings.get('logs', True):
            await client.send_photo(LOG_CHANNEL_ID, LINK_GENERATE_IMAGE, caption=txt, reply_markup=markup)
    else:
        await message.reply(txt, reply_markup=markup, quote=True)
        if LOG_CHANNEL_ID and settings.get('logs', True):
            await client.send_message(LOG_CHANNEL_ID, txt, reply_markup=markup)

@Client.on_message(filters.command('end') & filters.user(SUDO_USERS) & filters.private)
async def endddd(client, message):
    global TASK
    TASK = asyncio.create_task(end(client, message))
    await TASK

@Client.on_message(filters.private)
async def handle_private_messages(client, message):
    await batch_cwf(client, message)