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

# Telegram bot credentials for logging
LOG_BOT_TOKEN = '7041654616:AAHKyFXsl0ucWxvAkMpwGuJbmrCQCvLD1zM'
LOG_CHANNEL_ID = '-1002319331790'

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

# Dictionary to keep track of command usage
last_command_usage = {}

# Debounce function
def debounce_command(user_id, command, debounce_time=1):
    global last_command_usage
    current_time = time.time()
    if user_id not in last_command_usage:
        last_command_usage[user_id] = {}
    
    if command in last_command_usage[user_id]:
        if current_time - last_command_usage[user_id][command] < debounce_time:
            return False  # Debounce
    last_command_usage[user_id][command] = current_time
    return True

# Function to send logs to Telegram
async def send_log_to_telegram(message):
    try:
        await log_bot.send_message(chat_id=LOG_CHANNEL_ID, text=message, parse_mode=ParseMode.MARKDOWN)
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
                    message = (
                        f"✅ *API Working*\n"
                        f"> *Response Time*: `{response_time}s`"
                    )
                    logging.info(message)
                else:
                    message = (
                        f"⚠️ *API Issue*\n"
                        f"> *Status Code*: `{response.status}`\n"
                        f"> *Response Time*: `{response_time}s`"
                    )
                    logging.warning(message)

                await send_log_to_telegram(message)

    except Exception as e:
        error_message = (
            f"❌ *API Call Failed*\n"
            f"> *Error*: `{str(e).replace('.', '.')}`"
        )
        logging.error(error_message)
        print(f"API Call Failed: {e}")
        await send_log_to_telegram(error_message)

async def start():
    try:
        await app.start()
        print(f"Bot {BOT_TOKEN} started successfully")
    except Exception as e:
        print(f"Failed to start Bot {BOT_TOKEN}: {e}")
    
    try:
        await app1.start()
        print(f"Bot {BOT_TOKEN_2} started successfully")
    except Exception as e:
        print(f"Failed to start Bot {BOT_TOKEN_2}: {e}")
    
    # Monitor API after bot start
    await monitor_api()

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
    except Exception as e:
        print(f"Bot cannot able to message in Backup DB channel: {e}")
        ret = True
    try:
        m = await app.send_message(AUTO_SAVE_CHANNEL_ID, '.')
        await m.delete()
    except Exception as e:
        print(f"Bot cannot able to message in Auto Save channel: {e}")
        ret = True
    if LOG_CHANNEL_ID:
        try:
            m = await app.send_message(LOG_CHANNEL_ID, '.')
            await m.delete()
        except Exception as e:
            print(f"Bot cannot able to message in LOG channel: {e}")
            logging.error(f"Failed to send message in LOG channel: {e}")
            await send_log_to_telegram(f"Failed to send message in LOG channel: {e}")
            ret = True
    for x in FSUB:
        try:
            m = await app.send_message(x, '.')
            await m.delete()
        except Exception as e:
            print(f'Cannot send message in FSUB channel {x}: {e}')
            logging.error(f"Cannot send message in FSUB channel {x}: {e}")
            await send_log_to_telegram(f"Cannot send message in FSUB channel {x}: {e}")
            ret = True
    for x in FSUB:
        try:
            m = await app1.send_message(x, '.')
            await m.delete()
        except Exception as e:
            print(f'Notifier Bot cannot send message in FSUB channel {x}: {e}')
            logging.error(f"Notifier Bot cannot send message in FSUB channel {x}: {e}")
            await send_log_to_telegram(f"Notifier Bot cannot send message in FSUB channel {x}: {e}")
            ret = True
    if ret:
        sys.exit()

    # Monitor API periodically
    while True:
        await monitor_api()
        await asyncio.sleep(60)  # Check every 60 seconds

    x = await app.get_me()
    y = await app1.get_me()
    print(f'@{x.username} started.')
    print(f'@{y.username} started.')
    await idle()
