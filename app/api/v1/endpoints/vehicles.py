from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_database
from app.schemas.vehicle import VehicleCreate, VehicleResponse, AssignDriverRequest
from app.services.vehicle_service import VehicleService

from app.core.security import get_current_user

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])

@router.post("/", response_model=VehicleResponse)
async def create_vehicle(
    vehicle: VehicleCreate,
    current_user: str = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database),
):
    service = VehicleService(database)

    try:
        return await service.create_vehicle(vehicle)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    
@router.get("/", response_model=list[VehicleResponse])
async def get_vehicles(
    current_user: str = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database),
):
    service = VehicleService(database)

    return await service.get_vehicles()

@router.get("/{id}", response_model=VehicleResponse)
async def get_vehicle(
    id: str,
    current_user: str = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database),
):
    service = VehicleService(database)

    vehicle = await service.get_vehicle(id)

    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    return vehicle

@router.put("/{id}", response_model=VehicleResponse)
async def update_vehicle(
    id: str,
    vehicle: VehicleCreate,
    current_user: str = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database),
):
    service = VehicleService(database)

    updated_vehicle = await service.update_vehicle(id, vehicle)

    if updated_vehicle is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    return updated_vehicle

@router.delete("/{id}")
async def delete_vehicle(
    id: str,
    current_user: str = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database),
):
    service = VehicleService(database)

    deleted_vehicle = await service.delete_vehicle(id)

    if deleted_vehicle is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    return deleted_vehicle

@router.put("/{vehicle_id}/driver", response_model=VehicleResponse)
async def assign_driver(
    vehicle_id: str,
    assignment: AssignDriverRequest,
    current_user: str = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database),
):
    service = VehicleService(database)

    try:
        return await service.assign_driver(
            vehicle_id,
            assignment.driver_id,
        )
    except LookupError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error