from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List
import os
import shutil

from core.models import SummarizeRequest

from services import summarizer_service

router = APIRouter(
    prefix="/summarizer",
    tags=["Document Summarization"]
)

TEMP_FILES_DIR = "temp_files"
os.makedirs(TEMP_FILES_DIR, exist_ok=True)

@router.post("/summarize_document/", summary="Upload documents to get collated summary")
async def summarize_document(file: UploadFile = File(...), 
                             num_clusters: int = 10,
                             max_tokens: int = 512
):
    """
    Uploads PDF files to be processed and summarized.
    Supported file types: PDF

    Parameters:
    - files: A single file to be summarized, must be a PDF.
    - num_clusters: int - The number of clusters for KMeans clustering, default is 10.
    - max_tokens: int - The maximum number of tokens for the summary, default is 512
    """
    temp_filepath=None
    try:
        file_extension=os.path.splitext(file.filename)[1].lower()
        if file_extension != '.pdf':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are supported.")
        temp_filepath = os.path.join(TEMP_FILES_DIR, file.filename)
        with open(temp_filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        await file.close()
        summary=await summarizer_service.generate_document_summary([temp_filepath], num_clusters, max_tokens)
        return {"summary": summary}
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        if temp_filepath and os.path.exists(temp_filepath):
            try:
                os.remove(temp_filepath)
            except OSError as e: # Catch OSError specifically for cleanup issues
                print(f"Error removing temporary file {temp_filepath}: {e}")
                # You might want to log this error for debugging or send a notification