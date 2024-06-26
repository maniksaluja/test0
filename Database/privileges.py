from . import db

db = db.privileges

async def update_privileges(user_id, allow_batch, super_user, my_content, allow_dm):
    await db.update_one({"user_id": user_id}, {"$set": {"privileges": [allow_batch, super_user, my_content, allow_dm]}}, upsert=True)
    
async def get_privileges(user_id):
    x = await db.find_one({"user_id": user_id})
    if x:
        return x["privileges"]
    return [False, False, False, False]