from pyrogram import Client, idle
from config import *
import sys
import time
from resolve import ResolvePeer

FSUB = [FSUB_1, FSUB_2]

class ClientLike(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def resolve_peer(self, id):
        obj = ResolvePeer(self)
        return await obj.resolve_peer(id)

    async def track_response_time(self, message_func, *args, **kwargs):
        """Track the response time for a given message request."""
        start_time = time.time()
        try:
            result = await message_func(*args, **kwargs)
            response_time = time.time() - start_time
            if response_time > 5:  # If response time exceeds 5 seconds
                await self.send_message(VPSLOG_CHANNEL, f"[SLOW RESPONSE] Response time: {response_time:.2f}s, Function: {message_func.__name__}, Args: {args}, Kwargs: {kwargs}")
            return result
        except Exception as e:
            await self.send_message(VPSLOG_CHANNEL, f"[ERROR] Failed to send message in {message_func.__name__}. Error: {str(e)}")
            raise e

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

async def start():
    await app.start()
    await app1.start()
    ret = False

    # Check if bots can send messages to channels and track response time
    try:
        await app.track_response_time(app.send_message, DB_CHANNEL_ID, '.')
    except Exception as e:
        print(f"[ERROR] Bot1 cannot send message in DB_CHANNEL_ID. Error: {e}")
        ret = True
    try:
        await app.track_response_time(app.send_message, DB_CHANNEL_2_ID, '.')
    except Exception as e:
        print(f"[ERROR] Bot1 cannot send message in DB_CHANNEL_2_ID. Error: {e}")
        ret = True
    try:
        await app.track_response_time(app.send_message, AUTO_SAVE_CHANNEL_ID, '.')
    except Exception as e:
        print(f"[ERROR] Bot1 cannot send message in AUTO_SAVE_CHANNEL_ID. Error: {e}")
        ret = True
    if LOG_CHANNEL_ID:
        try:
            await app.track_response_time(app.send_message, LOG_CHANNEL_ID, '.')
        except Exception as e:
            print(f"[ERROR] Bot1 cannot send message in LOG_CHANNEL_ID. Error: {e}")
            ret = True

    # Check for FSUB channels
    for x in FSUB:
        try:
            await app.track_response_time(app.send_message, x, '.')
        except Exception as e:
            print(f"[ERROR] Bot1 cannot send message in FSUB channel {x}. Error: {e}")
            ret = True

    # Check for FSUB channels with second bot
    for x in FSUB:
        try:
            await app1.track_response_time(app1.send_message, x, '.')
        except Exception as e:
            print(f"[ERROR] Bot2 cannot send message in FSUB channel {x}. Error: {e}")
            ret = True

    if ret:
        sys.exit()

    x = await app.get_me()
    y = await app1.get_me()
    print(f'@{x.username} started.')
    print(f'@{y.username} started.')
    await idle()
