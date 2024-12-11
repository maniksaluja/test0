from pyrogram import Client, idle
from config import *
import sys
from resolve import ResolvePeer

FSUB = [FSUB_1, FSUB_2]

class ClientLike(Client):
    def __init__(self, *args, **kwargs):  # Corrected the method name
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

async def send_and_delete_message(bot, channel_id):
    try:
        m = await bot.send_message(channel_id, '.')
        await m.delete()
    except Exception as e:
        print(f"Error sending message to {channel_id}: {e}")
        return False
    return True

async def start():
    await app.start()
    await app1.start()
    ret = False
    
    # Check bot permissions for all channels
    channels_to_check = [DB_CHANNEL_ID, DB_CHANNEL_2_ID, AUTO_SAVE_CHANNEL_ID, LOG_CHANNEL_ID] + FSUB
    for channel_id in channels_to_check:
        if not await send_and_delete_message(app, channel_id):
            ret = True
        if not await send_and_delete_message(app1, channel_id):
            ret = True
    
    if ret:
        print("Some bots couldn't send messages in required channels, quitting.")
        sys.exit()

    # Bot started successfully
    x = await app.get_me()
    y = await app1.get_me()
    print(f'@{x.username} started.')
    print(f'@{y.username} started.')
    await idle()
