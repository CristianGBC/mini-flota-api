from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.vehicle import VehicleCreate

from bson import ObjectId

class VehicleService:

    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database["vehicles"]
    
    async def create_vehicle(self, vehicle: VehicleCreate):
        vehicle_data = vehicle.model_dump()
        
        result = await self.collection.insert_one(vehicle_data)
        
        created_vehicle = await self.collection.find_one(
            {"_id": result.inserted_id}
        )
        
        created_vehicle["_id"] = str(created_vehicle["_id"])
        
        return created_vehicle
    
    async def get_vehicles(self):
        vehicles = []

        cursor = self.collection.find()

        async for vehicle in cursor:
            vehicle["_id"] = str(vehicle["_id"])
            vehicles.append(vehicle)

        return vehicles
    
    async def get_vehicle(self, vehicle_id: str):
        vehicle = await self.collection.find_one(
            {"_id": ObjectId(vehicle_id)}
        )

        if vehicle is None:
            return None

        vehicle["_id"] = str(vehicle["_id"])

        return vehicle
    
    async def update_vehicle(self, vehicle_id: str, vehicle: VehicleCreate):
        vehicle_data = vehicle.model_dump()

        result = await self.collection.update_one(
            {"_id": ObjectId(vehicle_id)},
            {"$set": vehicle_data}
        )

        if result.matched_count == 0:
            return None

        updated_vehicle = await self.collection.find_one(
            {"_id": ObjectId(vehicle_id)}
        )

        updated_vehicle["_id"] = str(updated_vehicle["_id"])

        return updated_vehicle
    
    async def delete_vehicle(self, vehicle_id: str):
        result = await self.collection.delete_one(
            {"_id": ObjectId(vehicle_id)}
        )

        if result.deleted_count == 0:
            return None

        return {
            "message": "Vehicle deleted successfully"
        }