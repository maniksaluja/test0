import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, UserIsBlocked, PeerIdInvalid
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
    except UserIsBlocked:
        print(f"Cannot send message to user {request.from_user.id}, as they have blocked the bot.")
    except PeerIdInvalid:
        print(f"Cannot send message to user {request.from_user.id}, invalid peer ID.")
    except Exception as e:
        print(f"Unexpected error: {e}")
