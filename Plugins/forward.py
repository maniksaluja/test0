from pyrogram import Client, filters
from pyrogram.errors import FloodWait, RPCError
import time
from config import forwarding_enabled, source_channel, target_channel, API_ID2, API_HASH2, BOT_TOKEN_2

# Initialize the second Pyrogram Client with second bot credentials
app = Client(
    "second_forward_bot",  # Unique session name
    api_id=API_ID2,
    api_hash=API_HASH2,
    bot_token=BOT_TOKEN_2
)

# Function to set up forwarding handlers
@app.on_message(filters.channel & filters.chat(source_channel))
async def forward_posts(client, message):
    if not forwarding_enabled:
        print("Forwarding is disabled. Skipping message.")
        return

    try:
        await message.forward(chat_id=target_channel)
        print(f"Message ID {message.message_id} forwarded to {target_channel}.")
    except FloodWait as e:
        print(f"FloodWait detected: Sleeping for {e.value} seconds")
        time.sleep(e.value)
    except RPCError as rpc_err:
        print(f"RPC Error: {rpc_err}")
    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")

# Run the bot
if __name__ == "__main__":
    print("Second bot is starting...")
    app.run()  # Start the second bot with its own credentials
    print("Second bot is running...")
