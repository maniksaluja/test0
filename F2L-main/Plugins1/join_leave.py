from pyrogram import Client, filters
from pyrogram.types import ChatMemberUpdated
from config import (
    FSUB_1, FSUB_2, TUTORIAL_LINK,
)
from templates import LEAVE_MESSAGE
from Database.settings import get_settings
from Plugins.start import get_chats
from pyrogram.types import InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM

FSUB = [FSUB_1, FSUB_2]

markup = None

async def build(_):
    global markup
    if not markup:
        chats = (await get_chats(_))
        new = []
        for x in chats:
            y = await _.create_chat_invite_link(x.id, creates_join_request=True)
            new.append(y.invite_link)
        for x, y in enumerate(new):
            chats[x].invite_link = y
        chat = chats[0]
        chat1 = chats[1]
        markup = IKM(
            [
                [
                    IKB("ᴊᴏɪɴ ᴀɢᴀɪɴ", url=chat.invite_link),
                    IKB("ᴄᴏᴅᴇ ʟᴀɴɢᴜᴀɢᴇ", url="https://t.me/Utra_XYZ/9")
                ],
                [
                    IKB('ʜᴏᴡ ᴛᴏ ᴜsᴇ ᴛᴇʀᴀʙᴏx ʙᴏᴛ', url=TUTORIAL_LINK)
                ]
            ]
        )
    return markup

@Client.on_chat_member_updated(filters.chat(FSUB_1))
async def jl(_: Client, cmu: ChatMemberUpdated):
    user = cmu.from_user
    left = cmu.old_chat_member and not cmu.new_chat_member
    joined = cmu.new_chat_member and not cmu.old_chat_member
    if not left and not joined:
        return
    settings = await get_settings()
    markup = await build(_)
    if joined:
        """
        if not settings['join']:
            return
        try:
            if JOIN_IMAGE:
                await _.send_photo(user.username if user.username else user.id, JOIN_IMAGE, caption=JOIN_MESSAGE, reply_markup=markup)
            else:
                await _.send_message(user.username if user.username else user.id, JOIN_MESSAGE, reply_markup=markup)
        except Exception as e:
            print(e)
        """
        ...
    else:
        if not settings['leave']:
            return
        try:
            # if LEAVE_IMAGE:
            #     await _.send_photo(user.username if user.username else user.id, LEAVE_IMAGE, caption=LEAVE_MESSAGE, reply_markup=markup)
            # else:
            #     await _.send_message(user.username if user.username else user.id, LEAVE_MESSAGE, reply_markup=markup)
            await _.send_voice(user.username if user.username else user.id, 'Voice/uff.ogg', caption=LEAVE_MESSAGE, reply_markup=markup)
        except Exception as e:
            print(e)
