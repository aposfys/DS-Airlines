from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://mongodb:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client.dsairlines

async def get_db():
    return db
