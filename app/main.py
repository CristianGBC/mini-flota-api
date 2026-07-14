from fastapi import FastAPI
from app.api.v1.endpoints.vehicles import router as vehicles_router
from app.api.v1.endpoints import auth
from app.api.v1.endpoints import drivers

from contextlib import asynccontextmanager

from app.database import get_database
from app.services.user_service import UserService
from app.services.vehicle_service import VehicleService
from app.services.driver_service import DriverService
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    database = get_database()

    user_service = UserService(database)
    await user_service.create_seed_user()
    
    vehicle_service = VehicleService(database)
    await vehicle_service.create_indexes()
    
    driver_service = DriverService(database)
    await driver_service.create_indexes()

    yield

app = FastAPI(
    lifespan=lifespan
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vehicles_router)
app.include_router(auth.router)
app.include_router(drivers.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}