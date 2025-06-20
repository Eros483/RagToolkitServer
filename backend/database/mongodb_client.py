from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI=os.getenv("MONGO_URI")
DB_NAME=os.getenv("MONGO_DB_NAME")
COLLECTION_NAME=os.getenv("MONGO_COLLECTION_NAME")

_mongo_client: Optional[MongoClient] = None
_mongo_db: Optional[MongoClient] = None

async def connect_to_mongodb():
    '''
    Connects to mongodb and sets global client and db objects
    '''
    global _mongo_client, _mongo_db
    if _mongo_client is None:
        try:
            _mongo_client = MongoClient(MONGO_URI)
            _mongo_client.admin.command('ismaster')
            _mongo_db = _mongo_client[DB_NAME]
            print(f"Connected to MongoDB: {MONGO_URI}")
        except (ConnectionFailure, OperationFailure) as e:
            print(f"Error connecting to MongoDB: {e}")
            _mongo_client=None
            _mongo_db=None
            raise ConnectionFailure(f"Couldnt connect to mongoDB, ensure it is running")
        
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            _mongo_client=None
            _mongo_db=None
            raise Exception(f"Failed to connect to mongoDB {e}")
        
async def close_mongodb_connection():
    '''
    Closes the MongoDB connection
    '''
    global _mongo_client, _mongo_db
    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client=None
        _mongo_db=None
        print("Connection closed")

def get_image_collection()->Any:
    '''
    Returns the image collection
    Ensures connection is estabilished first
    '''
    global _mongo_db
    if _mongo_db is None:
        raise RuntimeError("Mongo db connection not estabilished")
    return _mongo_db[COLLECTION_NAME]

async def get_all_image_metadata()->List[Dict[str, Any]]:
    '''
    Returns all image metadata from the database
    Returns a list of dictionaries, each representing an image document.
    '''
    try:
        collection = get_image_collection()
        all_images=list(collection.find({}))
        print(f"Retrived {len(all_images)} images from database")
        return all_images
    except OperationFailure as e:
        print(f"Error retrieving images from database: {e}")
        return []
    except Exception as e:
        print(f"Error retrieving images from database: {e}")
        return []
    
async def get_image_details_by_name(image_name: str)->Optional[Dict[str, Any]]:
    '''
    Retrieves image details from the database by image name
    Returns a dictionary representing the image document, or None if not found
    '''
    try:
        collection = get_image_collection()
        image_details = collection.find_one({"image_name": image_name})
        return image_details
    except Exception as e:
        print(f"Error retrieving image details from database: {e}")
        return None