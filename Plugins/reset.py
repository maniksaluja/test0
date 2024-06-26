from pyrogram import Client, filters
from config import SUDO_USERS
from Database.count import reset_count
from Database.count_2 import reset_count_2
from Database import db
from time import time

@Client.on_message(filters.command('reset') & filters.user(SUDO_USERS))
async def reset(_, m):
  await reset_count()
  await reset_count_2()
  await m.reply(' **Count has been reset....** ')

confirm = False
t = time()

@Client.on_message(filters.command('resets') & filters.user(SUDO_USERS))
async def resets(_, m):
  global confirm, t
  if int(time()-t) > 30:
    confirm = False
  if not confirm:
    confirm = True
    t = time()
    return await m.reply('Are You Sure? You are Doing Reset\nBot Settings if Yes Than Type Again!!..')
  collections = await db.list_collection_names()
  for x in collections:
    if 'count' in x or 'users' in x:
      continue
    await db[x].drop()
  await m.reply('DB Formatted.')
