from Database.users import get_users_2, del_user_2
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from config import SUDO_USERS
import asyncio

REPLY_ERROR = """<code>Use this command as a reply to any telegram message without any spaces.</code>"""

@Client.on_message(filters.private & filters.command('bt') & filters.user(SUDO_USERS))
async def send_text(client, message):
    if message.reply_to_message:
        query = await get_users_2()
        broadcast_msg = message.reply_to_message
        total = len(query)
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0
        
        pls_wait = await message.reply("<i>Broadcasting Message... This will take some time</i>")
        err = None
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                try:
                    await broadcast_msg.copy(chat_id)
                    successful += 1
                except UserIsBlocked:
                    await del_user_2(chat_id)
                    blocked += 1
                    continue  # Skip to the next user
                except InputUserDeactivated:
                    await del_user_2(chat_id)
                    deleted += 1
                    continue  # Skip to the next user
                except Exception as e:
                    unsuccessful += 1
                    err = e
            except UserIsBlocked:
                await del_user_2(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user_2(chat_id)
                deleted += 1
            except Exception as e:
                unsuccessful += 1
                err = e
        
        status = f"""<b><u>Broadcast Completed</u></b>
        
Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>

Error: {err}"""
        
        return await pls_wait.edit(status)

    else:
        msg = await message.reply(REPLY_ERROR)
        await asyncio.sleep(8)
        await msg.delete()