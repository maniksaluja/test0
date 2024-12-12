from pyrogram import Client, idle
from config import *
import sys
import asyncio
from resolve import ResolvePeer
import logging
from pyrogram.errors import FloodWait, BadRequest

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            await client.send_message(channel_id, message)  # Removed timeout argument
            logger.info(f"Message sent to channel {channel_id} successfully for bot {client.name}.")
            return True
        except asyncio.TimeoutError:
            logger.warning(f"Timeout occurred while sending message to channel {channel_id} for bot {client.name}. Retrying...")
        except FloodWait as e:
            logger.warning(f"FloodWait occurred for bot {client.name}: waiting for {e.x} seconds")
            await asyncio.sleep(e.x)
        except BadRequest as e:
            logger.error(f"BadRequest error for bot {client.name}: {e}. Skipping message sending.")
            return False
        except Exception as e:
            logger.error(f"Unexpected error occurred for bot {client.name}: {e}")
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
        try:
            msg = await client.send_message(channel_id, '.')
            await msg.delete()
        except BadRequest as e:
            logger.error(f"BadRequest error while checking access for channel {channel_id} for {client.name}: {e}")
            return False, channel_id
        except Exception as e:
            logger.error(f"Error accessing channel {channel_id} for bot {client.name}: {e}")
            return False, channel_id
    return True, None

async def start():
    """
    Start both bot clients and validate their access to required channels.
    """
    await app.start()
    await app1.start()
    
    # Channels for BOT1
    bot1_channels_to_check = [
        DB_CHANNEL_ID,    # BOT1 DB channel
        DB_CHANNEL_2_ID,  # BOT1 DB Channel 2
        AUTO_SAVE_CHANNEL_ID,  # BOT1 Auto Save Channel (Optional)
        LOG_CHANNEL_ID   # BOT1 Log Channel (Optional)
    ] + FSUB  # FSUB can be checked by both bots

    # Channels for BOT2 (only FSUB channels)
    bot2_channels_to_check = FSUB
    
    # Check channel access for BOT1
    app_status, app_failed_channel = await check_channel_access(app, bot1_channels_to_check)
    # Check channel access for BOT2
    app1_status, app1_failed_channel = await check_channel_access(app1, bot2_channels_to_check)

    if not (app_status and app1_status):
        if not app_status:
            logger.error(f"Bot @:91: failed to access channel {app_failed_channel}.")
        if not app1_status:
            logger.error(f"Bot @:91-1: failed to access channel {app1_failed_channel}.")
        await app.stop()
        await app1.stop()
        sys.exit()

    bot1_info = await app.get_me()
    bot2_info = await app1.get_me()

    logger.info(f'Bot @{bot1_info.username} started successfully.')
    logger.info(f'Bot @{bot2_info.username} started successfully.')

    # Send test message with retries and log results
    if not await send_message_with_timeout(app, DB_CHANNEL_ID, "Test message from bot @The_TeraBox_bot"):
        logger.error(f"Failed to send message from bot @{bot1_info.username} to channel {DB_CHANNEL_ID}.")
    if not await send_message_with_timeout(app1, DB_CHANNEL_2_ID, "Test message from bot @Approvel87473bot"):
        logger.error(f"Failed to send message from bot @{bot2_info.username} to channel {DB_CHANNEL_2_ID}.")

    await idle()

if __name__ == "__main__":
    asyncio.run(start())
