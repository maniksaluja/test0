from pyrogram import Client, filters
from Database.sessions import get_session
from pyrogram.types import InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM
from Database.privileges import get_privileges
from config import API_HASH, API_ID, AUTO_DELETE_TIME, AUTO_SAVE_CHANNEL_ID, WARN_IMAGE
from pyrogram.errors import FloodWait
from Database.settings import get_settings
import os
from pyrogram.handlers import MessageHandler
from main import app as paa, ClientLike
import asyncio
from Database.auto_delete_2 import update_2, get_all_2, get_2
from templates import AUTO_DELETE_TEXT, POST_DELETE_TEXT, USELESS_MESSAGE
from . import AUTO_DELETE_STR, tryer, build
from Database.count_2 import incr_count_2
import time
from config import USELESS_IMAGE

async def stop(c):
    try:
        await c.stop()
    except ConnectionError:
        pass

TEMPL = '''┏━━━━━𓆩𝘌𝘳𝘳𝘰𝘳 𝘍𝘰𝘶𝘯𝘥𓆪ꪾ━━━━━┓
♛ 𝙃𝙚𝙮 𝙏𝙂 𝙐𝙨𝙚𝙧 : {}

≼𝗪𝗔𝗥𝗡𝗜𝗡𝗚 𝗔𝗟𝗘𝗥𝗧≽
➤**You are Not eligible To Save BOT 
Content ....

➤If You Try To Save Again, Your 
Membership Will Be Dead...**
┗━━━━━━𓆩𝘛𝘦𝘳𝘢𝘉𝘰𝘹𓆪ꪾ━━━━━━┛'''

markup = IKM([[IKB('𝘚𝘩𝘢𝘳𝘦 𝘞𝘪𝘵𝘩 𝘔𝘦', callback_data='sharewithme')]])
global_app = {}
me = None
bots = {}
async def save(C, M):
    if not M.chat.id in bots:
        bots[M.chat.id] = (await tryer(C.get_users, M.chat.id)).is_bot
    global me
    if not me:
        me = await paa.get_me()
    priv = await get_privileges(M.from_user.id)
    if not priv[2]:
        if M.chat.id == me.id:
            return await paa.send_photo(M.from_user.id, WARN_IMAGE, caption=TEMPL.format(M.from_user.mention))
    dm = not bots[M.chat.id]
    if not priv[3]:
        if dm:
            return await tryer(M.delete)
    try:
        count = int(M.text.split()[1])
    except:
        count = 1
    if count > 20:
        return await M.edit('Limit is 20.')
    if not M.reply_to_message:
        return await M.edit('Reply to a file to save.')
    settings = await get_settings()
    st = M.reply_to_message.id
    en = st + count
    messes = await C.get_messages(M.chat.id, list(range(st, en)))
    count = await incr_count_2()
    cops = []
    uffie = await tryer(paa.send_message, M.from_user.id, 'Under processing...')
    for msg in messes:
        if not msg or msg.empty:
            continue 
        if msg.from_user.id == M.from_user.id:
            continue
        if msg.text:
            await uffie.delete()
            cop = await paa.send_message(M.from_user.id, msg.text, reply_markup=markup)
        else:
            if dm:
                if not msg.caption:
                    msg.caption = '#DM'
                else:
                    msg.caption = '#DM\n ' + msg.caption
            try:
                dl = await msg.download()
                await uffie.delete()
                if msg.document:
                    cop = await paa.send_document(M.from_user.id, dl, caption=msg.caption, reply_markup=markup)
                elif msg.video:
                    cop = await paa.send_video(M.from_user.id, dl, caption=msg.caption, reply_markup=markup)
                elif msg.photo:
                    cop = await paa.send_photo(M.from_user.id, dl, caption=msg.caption, reply_markup=markup)
                elif msg.animation:
                    cop = await paa.send_animation(M.from_user.id, dl, caption=msg.caption, reply_markup=markup)
                os.remove('downloads/' + dl.split('/')[-1])
            except:
                pass
        if settings['auto_save']:
            await cop.copy(AUTO_SAVE_CHANNEL_ID, reply_markup=None)
        cops.append(cop.id)
    ok = await paa.send_message(M.from_user.id, AUTO_DELETE_TEXT.format(AUTO_DELETE_STR))
    await update_2(M.from_user.id, [cops, ok.id, count, time.time()])
    
    # await stop(global_app[M.from_user.id])

@Client.on_message(filters.command('bot'))
async def bot(_, m):
    id = m.from_user.id
    priv = await get_privileges(id)
    if not priv[1]:
        return await tryer(m.reply_photo, USELESS_IMAGE, caption=USELESS_MESSAGE, reply_markup=await build(_))
    session = await get_session(id)
    if not session:
        return await m.reply("**Before Use.You Have to Connect with Bot.For Connect Use: /connect **")
    try:
        app = ClientLike(str(id), api_id=API_ID, api_hash=API_HASH, session_string=session)
        await app.start()
        global_app[id] = app
        await m.reply('**UBot Activated\nUse  `..`  To Save Other Bot Content Or User DM Content.**')
        app.add_handler(MessageHandler(save, (filters.command('.', '.') & filters.me)))
        await asyncio.sleep(300)
        try:
            await app.stop()
            await tryer(m.reply, '**UBot Deactivate..**')
        except ConnectionError:
            pass
    except FloodWait as e:
        return await m.reply(f'Try Again After {e.value} seconds.')
    except:
        return await m.reply('Session Expired.')
    
async def task():
    while True:
        x = await get_all_2()
        for y in x:
            lis = await get_2(y)
            if not lis:
                continue
            if int(time.time()-lis[3]) < AUTO_DELETE_TIME:
                continue
            await tryer(paa.delete_messages, y, lis[0])
            try:
                await tryer(paa.edit_message_text, y, lis[1], POST_DELETE_TEXT.format(lis[2]))
            except:
                pass
            await update_2(y, [])
        await asyncio.sleep(10)

asyncio.create_task(task())
