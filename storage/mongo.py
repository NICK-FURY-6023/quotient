# storage/mongo.py
from motor.motor_asyncio import AsyncIOMotorClient
from .base import StorageBase

class MongoStorage(StorageBase):
    def __init__(self, db):
        self.collection = db["quotient_data"]

    async def save(self, data: dict):
        await self.collection.insert_one(data)
