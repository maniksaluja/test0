from Database.auto_delete import get, update, get_all
from pyrogram.types import InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM
from config import AUTO_DELETE_TIME
import asyncio
from time import time
from main import app
from .encode_decode import decrypt, Char2Int
from templates import POST_DELETE_TEXT
from . import tryer

async def auto_delete_task():
    """
    Task that automatically deletes messages after a specified time.
    """
    if AUTO_DELETE_TIME == 0:
        return

    while True:
        users = await get_all()
        for user_id in users:
            user_settings = await get(user_id)
            to_delete = []
            for msg_id, msg_info in user_settings.items():
                timestamp = msg_info[1]
                if int(time() - timestamp) >= AUTO_DELETE_TIME:
                    message_id_to_delete = int(msg_id)
                    message_id_to_edit = int(msg_info[0])
                    button = IKM([[IKB('ᴡᴀᴛᴄʜ ᴀɢᴀɪɴ', url=msg_info[2])]])

                    if 'get' in msg_info[2]:
                        count = Char2Int(decrypt(msg_info[2].split('get')[1]).split('|')[1])
                    else:
                        count = Char2Int(decrypt(msg_info[2].split('batch')[1][3:]).split('|')[1])

                    delete_text = POST_DELETE_TEXT.format(count)
                    to_delete.append(msg_id)
                    try:
                        await tryer(app.delete_messages, user_id, message_id_to_delete)
                        await tryer(app.edit_message_text, user_id, message_id_to_edit, delete_text, reply_markup=button)
                    except Exception:
                        pass

            for msg_id in to_delete:
                del user_settings[msg_id]

            await update(user_id, user_settings)

        await asyncio.sleep(1)

asyncio.create_task(auto_delete_task())
