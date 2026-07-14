from unittest.mock import AsyncMock, MagicMock

import pytest
from bson import ObjectId

from app.schemas.vehicle import VehicleCreate
from app.services.vehicle_service import VehicleService
from pymongo.errors import DuplicateKeyError
from pydantic import ValidationError


class TestVehicleService:
    
    #crear un vehiculo

    @pytest.mark.asyncio
    async def test_create_vehicle_returns_created_vehicle(self):
        vehicle_id = ObjectId()

        vehicle_data = {
            "plate": "PDA-1234",
            "brand": "Toyota",
            "model": "Hilux",
            "year": 2024,
            "capacity_kg": 1000.0,
            "status": "active",
        }

        created_vehicle = {
            "_id": vehicle_id,
            **vehicle_data,
        }

        fake_insert_result = MagicMock()
        fake_insert_result.inserted_id = vehicle_id

        fake_collection = MagicMock()
        fake_collection.insert_one = AsyncMock(return_value=fake_insert_result)
        fake_collection.find_one = AsyncMock(return_value=created_vehicle)

        fake_driver_collection = MagicMock() 
        fake_database = {
            "vehicles": fake_collection,
            "drivers": fake_driver_collection
        }

        service = VehicleService(fake_database)

        vehicle = VehicleCreate(**vehicle_data)

        result = await service.create_vehicle(vehicle)

        assert result["id"] == str(vehicle_id)
        assert "_id" not in result
        assert result["plate"] == "PDA-1234"
        assert result["brand"] == "Toyota"

        fake_collection.insert_one.assert_awaited_once_with(vehicle_data)
        fake_collection.find_one.assert_awaited_once_with(
            {"_id": vehicle_id}
        )
        
    #Listar los vehiculos
    
    @pytest.mark.asyncio
    async def test_get_vehicles_returns_vehicle_list(self):
        vehicle_id = ObjectId()

        fake_vehicle = {
            "_id": vehicle_id,
            "plate": "PDA-1234",
            "brand": "Toyota",
            "model": "Hilux",
            "year": 2024,
            "capacity_kg": 1000.0,
            "status": "active",
        }

        class FakeCursor:
            def __aiter__(self):
                async def generator():
                    yield fake_vehicle

                return generator()

        fake_collection = MagicMock()
        fake_collection.find.return_value = FakeCursor()

        fake_driver_collection = MagicMock()
        fake_database = {
            "vehicles": fake_collection,
            "drivers": fake_driver_collection
        }

        service = VehicleService(fake_database)

        result = await service.get_vehicles()

        assert len(result) == 1
        assert result[0]["id"] == str(vehicle_id)
        assert "_id" not in result[0]
        assert result[0]["plate"] == "PDA-1234"

        fake_collection.find.assert_called_once()
    
    #Editar datos de vehiculo
    
    @pytest.mark.asyncio
    async def test_update_vehicle_returns_updated_vehicle(self):
        vehicle_id = ObjectId()

        vehicle_data = {
            "plate": "PDA-1234",
            "brand": "Toyota",
            "model": "Hilux SR",
            "year": 2024,
            "capacity_kg": 1200.0,
            "status": "active",
        }

        updated_vehicle = {
            "_id": vehicle_id,
            **vehicle_data,
        }

        fake_update_result = MagicMock()
        fake_update_result.matched_count = 1

        fake_collection = MagicMock()
        fake_collection.update_one = AsyncMock(
            return_value=fake_update_result
        )
        fake_collection.find_one = AsyncMock(
            return_value=updated_vehicle
        )

        fake_driver_collection = MagicMock()
        fake_database = {
            "vehicles": fake_collection,
            "drivers": fake_driver_collection
        }

        service = VehicleService(fake_database)

        vehicle = VehicleCreate(**vehicle_data)

        result = await service.update_vehicle(
            str(vehicle_id),
            vehicle
        )

        assert result["id"] == str(vehicle_id)
        assert "_id" not in result
        assert result["model"] == "Hilux SR"
        assert result["capacity_kg"] == 1200.0

        fake_collection.update_one.assert_awaited_once_with(
            {"_id": vehicle_id},
            {"$set": vehicle_data},
        )

        fake_collection.find_one.assert_awaited_once_with(
            {"_id": vehicle_id}
        )
    
    #verificar placa duplicada
    
    @pytest.mark.asyncio
    async def test_create_vehicle_raises_value_error_when_plate_is_duplicated(self):
        vehicle_data = {
            "plate": "PDA-1234",
            "brand": "Toyota",
            "model": "Hilux",
            "year": 2024,
            "capacity_kg": 1000.0,
            "status": "active",
        }

        fake_collection = MagicMock()
        fake_collection.insert_one = AsyncMock(
            side_effect=DuplicateKeyError("Duplicate key")
        )

        fake_driver_collection = MagicMock()
        fake_database = {
            "vehicles": fake_collection,
            "drivers": fake_driver_collection
        }

        service = VehicleService(fake_database)

        vehicle = VehicleCreate(**vehicle_data)

        with pytest.raises(ValueError, match="La placa ya está registrada"):
            await service.create_vehicle(vehicle)
    
    #Verificar placa mal formada
    
    def test_vehicle_create_raises_validation_error_for_invalid_plate(self):
        vehicle_data = {
            "plate": "PDA1234",
            "brand": "Toyota",
            "model": "Hilux",
            "year": 2024,
            "capacity_kg": 1000.0,
            "status": "active",
        }

        with pytest.raises(ValidationError):
            VehicleCreate(**vehicle_data)
            
    #Verificar año inválido
    
    def test_vehicle_create_raises_validation_error_for_future_year(self):
        vehicle_data = {
            "plate": "PDA-1234",
            "brand": "Toyota",
            "model": "Hilux",
            "year": 3000,
            "capacity_kg": 1000.0,
            "status": "active",
        }

        with pytest.raises(ValidationError):
            VehicleCreate(**vehicle_data)
            
    #Asignación correcta
    
    @pytest.mark.asyncio
    async def test_assign_driver_returns_vehicle_with_driver(self):
        vehicle_id = ObjectId()
        driver_id = ObjectId()

        vehicle_document = {
            "_id": vehicle_id,
            "plate": "PDA-1234",
            "brand": "Toyota",
            "model": "Hilux",
            "year": 2024,
            "capacity_kg": 1000.0,
            "status": "active",
        }

        updated_vehicle = {
            **vehicle_document,
            "driver_id": driver_id,
        }

        driver_document = {
            "_id": driver_id,
            "name": "Cristian Ca",
            "license": "1234567898",
        }

        fake_vehicle_collection = MagicMock()
        fake_vehicle_collection.find_one = AsyncMock(
            side_effect=[
                vehicle_document,
                None,
                updated_vehicle,
            ]
        )
        fake_vehicle_collection.update_one = AsyncMock()

        fake_driver_collection = MagicMock()
        fake_driver_collection.find_one = AsyncMock(
            side_effect=[
                driver_document,
                driver_document,
            ]
        )

        fake_database = MagicMock()

        def get_collection(collection_name: str):
            if collection_name == "vehicles":
                return fake_vehicle_collection

            if collection_name == "drivers":
                return fake_driver_collection

            raise KeyError(collection_name)

        fake_database.__getitem__.side_effect = get_collection

        service = VehicleService(fake_database)

        result = await service.assign_driver(
            str(vehicle_id),
            str(driver_id),
        )

        assert result["id"] == str(vehicle_id)
        assert result["driver"] == {
            "id": str(driver_id),
            "name": "Cristian Ca",
            "license": "1234567898",
        }

        fake_vehicle_collection.update_one.assert_awaited_once_with(
            {"_id": vehicle_id},
            {
                "$set": {
                    "driver_id": driver_id,
                }
            },
        )
    
    #Conductor asignado a otro vehículo
    
    @pytest.mark.asyncio
    async def test_assign_driver_raises_value_error_when_driver_is_already_assigned(
        self,
    ):
        vehicle_id = ObjectId()
        other_vehicle_id = ObjectId()
        driver_id = ObjectId()

        vehicle_document = {
            "_id": vehicle_id,
        }

        driver_document = {
            "_id": driver_id,
            "name": "Cristian Ca",
            "license": "1234567898",
        }

        assigned_vehicle = {
            "_id": other_vehicle_id,
            "driver_id": driver_id,
        }

        fake_vehicle_collection = MagicMock()
        fake_vehicle_collection.find_one = AsyncMock(
            side_effect=[
                vehicle_document,
                assigned_vehicle,
            ]
        )
        fake_vehicle_collection.update_one = AsyncMock()

        fake_driver_collection = MagicMock()
        fake_driver_collection.find_one = AsyncMock(
            return_value=driver_document
        )

        fake_database = MagicMock()

        def get_collection(collection_name: str):
            if collection_name == "vehicles":
                return fake_vehicle_collection

            if collection_name == "drivers":
                return fake_driver_collection

            raise KeyError(collection_name)

        fake_database.__getitem__.side_effect = get_collection

        service = VehicleService(fake_database)

        with pytest.raises(
            ValueError,
            match="El conductor ya está asignado a otro vehículo",
        ):
            await service.assign_driver(
                str(vehicle_id),
                str(driver_id),
            )

        fake_vehicle_collection.update_one.assert_not_awaited()
        
    #Vehículo inexistente
    
    @pytest.mark.asyncio
    async def test_assign_driver_raises_lookup_error_when_vehicle_does_not_exist(
        self,
    ):
        vehicle_id = ObjectId()
        driver_id = ObjectId()

        fake_vehicle_collection = MagicMock()
        fake_vehicle_collection.find_one = AsyncMock(
            return_value=None
        )

        fake_driver_collection = MagicMock()

        fake_database = MagicMock()

        def get_collection(collection_name: str):
            if collection_name == "vehicles":
                return fake_vehicle_collection

            if collection_name == "drivers":
                return fake_driver_collection

            raise KeyError(collection_name)

        fake_database.__getitem__.side_effect = get_collection

        service = VehicleService(fake_database)

        with pytest.raises(
            LookupError,
            match="Vehículo no encontrado",
        ):
            await service.assign_driver(
                str(vehicle_id),
                str(driver_id),
            )
    
    #Conductor inexistente
    
    @pytest.mark.asyncio
    async def test_assign_driver_raises_lookup_error_when_driver_does_not_exist(
        self,
    ):
        vehicle_id = ObjectId()
        driver_id = ObjectId()

        vehicle_document = {
            "_id": vehicle_id,
        }

        fake_vehicle_collection = MagicMock()
        fake_vehicle_collection.find_one = AsyncMock(
            return_value=vehicle_document
        )

        fake_driver_collection = MagicMock()
        fake_driver_collection.find_one = AsyncMock(
            return_value=None
        )

        fake_database = MagicMock()

        def get_collection(collection_name: str):
            if collection_name == "vehicles":
                return fake_vehicle_collection

            if collection_name == "drivers":
                return fake_driver_collection

            raise KeyError(collection_name)

        fake_database.__getitem__.side_effect = get_collection

        service = VehicleService(fake_database)

        with pytest.raises(
            LookupError,
            match="Conductor no encontrado",
        ):
            await service.assign_driver(
                str(vehicle_id),
                str(driver_id),
            )
    
    #Identificador inválido
    
    @pytest.mark.asyncio
    async def test_assign_driver_raises_value_error_when_vehicle_id_is_invalid(
        self,
    ):
        fake_database = MagicMock()

        service = VehicleService(fake_database)

        with pytest.raises(
            ValueError,
            match="El id del vehículo no es válido",
        ):
            await service.assign_driver(
                "invalid-id",
                str(ObjectId()),
            )