from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.vehicle import VehicleCreate

from bson import ObjectId
from bson.errors import InvalidId

from pymongo.errors import DuplicateKeyError

def _to_object_id(vehicle_id: str) -> ObjectId | None:
    try:
        return ObjectId(vehicle_id)
    except InvalidId:
        return None

class VehicleService:
    
    async def create_indexes(self):
        await self.collection.create_index("plate", unique=True)

    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database["vehicles"]
        self.driver_collection = database["drivers"]
    
    async def create_vehicle(self, vehicle: VehicleCreate):
        vehicle_data = vehicle.model_dump()
        
        try:
            result = await self.collection.insert_one(vehicle_data)
        except DuplicateKeyError:
            raise ValueError("La placa ya está registrada")
        
        created_vehicle = await self.collection.find_one(
            {"_id": result.inserted_id}
        )
        
        if created_vehicle is None:
            raise RuntimeError(
                "No se pudo recuperar el vehículo creado",
            )

        return await self._serialize_vehicle(
            created_vehicle,
        )
    
    async def get_vehicles(self):
        vehicles = []

        cursor = self.collection.find()

        async for vehicle in cursor:
            serialized_vehicle = await self._serialize_vehicle(
                vehicle,
            )

            vehicles.append(serialized_vehicle)

        return vehicles
    
    async def get_vehicle(self, vehicle_id: str):
        object_id = _to_object_id(vehicle_id)

        if object_id is None:
            return None

        vehicle = await self.collection.find_one(
            {"_id": object_id}
        )

        if vehicle is None:
            return None

        return await self._serialize_vehicle(vehicle)
    
    async def update_vehicle(self, vehicle_id: str, vehicle: VehicleCreate):
        object_id = _to_object_id(vehicle_id)

        if object_id is None:
            return None

        vehicle_data = vehicle.model_dump()

        result = await self.collection.update_one(
            {"_id": object_id},
            {"$set": vehicle_data}
        )

        if result.matched_count == 0:
            return None

        updated_vehicle = await self.collection.find_one(
            {"_id": object_id}
        )

        if updated_vehicle is None:
            return None

        return await self._serialize_vehicle(updated_vehicle)
    
    async def delete_vehicle(self, vehicle_id: str):
        object_id = _to_object_id(vehicle_id)

        if object_id is None:
            return None

        result = await self.collection.delete_one(
            {"_id": object_id}
        )

        if result.deleted_count == 0:
            return None

        return {
            "message": "Vehicle deleted successfully"
        }
        
    async def _get_driver_data(self, driver_id: ObjectId | None) -> dict | None:
        if driver_id is None:
            return None

        driver = await self.driver_collection.find_one(
            {
                "_id": driver_id,
            },
        )

        if driver is None:
            return None

        return {
            "id": str(driver["_id"]),
            "name": driver["name"],
            "license": driver["license"],
        }
    
    async def _serialize_vehicle(self,vehicle: dict) -> dict:
        driver = await self._get_driver_data(
            vehicle.get("driver_id"),
        )

        return {
            "id": str(vehicle["_id"]),
            "plate": vehicle["plate"],
            "brand": vehicle["brand"],
            "model": vehicle["model"],
            "year": vehicle["year"],
            "capacity_kg": vehicle["capacity_kg"],
            "status": vehicle["status"],
            "driver": driver,
        }
    
    async def assign_driver(self, vehicle_id: str, driver_id: str):
        vehicle_object_id = _to_object_id(vehicle_id)
        driver_object_id = _to_object_id(driver_id)

        if vehicle_object_id is None:
            raise ValueError("El id del vehículo no es válido")

        if driver_object_id is None:
            raise ValueError("El id del conductor no es válido")

        vehicle = await self.collection.find_one(
            {"_id": vehicle_object_id}
        )

        if vehicle is None:
            raise LookupError("Vehículo no encontrado")

        driver = await self.driver_collection.find_one(
            {"_id": driver_object_id}
        )

        if driver is None:
            raise LookupError("Conductor no encontrado")

        assigned_vehicle = await self.collection.find_one(
            {
                "driver_id": driver_object_id,
                "_id": {"$ne": vehicle_object_id},
            }
        )

        if assigned_vehicle is not None:
            raise ValueError(
                "El conductor ya está asignado a otro vehículo"
            )

        await self.collection.update_one(
            {"_id": vehicle_object_id},
            {
                "$set": {
                    "driver_id": driver_object_id,
                }
            },
        )

        updated_vehicle = await self.collection.find_one(
            {"_id": vehicle_object_id}
        )

        if updated_vehicle is None:
            raise RuntimeError(
                "No se pudo recuperar el vehículo actualizado"
            )

        return await self._serialize_vehicle(updated_vehicle)