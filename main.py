from pyrogram import Client, idle
from config import *
import sys
import logging
import time
import aiohttp
from telegram import Bot
from telegram.constants import ParseMode
from resolve import ResolvePeer
import asyncio

FSUB = [FSUB_1, FSUB_2]

# Use BOT_TOKEN_2 for logging
LOG_BOT_TOKEN = BOT_TOKEN_2
LOG_CHANNEL_ID = VPS_LOGS  # Using the new VPS_LOGS variable

# Initialize Telegram Bot
log_bot = Bot(token=LOG_BOT_TOKEN)

# Logging setup
logging.basicConfig(filename="backend_monitor.log", level=logging.INFO, format="%(asctime)s - %(message)s")

class ClientLike(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def resolve_peer(self, id):
        obj = ResolvePeer(self)
        return await obj.resolve_peer(id)

# Initialize app for bot 1
app = ClientLike(
    ':91:',
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root='Plugins')
)

# Initialize app for bot 2 with its respective API ID, API Hash, and Token
app1 = ClientLike(
    ':91-1:',
    api_id=API_ID2,  # Bot 2's API ID
    api_hash=API_HASH2,  # Bot 2's API Hash
    bot_token=BOT_TOKEN_2,
    plugins=dict(root='Plugins1')
)

# Function to send logs to Telegram
async def send_log_to_telegram(message):
    try:
        escaped_message = message.replace('-', '\\-').replace('.', '\\.').replace('_', '\\_')
        await log_bot.send_message(chat_id=LOG_CHANNEL_ID, text=escaped_message, parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logging.error(f"Telegram notification failed: {e}")
        print(f"Telegram notification failed: {e}")

# Function to monitor API response times and errors
async def monitor_api():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
    try:
        start_time = time.time()
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                end_time = time.time()
                response_time = round(end_time - start_time, 2)

                if response.status == 200:
                    logging.info(f"API Working. Response Time: {response_time}s")
                else:
                    error_message = f"API Issue. Status Code: {response.status}, Response Time: {response_time}s"
                    logging.warning(error_message)
                    await send_log_to_telegram(error_message)

    except Exception as e:
        error_message = f"API Call Failed. Error: {str(e).replace('.', '.')}"
        logging.error(error_message)
        await send_log_to_telegram(error_message)

async def check_requirements():
    ret = False

    # Check message sending to specific channels with respective bot tokens
    try:
        await app.send_message(DB_CHANNEL_ID, '.')
    except Exception as e:
        error_message = f"Bot {BOT_TOKEN} cannot send message to DB_CHANNEL_ID: {str(e).replace('.', '.')}"
        logging.error(error_message)
        await send_log_to_telegram(error_message)
        ret = True

    try:
        await app.send_message(DB_CHANNEL_2_ID, '.')
    except Exception as e:
        error_message = f"Bot {BOT_TOKEN} cannot send message to DB_CHANNEL_2_ID: {str(e).replace('.', '.')}"
        logging.error(error_message)
        await send_log_to_telegram(error_message)
        ret = True

    try:
        await app.send_message(AUTO_SAVE_CHANNEL_ID, '.')
    except Exception as e:
        error_message = f"Bot {BOT_TOKEN} cannot send message to AUTO_SAVE_CHANNEL_ID: {str(e).replace('.', '.')}"
        logging.error(error_message)
        await send_log_to_telegram(error_message)
        ret = True

    if LOG_CHANNEL_ID:
        try:
            await app.send_message(LOG_CHANNEL_ID, '.')
        except Exception as e:
            error_message = f"Bot {BOT_TOKEN} cannot send message to LOG_CHANNEL_ID: {str(e).replace('.', '.')}"
            logging.error(error_message)
            await send_log_to_telegram(error_message)
            ret = True

    for x in FSUB:
        try:
            await app.send_message(x, '.')
        except Exception as e:
            error_message = f"Bot {BOT_TOKEN} cannot send message in FSUB channel {x}: {str(e).replace('.', '.')}"
            logging.error(error_message)
            await send_log_to_telegram(error_message)
            ret = True

        try:
            await app1.send_message(x, '.')
        except Exception as e:
            error_message = f"Notifier Bot cannot send message in FSUB channel {x}: {str(e).replace('.', '.')}"
            logging.error(error_message)
            await send_log_to_telegram(error_message)
            ret = True

    return ret

async def start():
    try:
        await app.start()
        print(f"Bot {BOT_TOKEN} started successfully")
    except Exception as e:
        error_message = f"Failed to start Bot {BOT_TOKEN}: {e}"
        print(error_message)
        logging.error(error_message)
        await send_log_to_telegram(error_message)

    try:
        await app1.start()
        print(f"Bot {BOT_TOKEN_2} started successfully")
    except Exception as e:
        error_message = f"Failed to start Bot {BOT_TOKEN_2}: {e}"
        print(error_message)
        logging.error(error_message)
        await send_log_to_telegram(error_message)

    # Check requirements before proceeding
    requirements_met = await check_requirements()
    if requirements_met:
        sys.exit()

    # Bots start message
    x = await app.get_me()
    y = await app1.get_me()
    start_message = f'@{x.username} started.\n@{y.username} started.'
    print(start_message)
    await send_log_to_telegram(start_message)

    # Monitor API periodically
    while True:
        await monitor_api()
        await asyncio.sleep(60)  # Check every 60 seconds

    await idle()

# Start the bot
asyncio.get_event_loop().run_until_complete(start())
