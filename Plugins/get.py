from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM
from Database.sessions import get_session
from Database.privileges import get_privileges
from config import (
    API_ID,
    API_HASH, 
    DB_CHANNEL_ID, 
    SUDO_USERS, 
    USELESS_IMAGE,
    AUTO_SAVE_CHANNEL_ID
)
from Database.settings import get_settings
import os
from pyrogram.errors import FloodWait
from . import tryer, AUTO_DELETE_STR
from Database.count_2 import incr_count_2
from Database.auto_delete_2 import update_2
from .encode_decode import *
from templates import LINK_GEN, AUTO_DELETE_TEXT, USELESS_MESSAGE
import time
from . import build
from main import ClientLike

markup = IKM([[IKB('𝘚𝘩𝘢𝘳𝘦 𝘞𝘪𝘵𝘩 𝘔𝘦', callback_data='sharewithme')]])

og = []

def dec(func):
    async def x(_, m):
        try:
            return await func(_, m)
        except:
            if m.from_user.id in og:
                og.remove(m.from_user.id)
            return 69
    return x

@dec
async def get(_, m):
  id = m.from_user.id
  if id in og:
    return await m.reply('**Wait Until Previous Download Finished.**')
  priv = await get_privileges(id)
  if not priv[1]:
    return await m.reply_photo(USELESS_IMAGE, caption=USELESS_MESSAGE, reply_markup=await build(_))
  session = await get_session(id)
  if not session:
    return await m.reply("**Before Use.You Have to Connect with Bot.For Connect Use: /connect **")
  try:
    if m.text.startswith("https://t.me/c"):
      channel = int("-100" + m.text.split("/")[-2])
      msg_id = int(m.text.split("/")[-1])
    elif m.text.startswith("https://t.me"):
      channel = m.text.split("/")[-2]
      msg_id = int(m.text.split("/")[-1])
  except:
    return await m.reply('Link Is Invalid..')
  cyapa = await m.reply('Under Processing...')
  try:
    app = ClientLike(str(id), api_id=API_ID, api_hash=API_HASH, session_string=session)
    await app.start()
  except FloodWait as e:
    return await cyapa.edit(f'Try Again After {e.value} seconds.')
  except:
    return await cyapa.edit('**Signal Lost\n\nType: /connect to restart.**')
  og.append(id)
  msg = await app.get_messages(channel, msg_id)
  settings = await get_settings()
  if msg.text:
    cop = await m.reply(msg.text, reply_markup=markup)
  else:
    try:
      dl = await msg.download()
      try:
        await app.stop()
      except ConnectionError:
        pass
      if msg.document:
        cop = await m.reply_document(dl, caption=msg.caption, reply_markup=markup)
      elif msg.video:
        cop = await m.reply_video(dl, caption=msg.caption, reply_markup=markup)
      elif msg.photo:
        cop = await m.reply_photo(dl, caption=msg.caption, reply_markup=markup)
      elif msg.animation:
        cop = await m.reply_animation(dl, caption=msg.caption, reply_markup=markup)
      else:
        return await cyapa.edit('This Link can\'t be accessed.')
      os.remove('downloads/' + dl.split('/')[-1])
    except Exception as e:
      og.remove(id)
      return await cyapa.edit(f'This Link can\'t be accessed due to: `{e}`')
  if settings['auto_save']:
    await cop.copy(AUTO_SAVE_CHANNEL_ID, reply_markup=None)
  count = await incr_count_2()
  ok = await m.reply(AUTO_DELETE_TEXT.format(AUTO_DELETE_STR))
  await update_2(id, [cop.id, ok.id, count, time.time()])
  await cyapa.delete()
  og.remove(id)
  return True

pbd = []

@Client.on_message(filters.command('batch') & ~filters.user(SUDO_USERS) & filters.private)
async def pbatch(_, m):
  id = m.from_user.id
  if id in pbd:
    return await m.reply("**Wait Until Previous Batch Gets Done.**")
  priv = await get_privileges(m.from_user.id)
  sets = await get_settings()
  if not priv[0]:
    return await m.reply_photo(USELESS_IMAGE, caption=USELESS_MESSAGE, reply_markup=await build(_))
  session = await get_session(id)
  if not session:
    return await m.reply("**Before Use.You Have to Connect with Bot.For Connect Use: /connect **")
  spl = m.text.split()
  try:
    link1 = spl[1]
  except:
    return await m.reply('Usage: /batch [starting_link] [ending_link]\n<pre>If you just give the startlink then the bot will automatically save a batch of 20 files.</pre>')
  try:
    link2 = spl[2]
  except:
    link2 = '/'.join(link1.split('/')[:-1]) + '/' + str(int(link1.split('/')[-1]) + 20)
  st = int(link1.split('/')[-1])
  en = int(link2.split('/')[-1]) + 1
  try:
    channel = int('-100' + link1.split('/')[-2])
  except:
    channel = link1.split('/')[-2]
  try:
    app = ClientLike(str(id), api_id=API_ID, api_hash=API_HASH, session_string=session)
    await app.start()
  except FloodWait as e:
    return await m.reply(f'Try Again After {e.value} seconds.')
  except:
    return await m.reply('**Signal Lost\nType: /connect to Restart..**')
  pbd.append(id)
  msges = await app.get_messages(channel, list(range(st, en)))
  dest_ids = []
  m_e = await tryer(m.reply, 'Processing Files...')
  tot = len(msges)
  DB_CHANNEL_ID = m.from_user.id
  for enu, msg in enumerate(msges, 1):
    if msg.text:
      cop = await tryer(_.send_message, DB_CHANNEL_ID, msg.text, reply_markup=markup)
    else:
      try:
        dl = await msg.download()
        if msg.document:
          cop = await tryer(_.send_document, DB_CHANNEL_ID, dl, caption=msg.caption, reply_markup=markup)
        elif msg.video:
          cop = await tryer(_.send_video, DB_CHANNEL_ID, dl, caption=msg.caption, reply_markup=markup)
        elif msg.photo:
          cop = await tryer(_.send_photo, DB_CHANNEL_ID, dl, caption=msg.caption, reply_markup=markup)
        elif msg.animation:
          cop = await tryer(_.send_animation, DB_CHANNEL_ID, dl, caption=msg.caption, reply_markup=markup)  
        os.remove('downloads/' + dl.split('/')[-1])
      except Exception as e:
        pass
    dest_ids.append(cop)
    await tryer(m_e.edit, f'Processing.. `{enu}/{tot}`...')
  await tryer(m_e.delete)
  try:
    await app.stop()
  except ConnectionError:
    pass
  count = await incr_count_2()
  ok = await m.reply(AUTO_DELETE_TEXT.format(AUTO_DELETE_STR))
  await update_2(id, [[x.id for x in dest_ids], ok.id, count, time.time()])
  pbd.remove(id) if id in pbd else None
  if sets['auto_save']:
    for x in dest_ids:
      await tryer(x.copy, AUTO_SAVE_CHANNEL_ID, reply_markup=None)
