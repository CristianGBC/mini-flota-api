from unittest.mock import AsyncMock, MagicMock

import pytest
from bson import ObjectId
from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError

from app.schemas.driver import DriverCreate
from app.services.driver_service import DriverService


class TestDriverService:

    @pytest.mark.asyncio
    async def test_create_driver_returns_created_driver(self):
        driver_id = ObjectId()

        driver_data = {
            "name": "Cristian Ca",
            "license": "1234567898",
        }

        created_driver = {
            "_id": driver_id,
            **driver_data,
        }

        fake_insert_result = MagicMock()
        fake_insert_result.inserted_id = driver_id

        fake_collection = MagicMock()
        fake_collection.insert_one = AsyncMock(
            return_value=fake_insert_result
        )
        fake_collection.find_one = AsyncMock(
            return_value=created_driver.copy()
        )

        fake_database = MagicMock()
        fake_database.__getitem__.return_value = fake_collection

        service = DriverService(fake_database)

        driver = DriverCreate(**driver_data)
        result = await service.create_driver(driver)

        assert result == {
            "id": str(driver_id),
            "name": "Cristian Ca",
            "license": "1234567898",
        }

        fake_collection.insert_one.assert_awaited_once_with(
            driver_data
        )

    @pytest.mark.asyncio
    async def test_create_driver_raises_value_error_when_license_is_duplicated(
        self,
    ):
        fake_collection = MagicMock()
        fake_collection.insert_one = AsyncMock(
            side_effect=DuplicateKeyError(
                "Duplicated license"
            )
        )

        fake_database = MagicMock()
        fake_database.__getitem__.return_value = fake_collection

        service = DriverService(fake_database)

        driver = DriverCreate(
            name="Cristian Ca",
            license="1234567898",
        )

        with pytest.raises(
            ValueError,
            match="La licencia ya está registrada",
        ):
            await service.create_driver(driver)

    @pytest.mark.asyncio
    async def test_get_drivers_returns_serialized_drivers(self):
        first_driver_id = ObjectId()
        second_driver_id = ObjectId()

        driver_documents = [
            {
                "_id": first_driver_id,
                "name": "Cristian Ca",
                "license": "1234567898",
            },
            {
                "_id": second_driver_id,
                "name": "Juan Pérez",
                "license": "0987654321",
            },
        ]

        fake_cursor = MagicMock()
        fake_cursor.__aiter__.return_value = iter(
            [
                driver.copy()
                for driver in driver_documents
            ]
        )

        fake_collection = MagicMock()
        fake_collection.find.return_value = fake_cursor

        fake_database = MagicMock()
        fake_database.__getitem__.return_value = fake_collection

        service = DriverService(fake_database)

        result = await service.get_drivers()

        assert result == [
            {
                "id": str(first_driver_id),
                "name": "Cristian Ca",
                "license": "1234567898",
            },
            {
                "id": str(second_driver_id),
                "name": "Juan Pérez",
                "license": "0987654321",
            },
        ]

    def test_driver_create_rejects_license_with_letters(self):
        with pytest.raises(ValidationError):
            DriverCreate(
                name="Cristian Ca",
                license="ABC4567898",
            )

    def test_driver_create_rejects_license_with_less_than_ten_digits(
        self,
    ):
        with pytest.raises(ValidationError):
            DriverCreate(
                name="Cristian Ca",
                license="12345",
            )

    def test_driver_create_removes_surrounding_spaces(self):
        driver = DriverCreate(
            name="  Cristian Ca  ",
            license=" 1234567898 ",
        )

        assert driver.name == "Cristian Ca"
        assert driver.license == "1234567898"