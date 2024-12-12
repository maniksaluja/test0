import logging
import re
from typing import Union

from pyrogram import raw, utils
from pyrogram.errors import PeerIdInvalid

log = logging.getLogger(__name__)

MIN_CHANNEL_ID = -1002147483647
MAX_CHANNEL_ID = -1000000000000
MIN_CHAT_ID = -2147483647
MAX_USER_ID_OLD = 2147483647
MAX_USER_ID = 999999999999

def get_peer_type(peer_id: int) -> str:
    if peer_id < 0:
        if MIN_CHAT_ID <= peer_id:
            return "chat"
        if peer_id < MAX_CHANNEL_ID:
            return "channel"
    elif 0 < peer_id <= MAX_USER_ID:
        return "user"
    raise ValueError(f"Peer id invalid: {peer_id}")

class ResolvePeer:
    def __init__(self, cl) -> None:
        self.cl = cl

    async def resolve_peer(self, peer_id: Union[int, str]) -> Union[raw.base.InputPeer, raw.base.InputUser, raw.base.InputChannel]:
        if not self.cl.is_connected:
            raise ConnectionError("Client has not been started yet")

        # Self/Me optimization
        if isinstance(peer_id, str) and peer_id in ("self", "me"):
            return raw.types.InputPeerSelf()

        # Cleanup peer_id string
        if isinstance(peer_id, str):
            peer_id = re.sub(r"[@+\s]", "", peer_id.lower())

            # Resolve username
            if not peer_id.isdigit():
                try:
                    return await self.cl.storage.get_peer_by_username(peer_id)
                except KeyError:
                    result = await self.cl.invoke(
                        raw.functions.contacts.ResolveUsername(username=peer_id)
                    )
                    await self.cl.fetch_peers(result)
                    return await self.cl.storage.get_peer_by_username(peer_id)

            # Resolve phone number
            try:
                return await self.cl.storage.get_peer_by_phone_number(peer_id)
            except KeyError:
                raise PeerIdInvalid

        # Resolve numeric peer_id
        peer_id = int(peer_id)
        peer_type = get_peer_type(peer_id)

        try:
            return await self.cl.storage.get_peer_by_id(peer_id)
        except KeyError:
            if peer_type == "user":
                result = await self.cl.invoke(
                    raw.functions.users.GetUsers(
                        id=[raw.types.InputUser(user_id=peer_id, access_hash=0)]
                    )
                )
                await self.cl.fetch_peers(result)
            elif peer_type == "chat":
                result = await self.cl.invoke(
                    raw.functions.messages.GetChats(id=[-peer_id])
                )
                # Process chats properly
                for chat in result.chats:
                    await self.cl.fetch_peers([chat])
            else:  # channel
                result = await self.cl.invoke(
                    raw.functions.channels.GetChannels(
                        id=[raw.types.InputChannel(channel_id=utils.get_channel_id(peer_id), access_hash=0)]
                    )
                )
                # Process channels properly
                for channel in result.chats:
                    await self.cl.fetch_peers([channel])

        try:
            return await self.cl.storage.get_peer_by_id(peer_id)
        except KeyError:
            raise PeerIdInvalid

    async def send_message_to_channel(self, channel_id: int, message: str):
        """Send message to a channel after ensuring bot has admin access."""
        try:
            await self.ensure_bot_can_message(channel_id)
            await self.cl.send_message(chat_id=channel_id, text=message)
        except Exception as e:
            log.error(f"Failed to send message: {e}")

    async def ensure_bot_can_message(self, channel_id: int):
        """Ensure bot has admin rights before sending a message."""
        try:
            member = await self.cl.get_chat_member(channel_id, "me")
            if member.status not in ["administrator", "creator"]:
                raise PermissionError("Bot does not have admin rights in the channel.")
        except Exception as e:
            log.error(f"Error checking admin status: {e}")
            raise
