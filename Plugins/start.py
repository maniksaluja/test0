for ok in haha:
                    if not ok:
                        continue
                    dic[str(ok.id)] = [str(ok1.id), time(), f'https://t.me/{me.username}?start=batchone{encr}']
                await update(m.from_user.id, dic)
            if okkie:
                await okkie.delete()
            return
        elif command.startswith('batchtwo'):
            encr = command[8:]
            for i in chats:
                if not await check_fsub(m.from_user.id):
                    #txt = 'Make sure you have joined all chats below.'
                    mark = await markup(_, f'https://t.me/{me.username}?start=batchtwo{encr}')
                    return await m.reply(TRY_AGAIN_TEXT.format(m.from_user.mention), reply_markup=mark)
            std = await m.reply_sticker(STICKER_ID)
            spl = decrypt(encr).split('|')[0].split('-')
            st = Char2Int(spl[0])
            en = Char2Int(spl[1])
            if st == en:
                messes = [await _.get_messages(DB_CHANNEL_2_ID, st)]
            else:
                mess_ids = []
                while en - st + 1 > 200:
                    mess_ids.append(list(range(st, st + 200)))
                    st += 200
                if en - st + 1 > 0:
                    mess_ids.append(list(range(st, en+1)))
                messes = []
                for x in mess_ids:
                    messes += (await _.get_messages(DB_CHANNEL_2_ID, x))
            okkie = None
            if len(messes) > 10:
                okkie = await m.reply("It's Take Few Seconds....")
            haha = []
            if not prem:
                for x in messes:
                    if not x:
                        continue
                    if x.empty:
                        continue
                    gg = await tryer(x.copy, m.from_user.id, caption=None, reply_markup=None, protect_content=True)
                    haha.append(gg)
                    await asyncio.sleep(1)
            else:
                for x in messes:
                    if not x:
                        continue
                    if x.empty:
                        continue
                    gg = await tryer(x.copy, m.from_user.id, caption=None, reply_markup=None)
                    haha.append(gg)
                    await asyncio.sleep(1)
                    # tasks.append(asyncio.create_task(x.copy(m.from_user.id)))
            await std.delete()
            if AUTO_DELETE_TIME != 0:
                ok1 = await m.reply(AUTO_DELETE_TEXT.format(AUTO_DELETE_STR))
                dic = await get(m.from_user.id)
                for ok in haha:
                    if not ok:
                        continue
                    dic[str(ok.id)] = [str(ok1.id), time(), f'https://t.me/{me.username}?start=batchtwo{encr}']
                await update(m.from_user.id, dic)
            if okkie:
                await okkie.delete()
            return
    else:
        await m.reply(START_MESSAGE_2.format(m.from_user.mention), reply_markup=await start_markup(_))

@Client.on_message(filters.command('start') & filters.private)
async def start_func(_, m):
    user_id = m.from_user.id
    if user_id in control_batch:
        return
    control_batch.append(user_id)
    try:
        await start(_, m)
    except:
        pass
    control_batch.remove(user_id) if user_id in control_batch else None
