from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.security import hash_password

class UserService:

    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database["users"]

    async def create_seed_user(self):
        existing_user = await self.collection.find_one(
            {"email": "admin@miniflota.com"}
        )

        if existing_user:
            return

        user = {
            "email": "admin@miniflota.com",
            "hashed_password": hash_password("Admin123*")
        }

        await self.collection.insert_one(user)