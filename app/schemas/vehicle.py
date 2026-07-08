from pydantic import BaseModel, Field, field_validator
import re

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

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str):
        allowed = {"active", "inactive"}

        if value not in allowed:
            raise ValueError("Status must be 'active' or 'inactive'")

        return value