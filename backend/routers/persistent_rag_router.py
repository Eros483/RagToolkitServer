from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List, Dict
import os
import shutil
import traceback

from services import persistent_index

router=APIRouter(
    prefix="/persistent_rag",
    tags=["Persistent Knowledge Base"],
)

TEMP_FILES_DIR_FOR_PERSISTENT_RAG="temp_files_persistent"
os.makedirs(TEMP_FILES_DIR_FOR_PERSISTENT_RAG, exist_ok=True)

@router.post("/upload_and_index/", summary="Upload files to build and update central rag index")
async def upload_and_index_persistent_rag(files: List[UploadFile] = File(...)):
    """
    Accepts pdf, json and txt format files to build or replace central rag index
    """
    temp_filepaths=[]
    try:
        if not files:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files provided")

        for file in files:
            file_extension=os.path.splitext(file.filename)[1].lower()
            if file_extension not in ['.pdf', '.json', '.txt']:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Only pdf, json, txt accepted, passed_file: {file.filename}")
            
            temp_filepath=os.path.join(TEMP_FILES_DIR_FOR_PERSISTENT_RAG, file.filename)
            temp_filepaths.append(temp_filepath)

            with open(temp_filepath, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            await file.close()

        await persistent_index.process_files_to_build_permanent_index(temp_filepaths)

        return {"message": "Files uploaded and indexed successfully"}
    
    except HTTPException as e:
        raise e
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {e}")
    
    finally:
        for temp_filepath in temp_filepaths:
            if os.path.exists(temp_filepath):
                try:   
                    os.remove(temp_filepath)
                except OSError as e:
                    print(f"Error deleting temporary file: {e}")

@router.post("/delete_index/", summary="Delete permanent RAG index from disk and memory")
async def delete_permanent_rag_index():
    """
    Deletes and clears memory of RAG index files
    Use with caution, permanently removes the stored knowledge base
    """
    try:
        await persistent_index.delete_permanent_index()
        return {"message": "Index deleted successfully"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred{e} while deleting permanent index")
    
@router.get("/status/", response_model=Dict[str, str], summary="Get status of permanent index")
async def get_persistent_rag_index_status():
    """
    Returns the status of the permanent RAG index
    """
    try:
        status_info=await persistent_index.get_permanent_index_status()
        return {k: str(v) for k, v in status_info.items()}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred in getting the status {e}")