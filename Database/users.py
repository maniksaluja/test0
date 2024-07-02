from . import db
from config import BOT_TOKEN, BOT_TOKEN_2

db1 = db[BOT_TOKEN.split(":")[0] + '_users']
db2 = db[BOT_TOKEN_2.split(":")[0] + '_users']

async def add_user_2(user_id):
    if await is_user_2(user_id):
        return
    await db2.insert_one({'user_id': user_id})

async def is_user_2(user_id) -> bool:
    x = await db2.find_one({'user_id': user_id})
    if x:
        return True
    return False

async def get_users_2() -> list[int]:
    x = db2.find()
    x = await x.to_list(length=None)
    return [y['user_id'] for y in x]

async def get_users_count_2() -> int:
    x = db2.find()
    return len(await x.to_list(length=None))

async def add_user(user_id):
    if await is_user(user_id):
        return
    await db1.insert_one({'user_id': user_id})

async def is_user(user_id) -> bool:
    x = await db1.find_one({'user_id': user_id})
    if x:
        return True
    return False

async def get_users() -> list[int]:
    x = db1.find()
    x = await x.to_list(length=None)
    return [y['user_id'] for y in x]

async def get_users_count() -> int:
    x = db1.find()
    return len(await x.to_list(length=None))

async def del_user(user_id: int) -> None:
    await db1.delete_one({'user_id': user_id})

async def del_user_2(user_id: int) -> None:
    await db2.delete_one({'user_id': user_id})
