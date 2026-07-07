from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings

app = FastAPI()

client = AsyncIOMotorClient(settings.mongodb_url)


@app.get("/health")
async def health_check():
    await client.admin.command("ping")
    return {"status": "okey"}