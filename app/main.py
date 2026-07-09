from fastapi import FastAPI
from app.api.v1.endpoints.vehicles import router as vehicles_router

from app.database import get_database
from app.services.vehicle_service import VehicleService

app = FastAPI()

@app.on_event("startup")
async def startup():
    database = get_database()

    service = VehicleService(database)

    await service.create_indexes()

app.include_router(vehicles_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}