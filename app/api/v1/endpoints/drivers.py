from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.security import get_current_user
from app.database import get_database
from app.schemas.driver import DriverCreate, DriverResponse
from app.services.driver_service import DriverService


router = APIRouter(
    prefix="/drivers",
    tags=["Drivers"],
)


@router.post(
    "/",
    response_model=DriverResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_driver(
    driver: DriverCreate,
    current_user: str = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database),
):
    service = DriverService(database)

    try:
        return await service.create_driver(driver)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get(
    "/",
    response_model=list[DriverResponse],
)
async def get_drivers(
    current_user: str = Depends(get_current_user),
    database: AsyncIOMotorDatabase = Depends(get_database),
):
    service = DriverService(database)

    return await service.get_drivers()