from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import BOT_TOKEN, BOT_TOKEN_2, SUDO_USERS
import asyncio

REPLY_ERROR = """<code>Use this command as a reply to any telegram message without any spaces.</code>"""

# /bt Command to show bot selection
@Client.on_message(filters.private & filters.command('bt') & filters.user(SUDO_USERS))
async def send_broadcast_message(client, message):
    # Show user a choice between Bot 1 or Bot 2 for broadcasting
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Use Bot 1", callback_data="use_bot_1")],
        [InlineKeyboardButton("Use Bot 2", callback_data="use_bot_2")]
    ])
    
    await message.reply("Please select which bot to use for broadcasting:", reply_markup=keyboard)

# Handle the callback query for bot selection
@Client.on_callback_query(filters.user(SUDO_USERS))
async def handle_bot_choice(client, callback_query):
    # Handle the selection of Bot 1 or Bot 2
    if callback_query.data == "use_bot_1":
        bot_token = BOT_TOKEN
        text = "You selected Bot 1 for broadcasting."
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Selected Bot 1", callback_data="no_action", disabled=True)],
            [InlineKeyboardButton("Use Bot 2", callback_data="use_bot_2")]
        ])
    elif callback_query.data == "use_bot_2":
        bot_token = BOT_TOKEN_2
        text = "You selected Bot 2 for broadcasting."
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Use Bot 1", callback_data="use_bot_1")],
            [InlineKeyboardButton("Selected Bot 2", callback_data="no_action", disabled=True)]
        ])
    
    # Edit message with bot selection
    await callback_query.message.edit(text, reply_markup=keyboard)

    # After bot selection, show broadcast options
    broadcast_options = InlineKeyboardMarkup([
        [InlineKeyboardButton("Original Broadcast", callback_data="original_broadcast")],
        [InlineKeyboardButton("Fake Broadcast", callback_data="fake_broadcast")],
        [InlineKeyboardButton("Specific Broadcast", callback_data="specific_broadcast")]
    ])
    
    await callback_query.message.reply("Please select the type of broadcast:", reply_markup=broadcast_options)

# Handle broadcast type selection
@Client.on_callback_query(filters.user(SUDO_USERS) & filters.regex("original_broadcast|fake_broadcast|specific_broadcast"))
async def handle_broadcast_type(client, callback_query):
    if callback_query.data == "original_broadcast":
        text = "You selected Original Broadcast. Please send me the message to broadcast."
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Cancel", callback_data="cancel_broadcast")]
        ])
    elif callback_query.data == "fake_broadcast":
        text = "You selected Fake Broadcast. Please send me the message to broadcast."
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Cancel", callback_data="cancel_broadcast")]
        ])
    elif callback_query.data == "specific_broadcast":
        text = "You selected Specific Broadcast. Please enter the number of users to broadcast."
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Cancel", callback_data="cancel_broadcast")]
        ])
    
    # Edit message with broadcast type selection
    await callback_query.message.edit(text, reply_markup=keyboard)

    # Wait for the user to send the broadcast message or number of users for specific broadcast
    if callback_query.data == "specific_broadcast":
        await callback_query.message.reply("Please enter the number of users for broadcast:")
    else:
        await callback_query.message.reply("Please send the message to broadcast:")

# Handle the response for the broadcast message or number of users
@Client.on_message(filters.private & filters.user(SUDO_USERS))
async def handle_broadcast_input(client, message):
    # Check if it's a broadcast message or number of users
    if message.reply_to_message and message.reply_to_message.text.startswith("Please enter the number of users"):
        # Handle specific broadcast by user input
        try:
            num_users = int(message.text)
            # Proceed with specific broadcast to num_users
            await message.reply(f"Broadcasting to {num_users} users...")
        except ValueError:
            await message.reply("Please enter a valid number of users.")
    elif message.reply_to_message and message.reply_to_message.text.startswith("Please send the message to broadcast"):
        # Handle message to broadcast
        broadcast_message = message.text
        # Proceed with sending the broadcast message to all users
        await message.reply("Broadcasting message to users...")
        
        # Broadcasting logic (Replace with actual user data and broadcast implementation)
        users = await get_users()  # Implement this to get the list of user IDs
        total = len(users)
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0
        
        for chat_id in users:
            try:
                await message.client.send_message(chat_id, broadcast_message)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await message.client.send_message(chat_id, broadcast_message)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except Exception as e:
                unsuccessful += 1
                pass

        status = f"""<b><u>Broadcast Completed</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""
        
        await message.reply(status)

# Cancel broadcast
@Client.on_callback_query(filters.user(SUDO_USERS) & filters.regex("cancel_broadcast"))
async def cancel_broadcast(client, callback_query):
    await callback_query.message.edit("Broadcast process cancelled.", reply_markup=None)
