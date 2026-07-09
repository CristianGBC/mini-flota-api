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
    
    async def create_vehicle(self, vehicle: VehicleCreate):
        vehicle_data = vehicle.model_dump()
        
        try:
            result = await self.collection.insert_one(vehicle_data)
        except DuplicateKeyError:
            raise ValueError("La placa ya está registrada")
        
        created_vehicle = await self.collection.find_one(
            {"_id": result.inserted_id}
        )
        
        created_vehicle["id"] = str(created_vehicle["_id"])
        del created_vehicle["_id"]
        
        return created_vehicle
    
    async def get_vehicles(self):
        vehicles = []

        cursor = self.collection.find()

        async for vehicle in cursor:
            vehicle["id"] = str(vehicle["_id"])
            del vehicle["_id"]
            vehicles.append(vehicle)

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

        vehicle["id"] = str(vehicle["_id"])
        del vehicle["_id"]

        return vehicle
    
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

        updated_vehicle["id"] = str(updated_vehicle["_id"])
        del updated_vehicle["_id"]

        return updated_vehicle
    
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