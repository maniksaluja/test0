from time import time
import asyncio
from pyrogram.errors import FloodWait
from pyrogram.types import (
    Message, InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM
)
from config import TUTORIAL_LINK, AUTO_DELETE_TIME
from config import FSUB_1, FSUB_2

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

# Function to format time into human-readable form
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

# Setup auto-delete time
AUTO_DELETE_STR = grt(AUTO_DELETE_TIME)

startTime = time()

# Importing necessary modules
from .start import get_chats

# Placeholder for markup
markup = None

# Asynchronous build function for generating markup with invite links
async def build(_):
    global markup
    if not markup:
        # Fetching the list of chats
        chats = await get_chats(_)
        new = []
        
        # Using asyncio.gather to process multiple invite links concurrently
        tasks = [_.create_chat_invite_link(x.id, creates_join_request=True) for x in chats]
        try:
            invite_links = await asyncio.gather(*tasks)
        except Exception as e:
            print(f"Error in generating invite links: {e}")
            invite_links = []
        
        # Assigning invite links to chats
        for x, link in zip(chats, invite_links):
            x.invite_link = link.invite_link
        
        # Getting two chats to create the markup
        chat = chats[0]
        chat1 = chats[1]
        
        # Creating the inline keyboard markup
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

# The `FSUB` list to subscribe to channels
FSUB = [FSUB_1, FSUB_2]

# ClientLike class to extend Pyrogram's Client class
class ClientLike(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # Async method to resolve peer from id
    async def resolve_peer(self, id):
        obj = ResolvePeer(self)
        return await obj.resolve_peer(id)

# Two client instances for the bot
app = ClientLike(
    ':91:',
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root='Plugins')
)

app1 = ClientLike(
    ':91-1:',
    api_id=API_ID2,
    api_hash=API_HASH2,
    bot_token=BOT_TOKEN_2,
    plugins=dict(root='Plugins1')
)

# Starting the bot and checking message sending capabilities
async def start():
    await app.start()
    await app1.start()
    ret = False
    try:
        m = await app.send_message(DB_CHANNEL_ID, '.')
        await m.delete()
    except Exception as e:
        print(e)
        print("Bot cannot able to message in DB channel.")
        ret = True
    try:
        m = await app.send_message(DB_CHANNEL_2_ID, '.')
        await m.delete()
    except:
        print("Bot cannot able to message in Backup DB channel.")
        ret = True
    try:
        m = await app.send_message(AUTO_SAVE_CHANNEL_ID, '.')
        await m.delete()
    except:
        print("Bot cannot able to message in Auto Save channel.")
        ret = True
    if LOG_CHANNEL_ID:
        try:
            m = await app.send_message(LOG_CHANNEL_ID, '.')
            await m.delete()
        except:
            print("Bot cannot able to message in LOG channel.")
            ret = True
    for x in FSUB:
        try:
            m = await app.send_message(x, '.')
            await m.delete()
        except:
            print(f'Cannot send message in FSUB channel {x}, Quitting.')
            ret = True
    for x in FSUB:
        try:
            m = await app1.send_message(x, '.')
            await m.delete()
        except:
            print(f'Notifier Bot cannot send message in FSUB channel {x}, Quitting.')
            ret = True
    if ret:
        sys.exit()
    x = await app.get_me()
    y = await app1.get_me()
    print(f'@{x.username} started.')
    print(f'@{y.username} started.')
    await idle()
