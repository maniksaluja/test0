from time import time
import asyncio
from pyrogram.errors import FloodWait
from pyrogram.types import (
    Message, InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM
)
from config import TUTORIAL_LINK

# Optimized tryer function to handle FloodWait with efficiency
async def tryer(func, *args, **kwargs):
    try:
        return await func(*args, **kwargs)
    except FloodWait as e:
        wait_time = e.value
        # Setting delay for a reasonable bot speed
        if wait_time > 10:
            wait_time = 10  # Max delay to avoid slowing down the bot too much
        await asyncio.sleep(wait_time)
        return await func(*args, **kwargs)

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
        chats = (await get_chats(_))
        new = []
        for x in chats:
            y = await _.create_chat_invite_link(x.id, creates_join_request=True)
            new.append(y.invite_link)
        for x, y in enumerate(new):
            chats[x].invite_link = y
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
