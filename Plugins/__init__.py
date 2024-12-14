from time import time
import asyncio
from pyrogram.errors import FloodWait
from pyrogram.types import (
    Message, InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM
)
from config import TUTORIAL_LINK, AUTO_DELETE_TIME

# Optimized tryer function to handle FloodWait
async def tryer(func, *args, **kwargs):
    while True:
        try:
            return await func(*args, **kwargs)
        except FloodWait as e:
            wait_time = min(e.value, 10)  # Max delay capped at 10 seconds
            print(f"FloodWait detected: Waiting for {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except Exception as ex:
            print(f"Unexpected error: {ex}")
            raise

# Utility functions for time formatting
def grt(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}S"
    elif seconds < 3600:
        return f"{int(seconds / 60)}M"
    else:
        return f"{int(seconds / 3600)}H"

def alpha_grt(sec: int) -> str:
    if sec < 60:
        return f"{sec}S"
    elif sec < 3600:
        return f"{int(sec / 60)}M"
    return "60M+"

# Global constants and variables
AUTO_DELETE_STR = grt(AUTO_DELETE_TIME)
startTime = time()
markup = None

# Function to build the InlineKeyboardMarkup
from .start import get_chats

async def build(client):
    global markup
    if not markup:
        chats = await get_chats(client)
        new_links = []
        
        # Generate invite links with join requests
        for chat in chats:
            invite_link = await client.create_chat_invite_link(chat.id, creates_join_request=True)
            new_links.append(invite_link.invite_link)
        
        # Map generated links to respective chats
        for idx, link in enumerate(new_links):
            chats[idx].invite_link = link

        # Prepare inline keyboard buttons
        chat1, chat2 = chats[:2]  # Assuming at least 2 chats exist
        markup = IKM(
            [
                [
                    IKB("ᴘᴏsᴛɪɴɢ ᴄʜᴀɴɴᴇʟ", url=chat1.invite_link),
                    IKB("ʙᴀᴄᴋᴜᴘ ᴄʜᴀɴɴᴇʟ", url=chat2.invite_link)
                ],
                [
                    IKB("ʜᴏᴡ ᴛᴏ ᴜsᴇ ᴛᴇʀᴀʙᴏx ʙᴏᴛ", url=TUTORIAL_LINK)
                ]
            ]
        )
    return markup
