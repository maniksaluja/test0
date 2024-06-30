from Database.auto_delete import get, update, get_all, db
from pyrogram.types import InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM
from config import AUTO_DELETE_TIME
import asyncio
from time import time
from main import app
from .encode_decode import decrypt, Char2Int
from templates import POST_DELETE_TEXT

async def task():
    if AUTO_DELETE_TIME == 0:
        return
    while True:
        x = await get_all()
        for i in x:
            dic = await get(i)
            to_del = []
            for z in dic:
                then = dic[z][1]
                if int(time()-then) >= AUTO_DELETE_TIME:
                    id_to_del = int(z)
                    id_to_edit = int(dic[z][0])
                    butt = IKM([[IKB('ᴡᴀᴛᴄʜ ᴀɢᴀɪɴ', url=dic[z][2])]])
                    if 'get' in dic[z][2]:
                        count = Char2Int(decrypt(dic[z][2].split('get')[1]).split('|')[1])
                    else:
                        count = Char2Int(decrypt(dic[z][2].split('batch')[1][3:]).split('|')[1])
                    txt = POST_DELETE_TEXT.format(count)
                    print(txt)
                    to_del.append(z)
                    try:
                        await app.delete_messages(i, id_to_del),
                        await app.edit_message_text(i, id_to_edit, txt, reply_markup=butt)
                    except:
                        pass
            for to_d in to_del:
                del dic[to_d]
            await update(i, dic)
        await asyncio.sleep(1)

asyncio.create_task(task())
