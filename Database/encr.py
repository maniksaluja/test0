from . import db

db = db.encr

async def update(encr, e):
    try:
        await db.update_one({"encr": encr}, {"$set": {"e": e}}, upsert=True)
    except Exception as ex:
        print(f"Error while updating encryption data: {ex}")

async def get_encr(encr):
    try:
        x = await db.find_one({"encr": encr})
        if x:
            return x["e"]
        return None  # Return None if no data found
    except Exception as ex:
        print(f"Error while retrieving encryption data: {ex}")
        return None
