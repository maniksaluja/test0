from pyrogram import Client, idle
from config import *
import sys
import logging
import time
import requests
from telegram import Bot, ParseMode
from resolve import ResolvePeer

FSUB = [FSUB_1, FSUB_2]

# Telegram bot credentials for logging
LOG_BOT_TOKEN = '7041654616:AAHKyFXsl0ucWxvAkMpwGuJbmrCQCvLD1zM'  # Apne bot ka token yahan daalein
LOG_CHANNEL_ID = '-1002319331790'  # Apna channel ya group yahan daalein

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

app = ClientLike(
    ':91:',
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root='Plugins')
)

app1 = ClientLike(
    ':91-1:',
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN_2,
    plugins=dict(root='Plugins1')
)

# Function to send logs to Telegram
def send_log_to_telegram(message):
    try:
        log_bot.send_message(chat_id=LOG_CHANNEL_ID, text=message, parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logging.error(f"Telegram notification failed: {e}")

# Function to monitor API response times and errors
def monitor_api():
    url = "https://api.telegram.org/bot<your_bot_token>/getMe"  # Example API call
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)
        end_time = time.time()
        response_time = round(end_time - start_time, 2)

        if response.status_code == 200:
            message = (
                f"✅ *API Working*\n"
                f"> *Response Time*: `{response_time}s`"
            )
            logging.info(message)
        else:
            message = (
                f"⚠️ *API Issue*\n"
                f"> *Status Code*: `{response.status_code}`\n"
                f"> *Response Time*: `{response_time}s`"
            )
            logging.warning(message)

        send_log_to_telegram(message)

    except requests.exceptions.RequestException as e:
        error_message = (
    f"❌ *API Call Failed*\n"
    f"> *Error*: `{str(e).replace('.', '\\.')}`"
        )
        logging.error(error_message)
        send_log_to_telegram(error_message)

async def start():
    await app.start()
    await app1.start()
    
    # Monitor API after bot start
    monitor_api()

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

    # Monitor API periodically
    while True:
        monitor_api()
        await asyncio.sleep(60)  # Check every 60 seconds

    x = await app.get_me()
    y = await app1.get_me()
    print(f'@{x.username} started.')
    print(f'@{y.username} started.')
    await idle()
