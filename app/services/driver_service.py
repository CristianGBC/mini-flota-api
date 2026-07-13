from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from app.schemas.driver import DriverCreate


class DriverService:

    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database["drivers"]

    async def create_indexes(self) -> None:
        await self.collection.create_index(
            "license",
            unique=True,
        )

    async def create_driver(self, driver: DriverCreate) -> dict[str, Any]:
        driver_data = driver.model_dump()

        try:
            result = await self.collection.insert_one(driver_data)
        except DuplicateKeyError as error:
            raise ValueError(
                "La licencia ya está registrada"
            ) from error

        created_driver = await self.collection.find_one(
            {"_id": result.inserted_id}
        )

        if created_driver is None:
            raise RuntimeError(
                "No se pudo recuperar el conductor creado"
            )

        created_driver["id"] = str(created_driver["_id"])
        del created_driver["_id"]

        return created_driver

    async def get_drivers(self) -> list[dict[str, Any]]:
        drivers = []

        cursor = self.collection.find()

        async for driver in cursor:
            driver["id"] = str(driver["_id"])
            del driver["_id"]
            drivers.append(driver)

        return drivers