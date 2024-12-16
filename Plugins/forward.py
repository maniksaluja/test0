from pyrogram import Client, filters
from pyrogram.errors import FloodWait
import time
from config import API_ID2, API_HASH2, BOT_TOKEN_2, source_channel, target_channel, forwarding_enabled

app = Client("channel_forwarder", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.channel & filters.chat(source_channel))
async def forward_posts(client, message):
    if not forwarding_enabled:
        print("Forwarding is disabled. Skipping message.")
        return

    try:
        # Forwarding the message
        await message.forward(chat_id=target_channel)
    except FloodWait as e:
        # Handling FloodWait exception
        print(f"FloodWait detected: Sleeping for {e.value} seconds")
        time.sleep(e.value)  # Wait for the required time before retrying
    except Exception as ex:
        print(f"An error occurred: {ex}")

print("Forwarding Enabled...")
