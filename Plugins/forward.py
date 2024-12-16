from pyrogram import Client, filters
from pyrogram.errors import FloodWait
import time
from config import forwarding_enabled, source_channel, target_channel

# Bot Client
app = Client("forward_bot")

@app.on_message(filters.channel & filters.chat(source_channel))
async def forward_posts(client, message):
    if not forwarding_enabled:
        print("Forwarding is disabled. Skipping message.")
        return

    try:
        # Forward message to target channel
        await message.forward(chat_id=target_channel)
    except FloodWait as e:
        # Handling FloodWait exception
        print(f"FloodWait detected: Sleeping for {e.value} seconds")
        time.sleep(e.value)
    except Exception as ex:
        print(f"An error occurred: {ex}")

print("Forwarding Bot is running...")
