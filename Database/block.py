from . import db
from config import BOT_TOKEN

db = db[f"block_{BOT_TOKEN.split(':')[0]}"]

async def block(user_id):
    await db.insert_one({'user_id': user_id})

async def unblock(user_id):
    await db.delete_one({'user_id': user_id})

async def is_blocked(user_id):
    x = await db.find_one({'user_id': user_id})
    if x:
        return True
    return False
