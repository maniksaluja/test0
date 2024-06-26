from . import db

db = db.sessions

async def update_session(user_id, session):
    await db.update_one({'user_id': user_id}, {'$set': {'session': session}}, upsert=True)

async def get_session(user_id):
    x = await db.find_one({'user_id': user_id}) or {}
    return x.get('session', None)

async def del_session(user_id):
    await db.delete_one({'user_id': user_id})