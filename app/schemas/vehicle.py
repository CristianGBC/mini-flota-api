from pydantic import BaseModel, Field, field_validator
import re
from datetime import datetime
from app.schemas.driver import DriverResponse
from typing import Literal
from fastapi import Query

class VehicleCreate(BaseModel):
    plate: str = Field(min_length=8, max_length=8)
    brand: str = Field(min_length=2, max_length=50)
    model: str = Field(min_length=1, max_length=50)
    year: int = Field(ge=1990)
    capacity_kg: float = Field(gt=0)
    status: str
    
    @field_validator("plate")
    @classmethod
    def validate_plate(cls, value: str):
        pattern = r"^[A-Z]{3}-\d{4}$"

        if not re.match(pattern, value):
            raise ValueError("Plate must have the format ABC-1234")

        return value
    
    @field_validator("year")
    @classmethod
    def validate_year(cls, value: int):
        current = datetime.now().year

        if not (1990 <= value <= current):
            raise ValueError(
                f"El año debe estar entre 1990 y {current}"
            )

        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str):
        allowed = {"active", "inactive"}

        if value not in allowed:
            raise ValueError("Status must be 'active' or 'inactive'")

        return value

class AssignDriverRequest(BaseModel):
    driver_id: str

class VehicleResponse(BaseModel):
    id: str
    plate: str
    brand: str
    model: str
    year: int
    capacity_kg: float
    status: str
    driver: DriverResponse | None = None
    
class VehicleQueryParams(BaseModel):
    page: int = Query(default=1, ge=1)
    page_size: int = Query(default=20, ge=1, le=100)
    status: Literal["active", "inactive"] | None = Query(default=None)
    search: str | None = Query(default=None)
    sort_by: Literal[
        "plate",
        "brand",
        "model",
        "year",
        "capacity_kg",
        "status",
    ] = Query(default="plate")
    order: Literal["asc", "desc"] = Query(default="asc")

class PaginatedVehicleResponse(BaseModel):
    items: list[VehicleResponse]
    total: int
    page: int
    page_size: int
    total_pages: int