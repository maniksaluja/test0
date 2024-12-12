from pyrogram import Client, idle
from config import *
import sys
from resolve import ResolvePeer

FSUB = [FSUB_1, FSUB_2]

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
    plugins=dict(root='Plugins'),
    workers=15  # Added worker threads for main bot
)

app1 = ClientLike(
    ':91-1:',
    api_id=API_ID2,
    api_hash=API_HASH2,
    bot_token=BOT_TOKEN_2,
    plugins=dict(root='Plugins1'),
    workers=4  # Added worker threads for notifier bot
)

async def start():
    await app.start()
    await app1.start()
    ret = False
    try:
        m = await app.send_message(DB_CHANNEL_ID, '.')
        await m.delete()
    except Exception as e:
        print(e)
        print("Bot cannot message in DB channel.")
        ret = True
    try:
        m = await app.send_message(DB_CHANNEL_2_ID, '.')
        await m.delete()
    except:
        print("Bot cannot message in Backup DB channel.")
        ret = True
    try:
        m = await app.send_message(AUTO_SAVE_CHANNEL_ID, '.')
        await m.delete()
    except:
        print("Bot cannot message in Auto Save channel.")
        ret = True
    if LOG_CHANNEL_ID:
        try:
            m = await app.send_message(LOG_CHANNEL_ID, '.')
            await m.delete()
        except:
            print("Bot cannot message in LOG channel.")
            ret = True
    for x in FSUB:
        try:
            m = await app.send_message(x, '.')
            await m.delete()
        except:
            print(f'Cannot send message in FSUB channel {x}, quitting.')
            ret = True
    for x in FSUB:
        try:
            m = await app1.send_message(x, '.')
            await m.delete()
        except:
            print(f'Notifier Bot cannot send message in FSUB channel {x}, quitting.')
            ret = True
    if ret:
        sys.exit()
    x = await app.get_me()
    y = await app1.get_me()
    print(f'@{x.username} started.')
    print(f'@{y.username} started.')
    await idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(start())
