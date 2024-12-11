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

# Create Client instances for both bots
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

async def send_vps_log(message):
    """Send logs to VPS log channel via BOT_TOKEN_2"""
    try:
        await app1.send_message(VPSLOG_CHANNEL, message)
    except Exception as e:
        print(f"[ERROR] Could not send VPS log. Error: {e}")

async def start():
    await app.start()
    await app1.start()
    ret = False
    log_message = []

    try:
        m = await app.send_message(DB_CHANNEL_ID, '.')
        await m.delete()
        log_message.append("Bot1: Successfully sent message in DB_CHANNEL_ID")
    except Exception as e:
        log_message.append(f"Bot1: Failed to send message in DB_CHANNEL_ID. Error: {e}")
        ret = True

    try:
        m = await app.send_message(DB_CHANNEL_2_ID, '.')
        await m.delete()
        log_message.append("Bot1: Successfully sent message in DB_CHANNEL_2_ID")
    except Exception as e:
        log_message.append(f"Bot1: Failed to send message in DB_CHANNEL_2_ID. Error: {e}")
        ret = True

    try:
        m = await app.send_message(AUTO_SAVE_CHANNEL_ID, '.')
        await m.delete()
        log_message.append("Bot1: Successfully sent message in AUTO_SAVE_CHANNEL_ID")
    except Exception as e:
        log_message.append(f"Bot1: Failed to send message in AUTO_SAVE_CHANNEL_ID. Error: {e}")
        ret = True

    if LOG_CHANNEL_ID:
        try:
            m = await app.send_message(LOG_CHANNEL_ID, '.')
            await m.delete()
            log_message.append("Bot1: Successfully sent message in LOG_CHANNEL_ID")
        except Exception as e:
            log_message.append(f"Bot1: Failed to send message in LOG_CHANNEL_ID. Error: {e}")
            ret = True

    # Check for FSUB channels for bot1
    for x in FSUB:
        try:
            m = await app.send_message(x, '.')
            await m.delete()
            log_message.append(f"Bot1: Successfully sent message in FSUB channel {x}")
        except Exception as e:
            log_message.append(f"Bot1: Failed to send message in FSUB channel {x}. Error: {e}")
            ret = True

    # Check for FSUB channels for bot2
    for x in FSUB:
        try:
            m = await app1.send_message(x, '.')
            await m.delete()
            log_message.append(f"Bot2: Successfully sent message in FSUB channel {x}")
        except Exception as e:
            log_message.append(f"Bot2: Failed to send message in FSUB channel {x}. Error: {e}")
            ret = True

    if ret:
        await send_vps_log("\n".join(log_message))
        sys.exit()

    x = await app.get_me()
    y = await app1.get_me()
    log_message.append(f"@{x.username} started.")
    log_message.append(f"@{y.username} started.")

    await send_vps_log("\n".join(log_message))
    await idle()
