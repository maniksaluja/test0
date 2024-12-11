from pyrogram import Client, idle
from config import *
import sys
from resolve import ResolvePeer

FSUB = [FSUB_1, FSUB_2]

# Second bot for logging and tracking
log_app = Client(
    ':91-log:',
    api_id=API_ID2,
    api_hash=API_HASH2,
    bot_token=BOT_TOKEN_2,
    plugins=dict(root='Plugins1')
)

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
    api_id=API_ID2,
    api_hash=API_HASH2,
    bot_token=BOT_TOKEN_2,
    plugins=dict(root='Plugins1')
)

async def send_error_log(message):
    try:
        await log_app.send_message(VPS_LOG_CHANNEL, message)
    except Exception as e:
        print(f"[ERROR] Failed to send log message to VPS_LOG_CHANNEL. Error: {e}")

async def start():
    await app.start()
    await app1.start()
    await log_app.start()
    ret = False

    # Check if bots can send messages to channels
    try:
        m = await app.send_message(DB_CHANNEL_ID, '.')
        await m.delete()
    except Exception as e:
        log_message = f"[ERROR] Bot1 cannot send message in DB_CHANNEL_ID. Error: {e}"
        print(log_message)
        await send_error_log(log_message)
        ret = True
    try:
        m = await app.send_message(DB_CHANNEL_2_ID, '.')
        await m.delete()
    except Exception as e:
        log_message = f"[ERROR] Bot1 cannot send message in DB_CHANNEL_2_ID. Error: {e}"
        print(log_message)
        await send_error_log(log_message)
        ret = True
    try:
        m = await app.send_message(AUTO_SAVE_CHANNEL_ID, '.')
        await m.delete()
    except Exception as e:
        log_message = f"[ERROR] Bot1 cannot send message in AUTO_SAVE_CHANNEL_ID. Error: {e}"
        print(log_message)
        await send_error_log(log_message)
        ret = True
    if LOG_CHANNEL_ID:
        try:
            m = await app.send_message(LOG_CHANNEL_ID, '.')
            await m.delete()
        except Exception as e:
            log_message = f"[ERROR] Bot1 cannot send message in LOG_CHANNEL_ID. Error: {e}"
            print(log_message)
            await send_error_log(log_message)
            ret = True

    # Check for FSUB channels
    for x in FSUB:
        try:
            m = await app.send_message(x, '.')
            await m.delete()
        except Exception as e:
            log_message = f"[ERROR] Bot1 cannot send message in FSUB channel {x}. Error: {e}"
            print(log_message)
            await send_error_log(log_message)
            ret = True

    # Check for FSUB channels with second bot
    for x in FSUB:
        try:
            m = await app1.send_message(x, '.')
            await m.delete()
        except Exception as e:
            log_message = f"[ERROR] Bot2 cannot send message in FSUB channel {x}. Error: {e}"
            print(log_message)
            await send_error_log(log_message)
            ret = True

    if ret:
        sys.exit()

    x = await app.get_me()
    y = await app1.get_me()
    print(f'@{x.username} started.')
    print(f'@{y.username} started.')
    await idle()
