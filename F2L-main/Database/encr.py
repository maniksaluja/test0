from . import db

db = db.encr

async def update(encr, e):
    await db.update_one({"encr": encr}, {"$set": {"e": e}}, upsert=True)
    
async def get_encr(encr):
    x = await db.find_one({"encr": encr})
    if x:
        return x["e"]