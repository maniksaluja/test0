from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, FloodWait, BadRequest  # Add necessary imports
from config import FSUB
from Database.settings import get_settings
import asyncio

@Client.on_chat_join_request(filters.chat(FSUB))
async def cjr(client: Client, request):
    """
    Automatically approve chat join requests if auto-approval is enabled.
    """
    settings = await get_settings()

    # Auto approval setting check
    if not settings.get('auto_approval', False):
        return

    try:
        # Try to approve the join request
        await client.approve_chat_join_request(request.chat.id, request.from_user.id)
        
        # Send a welcome message to the new user
        await client.send_message(request.from_user.id, "Hi! Welcome to the group!")
        
        # Optionally log successful approval
        print(f"Approved join request for {request.from_user.id}")

    except UserAlreadyParticipant:
        # Ignore if the user is already a participant
        print(f"User {request.from_user.id} is already a participant.")

    except FloodWait as e:
        # Handle FloodWait error and retry after waiting for the specified time
        print(f"Flood wait error: {e.x} seconds. Retrying...")
        await asyncio.sleep(e.x)  # Wait for the specified amount of time
        # Retry the join request approval after waiting
        await cjr(client, request)

    except BadRequest as e:
        # Specific handling for BadRequest errors
        if e.MESSAGE == "400 HIDE_REQUESTER_MISSING":
            print("Hide requester missing, can't approve join request.")
        else:
            print(f"BadRequest error: {e.MESSAGE}")

    except Exception as e:
        # Catch any unexpected exceptions
        print(f"An unexpected error occurred: {str(e)}")
