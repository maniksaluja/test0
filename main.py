from pyrogram import Client, idle
from config import *
import sys
from resolve import ResolvePeer
import asyncio
from pyrogram.errors import FloodWait
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

class ClientLike(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def resolve_peer(self, id):
        obj = ResolvePeer(self)
        return await obj.resolve_peer(id)

# Bot instances
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

async def send_message_with_timeout(client, channel_id, message, retries=3, delay=5):
    """
    Function to send message with retries and timeout handling.
    """
    for _ in range(retries):
        try:
            await client.send_message(channel_id, message, timeout=10)  # 10 seconds timeout
            logger.info(f"Message sent to channel {channel_id} successfully.")
            return True
        except asyncio.TimeoutError:
            logger.warning(f"Timeout occurred while sending message to channel {channel_id}. Retrying...")
        except FloodWait as e:
            logger.warning(f"FloodWait occurred: waiting for {e.x} seconds")
            await asyncio.sleep(e.x)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return False
        await asyncio.sleep(delay)  # Delay before retrying
    return False  # If retries are exhausted

async def check_channel_access(client, channels):
    """
    Verify that the bot can send messages in the specified channels.
    """
    for channel_id in channels:
        if channel_id is None:
            logger.warning(f"Channel ID is None for {client.name}. Skipping.")
            continue
        success = await send_message_with_timeout(client, channel_id, '.')
        if not success:
            logger.error(f"Error accessing channel {channel_id} for {client.name}. Exiting.")
            return False, channel_id
    return True, None

async def start():
    """
    Start both bot clients and validate their access to required channels.
    """
    await app.start()
    await app1.start()

    logger.info("Bot instances started.")
    
    channels_to_check = [
        DB_CHANNEL_ID,
        DB_CHANNEL_2_ID,
        AUTO_SAVE_CHANNEL_ID,
        LOG_CHANNEL_ID
    ] + FSUB

    # Check channel access for both bots
    app_status, app_failed_channel = await check_channel_access(app, channels_to_check)
    app1_status, app1_failed_channel = await check_channel_access(app1, FSUB)

    if not (app_status and app1_status):
        if not app_status:
            logger.error(f"Bot @:91: failed to access channel: {app_failed_channel}")
        if not app1_status:
            logger.error(f"Bot @:91-1: failed to access channel: {app1_failed_channel}")
        await app.stop()
        await app1.stop()
        sys.exit()

    bot1_info = await app.get_me()
    bot2_info = await app1.get_me()

    logger.info(f'@{bot1_info.username} started.')
    logger.info(f'@{bot2_info.username} started.')

    await idle()

if __name__ == "__main__":
    asyncio.run(start())
