from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, FloodWait, BadRequest
from config import FSUB
from Database.settings import get_settings
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def is_user_already_participant(client, chat_id, user_id):
    """Check if the user is already a participant in the chat."""
    try:
        chat_member = await client.get_chat_member(chat_id, user_id)
        if chat_member.status in ["member", "administrator", "creator"]:
            logger.info(f"User {user_id} is already a participant. Skipping approval.")
            return True
    except Exception as e:
        logger.error(f"Error checking participant status for {user_id}: {str(e)}")
    return False

async def approve_request(client, chat_id, user_id):
    """Helper function to approve join request."""
    try:
        await client.approve_chat_join_request(chat_id, user_id)
        logger.info(f"Approved join request for {user_id}")
        return True
    except UserAlreadyParticipant:
        logger.info(f"User {user_id} is already a participant. Skipping approval.")
        return False
    except Exception as e:
        logger.error(f"Error while approving request for {user_id}: {str(e)}")
        return False

async def send_welcome_message(client, user_id):
    """Send a welcome message to the new user."""
    try:
        await client.send_message(user_id, "Hi! Welcome to the group!")
        logger.info(f"Sent welcome message to {user_id}")
    except Exception as e:
        logger.error(f"Error sending welcome message to {user_id}: {str(e)}")

@Client.on_chat_join_request(filters.chat(FSUB))
async def cjr(client: Client, request):
    settings = await get_settings()

    if not settings.get('auto_approval', False):
        return

    if await is_user_already_participant(client, request.chat.id, request.from_user.id):
        return

    if await approve_request(client, request.chat.id, request.from_user.id):
        await send_welcome_message(client, request.from_user.id)

    else:
        try:
            await client.approve_chat_join_request(request.chat.id, request.from_user.id)
            await client.send_message(request.from_user.id, "Hi! Welcome to the group!")
        except FloodWait as e:
            logger.warning(f"Flood wait error: {e.x} seconds. Retrying...")
            await asyncio.sleep(e.x)
            await cjr(client, request)
        except BadRequest as e:
            if e.MESSAGE == "400 HIDE_REQUESTER_MISSING":
                logger.warning("Hide requester missing, can't approve join request.")
            elif "not a member of this chat" in e.MESSAGE:
                logger.warning(f"User {request.from_user.id} is not a member of the chat.")
            elif "blocked you" in e.MESSAGE:
                logger.warning(f"User {request.from_user.id} has blocked the bot. Skipping approval.")
            else:
                logger.error(f"BadRequest error: {e.MESSAGE}")
        except Exception as e:
            logger.error(f"Unexpected error occurred: {str(e)}")
