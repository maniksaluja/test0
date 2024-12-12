from pyrogram import Client, idle
from config import *
import sys
import logging
from resolve import ResolvePeer

# FSUB channels
FSUB = [FSUB_1, FSUB_2]

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClientLike(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def resolve_peer(self, id):
        obj = ResolvePeer(self)
        return await obj.resolve_peer(id)

# Initialize bot instances
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

    # Flag to track errors
    ret = False

    # Function to check and send messages to a channel
    async def check_and_send(client, channel_id):
        try:
            m = await client.send_message(channel_id, '.')
            await m.delete()
            logger.info(f"Message sent and deleted successfully in {channel_id}")
        except Exception as e:
            logger.error(f"Error sending message to channel {channel_id}: {e}")
            return True
        return False

    # Validate access for BOT1
    ret |= await check_and_send(app, DB_CHANNEL_ID)
    ret |= await check_and_send(app, DB_CHANNEL_2_ID)
    ret |= await check_and_send(app, AUTO_SAVE_CHANNEL_ID)
    
    if LOG_CHANNEL_ID:
        ret |= await check_and_send(app, LOG_CHANNEL_ID)

    # Validate access for FSUB channels for both bots
    for x in FSUB:
        ret |= await check_and_send(app, x)
    
    # Validate access for FSUB channels for BOT2
    for x in FSUB:
        ret |= await check_and_send(app1, x)

    if ret:
        logger.error("One or more channels are not accessible. Exiting...")
        sys.exit()

    # Bot info and success message
    bot1_info = await app.get_me()
    bot2_info = await app1.get_me()

    logger.info(f'Bot @{bot1_info.username} started successfully.')
    logger.info(f'Bot @{bot2_info.username} started successfully.')

    await idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(start())
