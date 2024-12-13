from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, FloodWait, BadRequest
from config import FSUB
from Database.settings import get_settings
import asyncio

@Client.on_chat_join_request(filters.chat(FSUB))
async def cjr(client: Client, request):
    settings = await get_settings()

    if not settings.get('auto_approval', False):
        return

    try:
        # Check if the user is already a participant
        chat_member = await client.get_chat_member(request.chat.id, request.from_user.id)
        if chat_member.status in ["member", "administrator", "creator"]:
            print(f"User {request.from_user.id} is already a participant. Skipping approval.")
            return  # Skip approval if already a participant

        # Approve the join request if not already a participant
        await client.approve_chat_join_request(request.chat.id, request.from_user.id)

        # Send welcome message
        await client.send_message(request.from_user.id, "Hi! Welcome to the group!")

        print(f"Approved join request for {request.from_user.id}")

    except UserAlreadyParticipant:
        print(f"User {request.from_user.id} is already a participant. Skipping approval.")
    except FloodWait as e:
        print(f"Flood wait error: {e.x} seconds. Retrying...")
        await asyncio.sleep(e.x)  # Wait for the specified amount of time
        await cjr(client, request)  # Retry after waiting
    except BadRequest as e:
        if e.MESSAGE == "400 HIDE_REQUESTER_MISSING":
            print("Hide requester missing, can't approve join request.")
        elif "not a member of this chat" in e.MESSAGE:
            print(f"User {request.from_user.id} is not a member of the chat.")
        elif "blocked you" in e.MESSAGE:
            print(f"User {request.from_user.id} has blocked the bot. Skipping approval.")
        else:
            print(f"BadRequest error: {e.MESSAGE}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
