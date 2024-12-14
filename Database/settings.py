from . import db

db = db.settings

# purane settings ko touch nahi kiya gaya
# blur ko new settings mein add kiya gaya hai

async def update_settings(dic):
    await db.update_one({'settings': 69}, {'$set': {'actual_settings': dic}}, upsert=True)

async def get_settings():
    x = await db.find_one({'settings': 69})
    if x:
        return x['actual_settings']
    return {
        'auto_approval': False, 
        'join': False, 
        'leave': False, 
        'image': False, 
        'generate': 10, 
        'auto_save': False, 
        'logs': True, 
        'blur_enabled': False,  # Blur setting added
        'blur_auto': False      # Blur Auto setting added
    }
