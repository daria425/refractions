from typing import Dict, List, Any, Optional, Union, Callable
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
    
    def get_data_by_query(self, query: Dict) -> Optional[Dict]:
        """Retrieve a single document matching the query."""
        result = self.collection.find_one(query)
        logger.info(f"Queried document with {query} from collection {self.collection.name}")
        return result


class GeneratedImagesCollection(DatabaseCollection):
    def __init__(self):
        super().__init__("generated_images")

    def get_image_by_request_id(self, request_id: str) -> Optional[Dict]:
        """Retrieve an image document by its request_id."""
        return self.get_data_by_query({"result_data.request_id": request_id})
    
    def update_image_with_variant(self, request_id:str, variant_data:Dict) -> Optional[Dict]:
        """Update an image document by adding a new variant."""
        updated_document = self.collection.find_one_and_update(
            {"result_data.request_id": request_id},
            {"$push": {"variants": variant_data}},
            return_document=ReturnDocument.AFTER
        )
        logger.info(f"Updated document with request_id: {request_id} by adding new variant.")
        return updated_document
    
    def update_image_with_edit(self, request_id:str, edited_image_data: Dict)->Optional[Dict]:
        updated_document = self.collection.find_one_and_update(
            {"result_data.request_id": request_id},
            {"$push": {"edits": edited_image_data}},
            return_document=ReturnDocument.AFTER
        )
        logger.info(f"Updated document with request_id: {request_id} by adding new variant.")
        return updated_document
    

