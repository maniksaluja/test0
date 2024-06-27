from . import db

db = db.settings

# dic = {'auto_approval': False, 'join': False, 'leave': False, 'image': False}

async def update_settings(dic):
    await db.update_one({'settings': 69}, {'$set': {'actual_settings': dic}}, upsert=True)

async def get_settings():
    x = await db.find_one({'settings': 69})
    if x:
        return x['actual_settings']
    return {'auto_approval': False, 'join': False, 'leave': False, 'image': False, 'generate': 20, 'auto_save': False, 'logs': False}
