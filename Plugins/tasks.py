from Database.auto_delete import get, update, get_all
from pyrogram.types import InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM
from config import AUTO_DELETE_TIME
import asyncio
from time import time
from main import app
from .encode_decode import decrypt, Char2Int
from templates import POST_DELETE_TEXT
from pyrogram.errors import FloodWait
from . import tryer

async def process_message(chat_id, message_id, edit_id, count, url):
    butt = IKM([[IKB('ᴡᴀᴛᴄʜ ᴀɢᴀɪɴ', url=url)]])
    txt = POST_DELETE_TEXT.format(count)
    try:
        await tryer(app.delete_messages, chat_id, message_id)
        await tryer(app.edit_message_text, chat_id, edit_id, txt, reply_markup=butt)
    except FloodWait as e:
        print(f"FloodWait: Sleeping for {e.x} seconds for chat {chat_id}")
        await asyncio.sleep(e.x)
    except Exception as e:
        print(f"Error deleting/editing message in chat {chat_id}: {e}")

async def task():
    if AUTO_DELETE_TIME == 0:
        return
    while True:
        try:
            x = await get_all()
            tasks = []
            for i in x:
                dic = await get(i)
                to_del = []
                for z in dic:
                    delete_time = dic[z][1] + AUTO_DELETE_TIME
                    if int(time()) >= delete_time:
                        id_to_del = int(z)
                        id_to_edit = int(dic[z][0])
                        if 'get' in dic[z][2]:
                            count = Char2Int(decrypt(dic[z][2].split('get')[1]).split('|')[1])
                        else:
                            count = Char2Int(decrypt(dic[z][2].split('batch')[1][3:]).split('|')[1])
                        tasks.append(process_message(i, id_to_del, id_to_edit, count, dic[z][2]))
                        to_del.append(z)
                for to_d in to_del:
                    del dic[to_d]
                await update(i, dic)
            await asyncio.gather(*tasks)
        except Exception as e:
            print(f"Error in task loop: {e}")

        await asyncio.sleep(60)  # Check every 60 seconds

asyncio.create_task(task())