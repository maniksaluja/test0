from time import time
from Database.encr import get_encr
from Database.auto_delete import get, update
from config import AUTO_DELETE_TIME
from pyrogram import Client
import asyncio
import logging

# Setup logging for better error tracking
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def auto_delete_message(_, message_id: int, user_id: int):
    """
    Handles the auto-delete process for a message.
    - Fetches the deletion time and performs auto delete if the time exceeds.
    """
    try:
        # Fetch stored data for the user
        dic = await get(user_id)

        if not dic:
            logging.warning(f"No delete data found for user {user_id}")
            return

        # Check if message is already scheduled for deletion
        if str(message_id) not in dic:
            logging.warning(f"Message {message_id} not found in stored data for user {user_id}")
            return

        # Extract message deletion info
        delete_info = dic.get(str(message_id))
        deletion_time = delete_info[1] + AUTO_DELETE_TIME

        # Check if the time has come to delete the message
        if time() > deletion_time:
            await delete_message(_, message_id)
            del dic[str(message_id)]  # Remove the deleted message info
            await update(user_id, dic)  # Update the database

            logging.info(f"Message {message_id} deleted for user {user_id}")
        else:
            logging.info(f"Message {message_id} not yet ready for deletion for user {user_id}")
    except Exception as e:
        logging.error(f"Error in auto delete for message {message_id}: {str(e)}")

async def delete_message(_, message_id: int):
    """
    Deletes a message by its message_id
    """
    try:
        await _.delete_messages(_, message_id)
        logging.info(f"Successfully deleted message {message_id}")
    except Exception as e:
        logging.error(f"Failed to delete message {message_id}: {str(e)}")

# Update auto-delete entries
async def update_auto_delete(user_id: int, message_id: int, reply_message_id: int, message_time: float, link: str):
    """
    Updates the auto delete entry in the database.
    """
    try:
        dic = await get(user_id)
        dic[str(message_id)] = [str(reply_message_id), message_time, link]
        await update(user_id, dic)
        logging.info(f"Auto delete entry updated for message {message_id} and user {user_id}")
    except Exception as e:
        logging.error(f"Error updating auto delete entry for message {message_id} and user {user_id}: {str(e)}")

# Async loop to check and delete expired messages periodically
async def check_for_expired_messages(_):
    """
    Checks for expired messages and deletes them based on time.
    This function should be run periodically, for example, every 5 minutes.
    """
    try:
        # Fetch users from database who have auto delete entries
        users = await get_users_with_auto_delete()
        
        for user in users:
            dic = await get(user)
            for message_id, delete_info in dic.items():
                deletion_time = delete_info[1] + AUTO_DELETE_TIME
                if time() > deletion_time:
                    await delete_message(_, int(message_id))  # Delete the expired message
                    del dic[message_id]  # Remove the entry
                    await update(user, dic)  # Update the database
                    logging.info(f"Expired message {message_id} deleted for user {user}")
    except Exception as e:
        logging.error(f"Error in checking for expired messages: {str(e)}")

async def get_users_with_auto_delete():
    """
    Fetches users with auto delete entries in the database.
    """
    # Fetch all users who have scheduled messages to delete
    try:
        users = await get_all_users()  # Placeholder for fetching all users
        return [user for user in users if await has_auto_delete(user)]
    except Exception as e:
        logging.error(f"Error fetching users with auto delete: {str(e)}")
        return []

async def has_auto_delete(user_id: int):
    """
    Check if a user has any auto delete scheduled messages.
    """
    dic = await get(user_id)
    return bool(dic)
