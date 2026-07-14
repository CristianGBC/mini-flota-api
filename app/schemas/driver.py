from pydantic import BaseModel, ConfigDict, field_validator
import re

class DriverCreate(BaseModel):
    name: str
    license: str

    @field_validator("name", "license")
    @classmethod
    def validate_non_empty_fields(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("El campo no puede estar vacío")

        return value


    @field_validator("license")
    @classmethod
    def validate_license(cls, value: str) -> str:
        if not re.fullmatch(r"\d{10}", value):
            raise ValueError(
                "La licencia debe contener exactamente 10 dígitos numéricos"
            )

        return value


class DriverResponse(BaseModel):
    id: str
    name: str
    license: str

    model_config = ConfigDict(
        from_attributes=True,
    )