from config import SUDO_USERS, EXPIRY_TIME
from pyrogram import Client, filters
from Database.privileges import *
from .tasks import IKM, IKB
from templates import SU_TEXT, EXPIRE_TEXT
import datetime
from . import tryer
from config import CONNECT_TUTORIAL_LINK, SU_IMAGE
import asyncio
from Database.subscription import get_all_subs, del_sub, active_sub
from main import app
import time

exp = int(EXPIRY_TIME * 86400)

def build_markup_2(lis, user_id, activate=True):
    return IKM(
        [
            [IKB("𝘈𝘭𝘰𝘸 𝘉𝘢𝘵𝘤𝘩", callback_data="answer"), IKB("✅" if lis[0] else "❌", callback_data=f"toggleab_{user_id}")],
            [IKB("𝘚𝘶𝘱𝘦𝘳 𝘜𝘴𝘦𝘳", callback_data="answer"), IKB("✅" if lis[1] else "❌", callback_data=f"togglesu_{user_id}")],
            [IKB("𝘔𝘺 𝘤𝘰𝘯𝘵𝘦𝘯𝘵", callback_data="answer"), IKB("✅" if lis[2] else "❌", callback_data=f"togglemc_{user_id}")],
            [IKB("𝘈𝘭𝘭𝘰𝘸 𝘋𝘔", callback_data="answer"), IKB("✅" if lis[3] else "❌", callback_data=f"togglead_{user_id}")],
            [IKB("𝘈𝘤𝘵𝘪𝘷𝘢𝘵𝘦" if activate else "𝘋𝘦𝘢𝘤𝘵𝘪𝘷𝘢𝘵𝘦", callback_data=f"activate_{user_id}")]
        ]
    )

@Client.on_message(filters.command("super") & filters.user(SUDO_USERS) & filters.private)
async def pay_settings(_, m):
    try:
        id = int(m.text.split()[1])
    except:
        return await m.reply("**Usage:** `/super [ID]`")
    priv = await get_privileges(id)
    subs = await get_all_subs()
    if id in subs:
        sec = int(time.time() - subs[id])
        sec = exp - sec
        tar = datetime.datetime.now() + datetime.timedelta(seconds=sec)
        await m.reply(f"**This User Already SuperUser**\n<pre>Expiry: {tar.day}-{tar.month}-{tar.year}</pre>", reply_markup=build_markup_2(priv, id, activate=False))
    else:
        await m.reply(f"**Before Activate Give Access..**", reply_markup=build_markup_2(priv, id))

me = None
async def activate_cbq(_, q):
    global me
    if not me:
        me = await _.get_me()
    id = int(q.data.split("_")[1])
    priv = await get_privileges(id)
    subs = await get_all_subs()
    if not id in subs:
        act = True if True in priv else False
        if not act:
            return await q.answer("Atleast one privilege should be up to activate.", show_alert=True)
        markup = None
        if priv[1]:
            markup = IKM([[IKB("𝘊𝘰𝘯𝘯𝘦𝘤𝘵", callback_data='connect'), IKB("𝘛𝘶𝘵𝘰𝘳𝘪𝘢𝘭", url=CONNECT_TUTORIAL_LINK)]])
        await active_sub(id)
        tar = datetime.datetime.now() + datetime.timedelta(seconds=exp)
        await tryer(_.send_photo, id, SU_IMAGE, caption=SU_TEXT.format((await _.get_users(id)).mention, f'{tar.day}-{tar.month}-{tar.year}'), reply_markup=markup)
        await q.answer()
        await tryer(q.edit_message_text, 'Activated.', reply_markup=None)
    else:
        deact = False if True in priv else True
        if not deact:
            return await q.answer("Disable all privileges to deactivate.", show_alert=True)
        await del_sub(id)
        markup = IKM([[IKB('𝘛𝘢𝘭𝘬 𝘛𝘰 𝘈𝘥𝘮𝘪𝘯', url='https://t.me/CuteGirlTG?text=%2A%2A%20I%20saw%20my%20subscription%20is%20stopped%20by%20admin%20but%20why%3F%20%2A%2A')]])
        await tryer(_.send_message, id, '**Your MemeberShip Cancelled By Admin**', reply_markup=markup)
        await q.answer()
        await tryer(q.edit_message_text, 'Deactivated.', reply_markup=None)

async def pay_cbq(_, q):
    id = int(q.data.split("_")[1])
    priv = await get_privileges(id)
    sub = id in await get_all_subs()
    if q.data.startswith("toggleab"):
        priv[0] = not priv[0]
    elif q.data.startswith("togglesu"):
        priv[1] = not priv[1]
    elif q.data.startswith("togglemc"):
        priv[2] = not priv[2]
    elif q.data.startswith("togglead"):
        priv[3] = not priv[3]
    elif q.data.startswith('activate'):
        return await activate_cbq(_, q)
    await update_privileges(id, priv[0], priv[1], priv[2], priv[3])
    await q.answer()
    await q.edit_message_reply_markup(reply_markup=build_markup_2(priv, id, activate=not sub)) 

renew = IKM([[IKB("𝘉𝘶𝘺 𝘈𝘨𝘢𝘪𝘯", url="https://t.me/CuteGirlTG?text=**Hii%20I%20Want%20To%20Renew%20My%20Membership...**")]])

async def task():
    while True:
        subs = await get_all_subs()
        for x in subs:
            if int(time.time() - subs[x]) >= exp:
                await del_sub(x)
                await update_privileges(x, False, False, False, False) 
                mention = (await tryer(app.get_users, x)).mention
                await tryer(app.send_photo, x, SU_IMAGE, caption=EXPIRE_TEXT.format(mention, mention), reply_markup=renew)
        await asyncio.sleep(exp/1000)
        
asyncio.create_task(task())
                
