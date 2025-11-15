from typing import Dict, List, Any, Optional, Union
from pymongo import ReturnDocument
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from app.utils.logger import logger
from app.db.db_connection import DatabaseConnection



class DatabaseCollection:
    """
    A class to handle MongoDB collections.
    Provides methods to interact with a specific MongoDB collection.
    """

    def __init__(self, collection_name):
        db_connection = DatabaseConnection.get_instance()
        self.collection = db_connection.get_collection(collection_name)

    def insert_data(self, data: Dict) -> ObjectId:
        """Insert a document into the collection."""
        data["timestamp"] = datetime.now(timezone.utc)
        result = self.collection.insert_one(data)
        logger.info(f"Inserted document with ID: {result.inserted_id} into collection {self.collection.name}")
        return result.inserted_id


class ImagesCollection(DatabaseCollection):
    def __init__(self):
        super().__init__("images")

