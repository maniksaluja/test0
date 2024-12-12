import aiohttp
import json
from config import BOT_TOKEN

base = f'https://api.telegram.org/bot{BOT_TOKEN}/'

class TelegramBot:
    def __init__(self):
        self.session = aiohttp.ClientSession()

    async def api_call(self, method, params=None):
        url = base + method
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"ok": False, "error_code": response.status, "description": await response.text()}
        except aiohttp.ClientError as e:
            return {"ok": False, "error": str(e)}

    async def get_chat_member(self, chat_id, user_id):
        return await self.api_call("getChatMember", {"chat_id": chat_id, "user_id": user_id})

    async def send_message(self, chat_id, text, reply_markup=None):
        params = {"chat_id": chat_id, "text": text}
        if reply_markup:
            params["reply_markup"] = json.dumps(reply_markup)
        return await self.api_call("sendMessage", params)

    async def edit_message_text(self, chat_id, msg_id, text, reply_markup=None):
        params = {"chat_id": chat_id, "message_id": msg_id, "text": text}
        if reply_markup:
            params["reply_markup"] = json.dumps(reply_markup)
        return await self.api_call("editMessageText", params)

    async def delete_message(self, chat_id, msg_id):
        return await self.api_call("deleteMessage", {"chat_id": chat_id, "message_id": msg_id})

    async def send_document(self, chat_id, file_id):
        return await self.api_call("sendDocument", {"chat_id": chat_id, "document": file_id})

    async def send_video(self, chat_id, file_id):
        return await self.api_call("sendVideo", {"chat_id": chat_id, "video": file_id})

    async def send_photo(self, chat_id, photo, caption=None, reply_markup=None):
        params = {"chat_id": chat_id, "photo": photo}
        if caption:
            params["caption"] = caption
        if reply_markup:
            params["reply_markup"] = json.dumps(reply_markup)
        return await self.api_call("sendPhoto", params)

    async def edit_message_caption(self, chat_id, msg_id, caption, reply_markup=None):
        params = {"chat_id": chat_id, "message_id": msg_id, "caption": caption}
        if reply_markup:
            params["reply_markup"] = json.dumps(reply_markup)
        return await self.api_call("editMessageCaption", params)

    async def close(self):
        await self.session.close()
