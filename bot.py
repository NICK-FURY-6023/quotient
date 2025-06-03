# bot.py
import asyncio
import logging
from config import MONGODB, DISCORD_TOKEN

from motor.motor_asyncio import AsyncIOMotorClient
from storage.mongo import MongoStorage
from storage.json_file import JSONFileStorage
from core import bot  # Your bot instance

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    try:
        mongo_client = AsyncIOMotorClient(MONGODB, serverSelectionTimeoutMS=2000)
        await mongo_client.server_info()  # Force connection on startup
        bot.storage = MongoStorage(mongo_client)
        logger.info("✅ Connected to MongoDB")
    except Exception as e:
        logger.warning(f"❌ MongoDB connection failed, using JSON fallback. Error: {e}")
        bot.storage = JSONFileStorage("data.json")

    await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
