from pyrogram import Client
from pyrogram.types import CallbackQuery
from config import SUDO_USERS, AUTO_SAVE_CHANNEL_ID
from .settings import markup
from Database.settings import get_settings, update_settings
from .paid import pay_cbq

@Client.on_callback_query()
async def cbq(_, q: CallbackQuery):
    data = q.data
    if data == 'sharewithme':
        settings = await get_settings()
        await q.answer('Thank You', show_alert=True)
        new = await q.edit_message_reply_markup(reply_markup=None)
        if not settings['auto_save']:
            await new.copy(AUTO_SAVE_CHANNEL_ID)
        return
    elif data == 'connect':
        await q.answer()
        return await q.message.reply('Type /connect.')
    if not q.from_user.id in SUDO_USERS:
        return await q.answer()
    if data == 'answer':
        await q.answer()
    elif data == 'toggle_approval':
        dic = await get_settings()
        dic['auto_approval'] = not dic['auto_approval']
        mark = markup(dic)
        await q.answer()
        await update_settings(dic)
        await q.edit_message_reply_markup(reply_markup=mark)
    elif data == 'toggle_join':
        dic = await get_settings()
        dic['join'] = not dic['join']
        mark = markup(dic)
        await q.answer()
        await update_settings(dic)
        await q.edit_message_reply_markup(reply_markup=mark)
    elif data == 'toggle_leave':
        dic = await get_settings()
        dic['leave'] = not dic['leave']
        mark = markup(dic)
        await q.answer()
        await update_settings(dic)
        await q.edit_message_reply_markup(reply_markup=mark)
    elif data == 'toggle_image':
        dic = await get_settings()
        dic['image'] = not dic['image']
        mark = markup(dic)
        await q.answer()
        await update_settings(dic)
        await q.edit_message_reply_markup(reply_markup=mark)
    elif data == 'toggle_gen':
        dic = await get_settings()
        dic['generate'] = 20 if dic.get('generate', 20) == 1 else 1
        mark = markup(dic)
        await q.answer()
        await update_settings(dic)
        await q.edit_message_reply_markup(reply_markup=mark)
    elif data == "toggle_save":
        dic = await get_settings()
        dic['auto_save'] = not dic.get('auto_save', False)
        mark = markup(dic)
        await q.answer()
        await update_settings(dic)
        await q.edit_message_reply_markup(reply_markup=mark)
    elif data.startswith(("toggleab", "togglesu", "togglemc", "togglead", "activate")):
        await pay_cbq(_, q)
        
