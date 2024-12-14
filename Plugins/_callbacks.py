from pyrogram import Client
from pyrogram.types import CallbackQuery
from config import SUDO_USERS, AUTO_SAVE_CHANNEL_ID
from .settings import markup
from Database.settings import get_settings, update_settings
from .paid import pay_cbq

@Client.on_callback_query()
async def cbq(_, q: CallbackQuery):
    data = q.data
    user_id = q.from_user.id

    # Handle 'sharewithme' callback
    if data == 'sharewithme':
        settings = await get_settings()
        await q.answer('Thank You', show_alert=True)
        new_msg = await q.edit_message_reply_markup(reply_markup=None)
        if not settings['auto_save']:
            await new_msg.copy(AUTO_SAVE_CHANNEL_ID)
        return

    # Handle 'connect' callback
    if data == 'connect':
        await q.answer()
        return await q.message.reply('Type /connect.')

    # Restrict access to sudo users
    if user_id not in SUDO_USERS:
        return await q.answer()

    # Define helper function for toggling settings
    async def toggle_setting(setting_key, default_value=False):
        settings = await get_settings()
        settings[setting_key] = not settings.get(setting_key, default_value)
        markup_content = markup(settings)
        await update_settings(settings)
        return settings, markup_content

    # Handle toggling various settings
    toggle_actions = {
        'toggle_approval': 'auto_approval',
        'toggle_join': 'join',
        'toggle_leave': 'leave',
        'toggle_image': 'image',
        'toggle_gen': 'generate',
        'toggle_save': 'auto_save',
        'toggle_logs': 'logs'
    }

    if data in toggle_actions:
        setting_key = toggle_actions[data]
        settings, mark = await toggle_setting(setting_key)
        await q.answer()
        await q.edit_message_reply_markup(reply_markup=mark)

    # Handle 'activate' and 'toggle' prefixes (paid-related actions)
    elif data.startswith(("toggleab", "togglesu", "togglemc", "togglead", "activate")):
        await pay_cbq(_, q)
