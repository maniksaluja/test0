from . import db

db = db.auto_delete_2

async def update_2(user_id, dic):
    await db.update_one({'user_id': user_id}, {'$set': {'dic': dic}}, upsert=True)

async def get_2(user_id):
    x = await db.find_one({'user_id': user_id})
    if x:
        return x['dic']
    return {}
    
async def get_all_2() -> list[int]:
    x = db.find()
    x = await x.to_list(length=None)
    return [y['user_id'] for y in x]