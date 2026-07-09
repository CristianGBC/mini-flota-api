from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_database
from app.schemas.vehicle import VehicleCreate
from app.services.vehicle_service import VehicleService

from app.core.security import get_current_user

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])

@router.post("/")
async def create_vehicle(
    vehicle: VehicleCreate,
    current_user: str = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database),
):
    service = VehicleService(database)

    return await service.create_vehicle(vehicle)
    
@router.get("/")
async def get_vehicles(
    current_user: str = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database),
):
    service = VehicleService(database)

    return await service.get_vehicles()

@router.get("/{id}")
async def get_vehicle(
    id: str,
    current_user: str = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database),
):
    service = VehicleService(database)

    return await service.get_vehicle(id)

@router.put("/{id}")
async def update_vehicle(
    id: str,
    vehicle: VehicleCreate,
    current_user: str = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database),
):
    service = VehicleService(database)

    return await service.update_vehicle(id, vehicle)

@router.delete("/{id}")
async def delete_vehicle(
    id: str,
    current_user: str = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database),
):
    service = VehicleService(database)

    return await service.delete_vehicle(id)