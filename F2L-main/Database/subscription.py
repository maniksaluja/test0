from . import db
import time

db = db.subscription

async def active_sub(user_id):
    await db.update_one({"user_id": user_id}, {"$set": {"time": time.time()}}, upsert=True)
    
async def get_all_subs():
    x = db.find()
    x = await x.to_list(length=None)
    return {u["user_id"]: u["time"] for u in x}
    
async def del_sub(user_id):
    x = await db.delete_one({"user_id": user_id})