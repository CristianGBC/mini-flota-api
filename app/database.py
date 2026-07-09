from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings

client = AsyncIOMotorClient(settings.mongodb_url)

database = client[settings.database_name]

def get_database():
    return database