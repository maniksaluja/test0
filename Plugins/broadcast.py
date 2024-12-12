from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from config import BOT_TOKEN, BOT_TOKEN_2, SUDO_USERS
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio

REPLY_ERROR = """<code>Use this command as a reply to any telegram message with out any spaces.</code>"""

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
    if callback_query.data == "use_bot_1":
        bot_token = BOT_TOKEN
        await callback_query.message.edit("You selected Bot 1 for broadcasting.")
    elif callback_query.data == "use_bot_2":
        bot_token = BOT_TOKEN_2
        await callback_query.message.edit("You selected Bot 2 for broadcasting.")
    
    # Now continue with broadcasting using the selected bot token
    chosen_client = Client("ChosenBot", bot_token=bot_token)
    await chosen_client.start()

    # Show message asking for the broadcast message
    broadcast_message = await callback_query.message.reply("Please send the message you want to broadcast:")

    # Wait for the user's reply with the message to broadcast
    reply_message = await client.listen(callback_query.message.chat.id)
    
    if reply_message:
        # Start broadcasting
        await broadcast_message.edit("Broadcasting in progress...")

        users = await get_users()  # You should define get_users to get the list of user IDs
        total = len(users)
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0
        
        pls_wait = await broadcast_message.reply("<i>Broadcasting Message.. This will Take Some Time</i>")
        err = None
        for chat_id in users:
            try:
                await chosen_client.send_message(chat_id, reply_message.text)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await chosen_client.send_message(chat_id, reply_message.text)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)  # Implement this to remove blocked users from your DB
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)  # Implement this to remove deleted accounts from your DB
                deleted += 1
            except Exception as e:
                unsuccessful += 1
                err = e
                pass

        # Broadcasting status update
        status = f"""<b><u>Broadcast Completed</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>

Error: {err}"""
        
        # Final status
        await pls_wait.edit(status)

    # Stop the chosen client after broadcasting is done
    await chosen_client.stop()

# Handle /msg command (similar to your /m command)
@Client.on_message(filters.private & filters.command('msg') & filters.user(SUDO_USERS))
async def send_message(_, m):
    reply = m.reply_to_message
    if not reply:
        return await m.reply("Reply to a message.")
    try:
        id = int(m.text.split()[1])
    except:
        return await m.reply("Enter ID to send message.")
    if reply.forward_from or reply.forward_from_chat:
        forward = True
    else:
        forward = False
    if forward:
        await reply.forward(id)
    else:
        await reply.copy(id)
    await m.reply("Done.")
