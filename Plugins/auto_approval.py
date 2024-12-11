from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, FloodWait, BadRequest  # Add necessary imports
from config import FSUB
from Database.settings import get_settings

@Client.on_chat_join_request(filters.chat(FSUB))
async def cjr(client: Client, request):
    """
    Automatically approve chat join requests if auto-approval is enabled.
    """
    settings = await get_settings()
    if not settings['auto_approval']:
        return

    try:
        # Approve the chat join request
        await client.approve_chat_join_request(
            request.chat.id,
            request.from_user.id
        )
        # Send a welcome message to the user
        await client.send_message(request.from_user.id, "Hi")
    except UserAlreadyParticipant:
        pass  # Ignore if user is already a participant
    except FloodWait as e:
        print(f"Flood wait error: {e.x} seconds")
        await asyncio.sleep(e.x)
    except BadRequest as e:
        if e.MESSAGE == "400 HIDE_REQUESTER_MISSING":
            print("Hide requester missing, can't approve join request.")
        else:
            print(f"BadRequest error: {e.MESSAGE}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

# Your Pyrogram client setup code here
