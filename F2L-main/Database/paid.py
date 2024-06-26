from . import db

db = db.paid

async def pay(user_id):
    await db.insert_one({'user_id': user_id})

async def unpay(user_id):
    await db.delete_one({'user_id': user_id})

async def is_paid(user_id):
    x = await db.find_one({'user_id': user_id})
    if x:
        return True
    return False
