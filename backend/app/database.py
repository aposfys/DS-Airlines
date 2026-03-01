from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

# Use "MONGO_URL" to match .env or docker-compose, fallback to "mongodb://localhost:27017"
# This allows local execution (e.g. uvicorn main:app) without errors when the db container is mapped to localhost.
MONGO_URL = os.environ.get("MONGO_URL", os.environ.get("MONGODB_URL", "mongodb://localhost:27017"))
DB_NAME = os.environ.get("DB_NAME", "dsairlines")

# Create client
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

async def get_db():
    return db
