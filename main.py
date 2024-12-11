import logging
import time
import sys
import asyncio
from pyrogram import Client, idle
from config import *
from resolve import ResolvePeer
from pyrogram.errors import FloodWait, BadRequest

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            logger.info(f"Attempting to send message to channel ID: {args[0]}")  # Debugging statement
            if args[0] is None:
                logger.error("[ERROR] Channel ID is None. Skipping.")
                return  # Skip if channel ID is None
            
            sent_msg = await message_func(*args, **kwargs)  # Send the message
            response_time = time.time() - start_time
            if response_time > 5:  # If response time exceeds 5 seconds
                await self.send_message(VPSLOG_CHANNEL, f"[SLOW RESPONSE] Response time: {response_time:.2f}s, Function: {message_func.__name__}, Args: {args}, Kwargs: {kwargs}")
            
            # Ensure message was sent and delete it
            if hasattr(sent_msg, 'message_id'):
                await self.delete_messages(args[0], sent_msg.message_id)  # Delete the sent message
                logger.info(f"Message deleted from channel {args[0]} with message_id {sent_msg.message_id}")
            else:
                logger.error(f"[ERROR] Message does not have message_id. Not deleting.")
            
            return sent_msg
        except FloodWait as e:
            await self.send_message(VPSLOG_CHANNEL, f"[FLOOD WAIT] Sleeping for {e.x} seconds. Error: {str(e)}")
            await asyncio.sleep(e.x)  # Use asyncio.sleep to avoid blocking the event loop
            raise e
        except BadRequest as e:
            await self.send_message(VPSLOG_CHANNEL, f"[BAD REQUEST] Error: {str(e)}")
            logger.error(f"[BAD REQUEST] Error: {str(e)}")
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

    channels_to_check = [DB_CHANNEL_ID, DB_CHANNEL_2_ID, AUTO_SAVE_CHANNEL_ID, LOG_CHANNEL_ID] + FSUB

    for i, channel in enumerate(channels_to_check):
        if channel is not None:
            try:
                if i < len(FSUB):
                    logger.info(f"Checking Bot2 message to channel ID: {channel}")  # Debugging statement
                    sent_msg = await app1.track_response_time(app1.send_message, channel, '.')
                else:
                    logger.info(f"Checking Bot1 message to channel ID: {channel}")  # Debugging statement
                    sent_msg = await app.track_response_time(app.send_message, channel, '.')
                
                if not hasattr(sent_msg, 'message_id'):
                    logger.error(f"[ERROR] Message does not have message_id in channel {channel}.")
            except Exception as e:
                logger.error(f"[ERROR] Cannot send message in channel {channel}. Error: {e}")
                ret = True

    if ret:
        sys.exit()

    x = await app.get_me()
    y = await app1.get_me()
    logger.info(f'@{x.username} started.')
    logger.info(f'@{y.username} started.')
    await idle()

if __name__ == "__main__":
    app.run(start)
