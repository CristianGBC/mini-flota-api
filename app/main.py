from fastapi import FastAPI
from app.api.v1.endpoints.vehicles import router as vehicles_router
from app.api.v1.endpoints import auth

from contextlib import asynccontextmanager

from app.database import get_database
from app.services.user_service import UserService
from app.services.vehicle_service import VehicleService

@asynccontextmanager
async def lifespan(app: FastAPI):
    database = get_database()

    user_service = UserService(database)
    await user_service.create_seed_user()
    
    vehicle_service = VehicleService(database)
    await vehicle_service.create_indexes()

    yield

app = FastAPI(
    lifespan=lifespan
)

app.include_router(vehicles_router)
app.include_router(auth.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}