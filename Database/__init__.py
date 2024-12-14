from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB_URI

# Database connection with maxPoolSize and waitQueueTimeoutMS for better handling of concurrent requests
mongo = AsyncIOMotorClient(
    MONGO_DB_URI,
    maxPoolSize=50,  # Max number of simultaneous connections to MongoDB
    waitQueueTimeoutMS=50000  # Timeout for waiting for a free connection
)
db = mongo.SpL
