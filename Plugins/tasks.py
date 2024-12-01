from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM
from .encode_decode import decrypt, Char2Int
from config import DB_CHANNEL_ID, AUTO_DELETE_TIME, FSUB_1, FSUB_2, DB_CHANNEL_2_ID, TUTORIAL_LINK, CONTENT_SAVER, STICKER_ID
from time import time
from Database.auto_delete import update, get
from Database.privileges import get_privileges
from . import AUTO_DELETE_STR, tryer
from Database.users import add_user, is_user
from templates import AUTO_DELETE_TEXT, START_MESSAGE, START_MESSAGE_2, TRY_AGAIN_TEXT
from .block import block_dec
from Database.encr import get_encr
import asyncio
from main import app

# Cache for subscribed members
members = {FSUB_1: [], FSUB_2: []}  # {chat_id: [user_id]}

FSUB = [FSUB_1, FSUB_2]

# Function to track chat member updates (joined/left)
@Client.on_chat_member_updated(filters.chat(FSUB))
async def cmufunc(_, cmu):
    joined = cmu.new_chat_member and not cmu.old_chat_member
    left = cmu.old_chat_member and not cmu.new_chat_member
    if joined:
        members[cmu.chat.id].append(cmu.from_user.id)
    elif left:
        try:
            members[cmu.chat.id].remove(cmu.from_user.id)
        except:
            pass

# Check if the user has subscribed to all necessary channels
async def check_fsub(user_id: int) -> bool:
    for y in FSUB:
        if not user_id in members[y]:
            try:
                x = await tryer(app.get_chat_member, y, user_id)
                if not x.status.name in ["ADMINISTRATOR", "OWNER", "MEMBER"]:
                    return False
            except:
                return False
            members[y].append(user_id)
    return True

me = None
chats = []

# Function to fetch the necessary chat info and generate invite links
async def get_chats(_):
    global chats
    if not chats:
        chats = [await _.get_chat(FSUB_1), await _.get_chat(FSUB_2)]
        new = []
        for x in chats:
            y = await _.create_chat_invite_link(x.id, creates_join_request=True)
            new.append(y.invite_link)
        for x, y in enumerate(new):
            chats[x].invite_link = y
    return chats

# Generate keyboard markup for showing channel links
async def markup(_, link=None) -> IKM:
    chats = await get_chats(_)
    l = len(FSUB)
    mark = [
        IKB('ᴍᴀɪɴ ᴄʜᴀɴɴᴇʟ', url=chats[0].invite_link),
        IKB('ʙᴀᴄᴋᴜᴘ ᴄʜᴀɴɴᴇʟ', url=chats[1].invite_link)
    ]
    mark = [mark]
    if link:
        mark.append([IKB('ᴛʀʏ ᴀɢᴀɪɴ♻️', url=link)])
    markup = IKM(mark)
    return markup

# Main start function with permission and message handling
control_batch = []

@block_dec
async def start(_, m):
    global me, chats
    if not me:
        me = await _.get_me()
    user_id = m.from_user.id
    chats = await get_chats(_)
    
    # If user is not in the database, add them
    if not await is_user(m.from_user.id):
        await add_user(m.from_user.id)
        return await m.reply(START_MESSAGE.format(m.from_user.mention), reply_markup=await start_markup(_))

    # Check user privilege for content saver
    if CONTENT_SAVER:
        prem = (await get_privileges(m.from_user.id))[2]
    else:
        prem = True

    # Parsing command arguments
    txt = m.text.split()
    if len(txt) > 1:
        command = txt[1]
        
        # For 'get' command
        if command.startswith('get'):
            encr = command[3:]
            for i in chats:
                if not await check_fsub(m.from_user.id):
                    mark = await markup(_, f'https://t.me/{me.username}?start=get{encr}')
                    return await m.reply(TRY_AGAIN_TEXT.format(m.from_user.mention), reply_markup=mark)
            std = await m.reply_sticker(STICKER_ID)
            spl = decrypt(encr).split('|')
            try:
                msg = await _.get_messages(DB_CHANNEL_ID, Char2Int(spl[0]))
                if msg.empty:
                    msg = await _.get_messages(DB_CHANNEL_2_ID, Char2Int(spl[2]))
            except:
                msg = await _.get_messages(DB_CHANNEL_2_ID, Char2Int(spl[2]))
            await std.delete()
            if not prem:
                ok = await msg.copy(m.from_user.id, caption=None, reply_markup=None, protect_content=True)
            else:
                ok = await msg.copy(m.from_user.id, caption=None, reply_markup=None)
            if AUTO_DELETE_TIME != 0:
                ok1 = await ok.reply(AUTO_DELETE_TEXT.format(AUTO_DELETE_STR))
                dic = await get(m.from_user.id)
                dic[str(ok.id)] = [str(ok1.id), time(), f'https://t.me/{me.username}?start=get{encr}']
                await update(m.from_user.id, dic)
            return

        # For batchone command
        elif command.startswith('batchone'):
            encr = command[8:]
            for i in chats:
                if not await check_fsub(m.from_user.id):
                    mark = await markup(_, f'https://t.me/{me.username}?start=batchone{encr}')
                    return await m.reply(TRY_AGAIN_TEXT.format(m.from_user.mention), reply_markup=mark)
            await process_batch_command(_, m, encr, 'batchone')

        # For batchtwo command
        elif command.startswith('batchtwo'):
            encr = command[8:]
            for i in chats:
                if not await check_fsub(m.from_user.id):
                    mark = await markup(_, f'https://t.me/{me.username}?start=batchtwo{encr}')
                    return await m.reply(TRY_AGAIN_TEXT.format(m.from_user.mention), reply_markup=mark)
            await process_batch_command(_, m, encr, 'batchtwo')

    else:
        await m.reply(START_MESSAGE_2.format(m.from_user.mention), reply_markup=await start_markup(_))

# Function to process batch commands
async def process_batch_command(_, m, encr, batch_type):
    std = await m.reply_sticker(STICKER_ID)
    spl = decrypt(encr).split('|')[0].split('-')
    st = Char2Int(spl[0])
    en = Char2Int(spl[1])
    
    messes = await fetch_messages(st, en, batch_type)
    
    okkie = None
    if len(messes) > 10:
        okkie = await m.reply("**It's Take Few Seconds...**")

    haha = []
    for x in messes:
        if not x or x.empty:
            continue
        gg = await tryer(x.copy, m.from_user.id, caption=None, reply_markup=None)
        haha.append(gg)
        await asyncio.sleep(1)

    await std.delete()
    if AUTO_DELETE_TIME != 0:
        ok1 = await m.reply(AUTO_DELETE_TEXT.format(AUTO_DELETE_STR))
        dic = await get(m.from_user.id)
        for ok in haha:
            if ok:
                dic[str(ok.id)] = [str(ok1.id), time(), f'https://t.me/{me.username}?start={batch_type}{encr}']
        await update(m.from_user.id, dic)

    if okkie:
        await okkie.delete()

# Fetching messages based on batch
async def fetch_messages(st, en, batch_type):
    messes = []
    if st == en:
        messes = [await app.get_messages(DB_CHANNEL_2_ID, st)]
    else:
        mess_ids = []
        while en - st + 1 > 200:
            mess_ids.append(list(range(st, st + 200)))
            st += 200
        if en - st + 1 > 0:
            mess_ids.append(list(range(st, en+1)))
        for x in mess_ids:
