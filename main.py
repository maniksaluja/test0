from pyrogram import Client, idle
from config import *
import sys
import time
from resolve import ResolvePeer
from pyrogram.errors import FloodWait, BadRequest

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
            print(f"Attempting to send message to channel ID: {args[0]}")  # Debugging statement
            result = await message_func(*args, **kwargs)
            response_time = time.time() - start_time
            if response_time > 5:  # If response time exceeds 5 seconds
                await self.send_message(VPSLOG_CHANNEL, f"[SLOW RESPONSE] Response time: {response_time:.2f}s, Function: {message_func.__name__}, Args: {args}, Kwargs: {kwargs}")
            return result
        except FloodWait as e:
            await self.send_message(VPSLOG_CHANNEL, f"[FLOOD WAIT] Sleeping for {e.x} seconds. Error: {str(e)}")
            time.sleep(e.x)
            raise e
        except BadRequest as e:
            await self.send_message(VPSLOG_CHANNEL, f"[BAD REQUEST] Error: {str(e)}")
            print(f"[BAD REQUEST] Error: {str(e)}")  # Printing detailed BadRequest error
            raise e
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

    channels_to_check = [DB_CHANNEL_ID, DB_CHANNEL_2_ID, AUTO_SAVE_CHANNEL_ID] + FSUB
    if LOG_CHANNEL_ID:
        channels_to_check.append(LOG_CHANNEL_ID)

    for channel in channels_to_check:
        try:
            print(f"Checking Bot1 message to channel ID: {channel}")  # Debugging statement
            sent_msg = await app.track_response_time(app.send_message, channel, '.')
            if hasattr(sent_msg, 'message_id'):
                await app.delete_messages(channel, sent_msg.message_id)  # Delete the sent message
            else:
                print(f"[ERROR] Message does not have message_id in channel {channel}")
        except Exception as e:
            print(f"[ERROR] Bot1 cannot send message in channel {channel}. Error: {e}")
            ret = True

    for channel in FSUB:
        try:
            print(f"Checking Bot2 message to channel ID: {channel}")  # Debugging statement
            sent_msg = await app1.track_response_time(app1.send_message, channel, '.')
            if hasattr(sent_msg, 'message_id'):
                await app1.delete_messages(channel, sent_msg.message_id)  # Delete the sent message
            else:
                print(f"[ERROR] Message does not have message_id in channel {channel}")
        except Exception as e:
            print(f"[ERROR] Bot2 cannot send message in FSUB channel {channel}. Error: {e}")
            ret = True

    if ret:
        sys.exit()

    x = await app.get_me()
    y = await app1.get_me()
    print(f'@{x.username} started.')
    print(f'@{y.username} started.')
    await idle()

if __name__ == "__main__":
    app.run(start)
