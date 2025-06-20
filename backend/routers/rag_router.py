from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, HTTPException, status
from typing import List
import os
import shutil

from core.models import ChatRequest, RAGResponse

from services import rag_service

router=APIRouter(
    prefix="/rag",
    tags=["RAG Chatbot"]
)

TEMP_FILES_DIR = "temp_files"
os.makedirs(TEMP_FILES_DIR, exist_ok=True)

MAX_CHAT_HISTORY_TURNS=5

@router.post("/upload_files/", summary="Upload files for RAG processing")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Uploads PDF files to be processed and indexed for rag system.
    Saved as temporary files, later deleted after processing.
    Supported file types: PDF
    """
    temp_filepaths=[]
    try:
        for file in files:
            if not file.filename.endswith('.pdf'):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are supported.")
            
            temp_filepath = os.path.join(TEMP_FILES_DIR, file.filename)
            temp_filepaths.append(temp_filepath)

            with open(temp_filepath, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        
        await rag_service.process_files_for_rag(temp_filepaths)
        return {"message": "Files uploaded and processed successfully."}
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        for filepath in temp_filepaths:
            if os.path.exists(filepath):
                os.remove(filepath)

@router.post("/chat/", response_model=RAGResponse,summary="Chat with the RAG system")
async def chat_with_rag(chat_request: ChatRequest):
    """
    Sends a chat request to the RAG system and returns the response.
    -Requires documents to be uploaded first, and indexed
    
    Request Body:
    - question: str - The question to ask the RAG system.
    - history: List[Tuple[str, str]] - The chat history as a list of tuples (question, answer).
    - max_tokens: int - The maximum number of tokens to generate in the response.
    """
    try:
        if len(chat_request.history)>MAX_CHAT_HISTORY_TURNS:
            chat_request.history=chat_request.history[-MAX_CHAT_HISTORY_TURNS:]
            print(f"RAG Chat - History truncated to {len(chat_request.history)} turns.")

        print(f"RAG Chat - Final history content sent to service: {chat_request.history}")

        response_data=await rag_service.ask_model(
            question=chat_request.question,
            history=chat_request.history,
            max_tokens=chat_request.max_tokens
        )
        return response_data
    
    except ValueError as e:
        print(f"ValueError in RAG Chat endpoint: {e}") # Debug print
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Unexpected error in RAG Chat endpoint: {e}") # Debug print
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))