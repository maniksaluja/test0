import logging
import re
from typing import Union
import pyrogram
from pyrogram import raw, utils
from pyrogram.errors import PeerIdInvalid

log = logging.getLogger(__name__)

MIN_CHANNEL_ID = -1002147483647
MAX_CHANNEL_ID = -1000000000000
MIN_CHAT_ID = -2147483647
MAX_USER_ID_OLD = 2147483647
MAX_USER_ID = 999999999999

# Caching to store resolved peer IDs for faster lookups
peer_cache = {}

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

    async def resolve_peer(
        self: "pyrogram.Client",
        peer_id: Union[int, str]
    ) -> Union[raw.base.InputPeer, raw.base.InputUser, raw.base.InputChannel]:
        """Get the InputPeer of a known peer id.
        Useful whenever an InputPeer type is required.
        """
        if not self.cl.is_connected:
            raise ConnectionError("Client has not been started yet")

        # Check if the peer ID is already in the cache
        if peer_id in peer_cache:
            log.debug(f"Peer ID {peer_id} found in cache.")
            return peer_cache[peer_id]

        try:
            # First try to resolve from storage
            return await self.cl.storage.get_peer_by_id(peer_id)
        except KeyError:
            log.debug(f"Peer ID {peer_id} not found in storage. Attempting to resolve.")

            if isinstance(peer_id, str):
                if peer_id in ("self", "me"):
                    return raw.types.InputPeerSelf()

                # Clean up the username for valid format
                peer_id = re.sub(r"[@+\s]", "", peer_id.lower())
                try:
                    int(peer_id)  # Try to convert to int
                except ValueError:
                    try:
                        # Resolve by username
                        return await self.cl.storage.get_peer_by_username(peer_id)
                    except KeyError:
                        log.debug(f"Username {peer_id} not found in storage. Invoking ResolveUsername.")
                        await self.cl.invoke(raw.functions.contacts.ResolveUsername(username=peer_id))
                        resolved_peer = await self.cl.storage.get_peer_by_username(peer_id)
                        peer_cache[peer_id] = resolved_peer  # Cache the resolved peer
                        return resolved_peer
                else:
                    try:
                        # Resolve by phone number
                        return await self.cl.storage.get_peer_by_phone_number(peer_id)
                    except KeyError:
                        raise PeerIdInvalid

            peer_type = get_peer_type(peer_id)
            if peer_type == "user":
                await self.cl.fetch_peers(
                    await self.cl.invoke(
                        raw.functions.users.GetUsers(
                            id=[raw.types.InputUser(user_id=peer_id, access_hash=0)]
                        )
                    )
                )
            elif peer_type == "chat":
                await self.cl.invoke(raw.functions.messages.GetChats(id=[-peer_id]))
            else:
                await self.cl.invoke(
                    raw.functions.channels.GetChannels(
                        id=[raw.types.InputChannel(channel_id=utils.get_channel_id(peer_id), access_hash=0)]
                    )
                )

            # Cache the resolved peer for future use
            try:
                resolved_peer = await self.cl.storage.get_peer_by_id(peer_id)
                peer_cache[peer_id] = resolved_peer
                return resolved_peer
            except KeyError:
                raise PeerIdInvalid

        except Exception as e:
            log.error(f"An unexpected error occurred: {str(e)}")
            raise
