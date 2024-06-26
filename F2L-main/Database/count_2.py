from . import db

db = db.count_2

async def incr_count_2() -> int:
    x = await db.find_one({"count_2": 69})
    if x:
        y = x["actual_count_2"]
        y += 1
    else:
        y = 1
    await db.update_one({"count_2": 69}, {"$set": {"actual_count_2": y}}, upsert=True)
    return y
    
async def get_count_2() -> int:
    x = await db.find_one({"count_2": 69})
    if x:
        return x["actual_count_2"]
    return 0

async def incr_count_2_by(c) -> int:
    x = await db.find_one({"count_2": 69})
    if x:
        y = x["actual_count_2"]
        y += c
    else:
        y = c
    await db.update_one({"count_2": 69}, {"$set": {"actual_count_2": y}}, upsert=True)
    return y

async def reset_count_2():
    await db.delete_one({"count_2": 69})
