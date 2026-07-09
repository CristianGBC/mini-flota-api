from fastapi import FastAPI
from app.api.v1.endpoints.vehicles import router as vehicles_router
from app.api.v1.endpoints import auth

from contextlib import asynccontextmanager

from app.database import get_database
from app.services.user_service import UserService


@asynccontextmanager
async def lifespan(app: FastAPI):
    database = get_database()

    service = UserService(database)

    await service.create_seed_user()

    yield

app = FastAPI(
    lifespan=lifespan
)

app.include_router(vehicles_router)
app.include_router(auth.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}