import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection

from app.utils.logger import logger

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")


class DatabaseConnection:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DatabaseConnection()
        return cls._instance

    def __init__(self):
        if DatabaseConnection._instance is not None:
            raise Exception(
                "🙅‍♀️ The DatabaseConnection class is a singleton 🙅‍♀️ Use get_instance() instead ✅"
            )
        self.client = None
        self.db = None
        self.collections = {}

    def initialize_mongo_client(self):
        """Initialize MongoDB Client"""
        if not self.client:
            try:
                self.client = MongoClient(host=MONGO_URI)
                self.db = self.client[MONGO_DB_NAME]
                logger.info("✅  MongoDB connection established ✅")
                return self.db
            except Exception as e:
                logger.error(f"❌ Failed to initialize MongoDB: {e} ❌")
                raise

    def close_connection(self):
        """Close the MongoDB connection"""
        if self.client:
            try:
                self.client.close()
                logger.info("✅ MongoDB connection closed ✅")
            except Exception as e:
                logger.error(f"❌ Failed to close MongoDB connection: {e} ❌")

    def get_collection(self, collection_name) -> Collection:
        """Get a collection by name"""
        if self.db is None:
            raise Exception(
                "Database not initialized. Call initialize_mongo_client first."
            )

        # Cache collection reference for reuse
        if collection_name not in self.collections:
            self.collections[collection_name] = self.db[collection_name]

        return self.collections[collection_name]