# routers/image_router.py
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
import os
import mimetypes
from typing import Optional

# Import the MongoDB client to get image paths
from database import mongodb_client

router = APIRouter(
    prefix="/images",
    tags=["Image Serving"]
)

@router.get("/{image_name}", summary="Serve image files by name")
async def get_image(image_name: str):
    """
    **Serves an image file from the local file system based on its name.**
    
    This endpoint retrieves the image path from MongoDB and then streams the file content.
    
    **Parameters**:
    - `image_name` (str): The full name of the image file (e.g., "drone.png", "submarine.jpg").
    
    **Returns**:
    - `FileResponse`: The image file streamed as an HTTP response.
    - `HTTPException`: If the image is not found in the database, the file does not exist,
                       or the image path is invalid.
    """
    # 1. Get image details from MongoDB
    image_doc = await mongodb_client.get_image_details_by_name(image_name)

    if not image_doc:
        print(f"DEBUG: Image '{image_name}' not found in MongoDB.") # Debug print
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Image '{image_name}' not found in database.")

    image_path = image_doc.get("image_path")
    if not image_path:
        print(f"DEBUG: Image path missing for '{image_name}' in database record.") # Debug print
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Image path not found for '{image_name}' in database.")
    
    # Sanitize the path to prevent directory traversal attacks
    # For demonstration, we assume image_path from DB is absolute and trusted for local FS
    # In production, use os.path.normpath and strict base directory checks
    
    # Add a debug print to see the exact path FastAPI is trying to open
    print(f"DEBUG: Attempting to serve image from path: '{image_path}'")

    if not os.path.isabs(image_path):
        print(f"WARNING: Image path '{image_path}' is not absolute. This might cause issues.") # Debug print
        # In a real application, you'd prepend a base directory here if paths are relative
        # Example: base_image_dir = "/path/to/your/images"
        # image_path = os.path.join(base_image_dir, image_path)
        
    # Ensure path exists and is a file
    if not os.path.exists(image_path) or not os.path.isfile(image_path):
        print(f"DEBUG: File does not exist or is not a file at path: '{image_path}'") # Debug print
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Image file not found on server at '{image_path}'.")

    # Determine MIME type for the response
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        mime_type = "application/octet-stream" # Default if MIME type cannot be guessed

    # Return the file as a FastAPI FileResponse
    return FileResponse(path=image_path, media_type=mime_type)

