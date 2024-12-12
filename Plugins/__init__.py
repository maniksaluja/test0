from time import time
import asyncio
from pyrogram.errors import FloodWait
from pyrogram.types import (
    Message, InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM
)
from config import TUTORIAL_LINK

# Improved retry mechanism with async handling
async def tryer(func, *args, **kwargs):
    try:
        return await func(*args, **kwargs)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await func(*args, **kwargs)
    except Exception as e:
        print(f"Error: {e}")
        return None

def grt(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}S"
    if seconds < 3600:
        return f"{int(seconds/60)}M"
    return f"{int(seconds/3600)}H"
    
def alpha_grt(sec: int) -> str:
    if sec < 60:
        return f"{sec}S"
    if sec < 3600:
        return f"{int(sec/60)}M"
    return "60M+"

from config import AUTO_DELETE_TIME
AUTO_DELETE_STR = grt(AUTO_DELETE_TIME)

startTime = time()

from .start import get_chats

markup = None

async def build(_):
    global markup
    if not markup:
        chats = await get_chats(_)
        new = []
        # Using asyncio.gather to process multiple invite links concurrently
        tasks = [_.create_chat_invite_link(x.id, creates_join_request=True) for x in chats]
        invite_links = await asyncio.gather(*tasks)
        
        # Assigning invite links to chats
        for x, link in zip(chats, invite_links):
            x.invite_link = link.invite_link

        chat = chats[0]
        chat1 = chats[1]
        
        markup = IKM(
            [
                [
                    IKB("ᴘᴏsᴛɪɴɢ ᴄʜᴀɴɴᴇʟ", url=chat.invite_link),
                    IKB("ʙᴀᴄᴋᴜᴘ ᴄʜᴀɴɴᴇʟ", url=chat1.invite_link)
                ],
                [
                    IKB('ʜᴏᴡ ᴛᴏ ᴜsᴇ ᴛᴇʀᴀʙᴏx ʙᴏᴛ', url=TUTORIAL_LINK)
                ]
            ]
        )
    return markup
