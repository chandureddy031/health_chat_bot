from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
from backend.logger import get_logger

logger = get_logger("Database")

class Database:
    _db = None

    @classmethod
    def get_db(cls):
        if cls._db is None:
            try:
                uri = os.getenv("MONGO_URI")
                logger.info("Connecting to MongoDB")

                client = MongoClient(uri, server_api=ServerApi("1"))
                client.admin.command("ping")

                cls._db = client[os.getenv("MONGO_DB_NAME")]
                logger.info("MongoDB connection successful")

            except Exception as e:
                logger.error(f"MongoDB connection failed: {e}")
                raise

        return cls._db