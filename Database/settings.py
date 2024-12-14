from . import db

db = db.settings

async def update_settings(dic):
    """Update the settings in the database."""
    await db.update_one({'settings': 69}, {'$set': {'actual_settings': dic}}, upsert=True)

async def get_settings():
    """Retrieve settings from the database."""
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
        'blur_mode': 'off',   # New: Blur mode options (off/manual/auto)
        'auto_blur': False    # New: Auto blur setting for 12-hour delay
    }
