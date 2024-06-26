from . import db

db = db.count

async def incr_count() -> int:
    x = await db.find_one({"count": 69})
    if x:
        y = x["actual_count"]
        y += 1
    else:
        y = 1
    await db.update_one({"count": 69}, {"$set": {"actual_count": y}}, upsert=True)
    return y
    
async def get_count() -> int:
    x = await db.find_one({"count": 69})
    if x:
        return x["actual_count"]
    return 0

async def incr_count_by(c) -> int:
    x = await db.find_one({"count": 69})
    if x:
        y = x["actual_count"]
        y += c
    else:
        y = c
    await db.update_one({"count": 69}, {"$set": {"actual_count": y}}, upsert=True)
    return y

async def reset_count():
    await db.delete_one({"count": 69})
