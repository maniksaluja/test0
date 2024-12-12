from pyrogram import Client, idle
from config import *
import sys
from resolve import ResolvePeer

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

async def check_channel_access(client, channels):
    """
    Verify that the bot can send messages in the specified channels.
    """
    for channel_id in channels:
        try:
            msg = await client.send_message(channel_id, '.')
            await msg.delete()
        except Exception as e:
            print(f"Error accessing channel {channel_id} for {client.name}: {e}")
            return False
    return True

async def start():
    """
    Start both bot clients and validate their access to required channels.
    """
    await app.start()
    await app1.start()
    
    channels_to_check = [
        DB_CHANNEL_ID,
        DB_CHANNEL_2_ID,
        AUTO_SAVE_CHANNEL_ID,
        LOG_CHANNEL_ID
    ] + FSUB

    # Check channel access for both bots
    if not (await check_channel_access(app, channels_to_check) and await check_channel_access(app1, FSUB)):
        print("Required channels are not accessible. Exiting.")
        await app.stop()
        await app1.stop()
        sys.exit()

    bot1_info = await app.get_me()
    bot2_info = await app1.get_me()

    print(f'@{bot1_info.username} started.')
    print(f'@{bot2_info.username} started.')

    await idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(start())
