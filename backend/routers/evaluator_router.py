# routers/evaluator_router.py
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from typing import List, Tuple
import os
import shutil
import json # Ensure json is imported

# Import Pydantic models from the core directory
from core.models import EvaluationRequest

# Import evaluator service functions
from services import evaluator_service

MAX_CHAT_HISTORY_TURNS=5

# Create an APIRouter instance for evaluator-related endpoints
router = APIRouter(
    prefix="/evaluator", # All endpoints in this router will be prefixed with /evaluator
    tags=["Evaluation Assistant"], # Tags for API documentation (Swagger UI)
)

# Define the directory for temporary file storage
TEMP_FILES_DIR = "temp_files"
os.makedirs(TEMP_FILES_DIR, exist_ok=True) # Ensure the directory exists upon startup

@router.post("/upload_eval_files/", summary="Upload context and metrics files for evaluation")
async def upload_eval_files(
    context_file: UploadFile = File(..., description="Upload a single PDF or JSON document for evaluation context."),
    metrics_file: UploadFile = File(..., description="Upload the JSON file containing evaluation metrics.")
):
    """
    **Uploads a context file (PDF/JSON) and a metrics JSON file to be used by the evaluation assistant.**

    - Both files are temporarily saved to `temp_files/`.
    - The context file's text is extracted and used to build the evaluation context FAISS index.
    - The content of the metrics file is loaded and stored in memory for subsequent chat requests.
    - Temporary files are deleted after processing.

    **Supported file types**:
    - `context_file`: `.pdf`, `.json`
    - `metrics_file`: `.json`
    """
    context_filepath = None
    metrics_filepath = None
    try:
        # --- Handle Context File Upload ---
        context_file_extension = os.path.splitext(context_file.filename)[1].lower()
        if context_file_extension not in ['.pdf', '.json']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported context file type: {context_file.filename}. Only .pdf and .json are allowed."
            )
        context_filepath = os.path.join(TEMP_FILES_DIR, context_file.filename)
        with open(context_filepath, "wb") as buffer:
            shutil.copyfileobj(context_file.file, buffer)
        await context_file.close() # Close handle for uploaded context file

        # --- Handle Metrics File Upload ---
        metrics_file_extension = os.path.splitext(metrics_file.filename)[1].lower()
        if metrics_file_extension != '.json':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported metrics file type: {metrics_file.filename}. Only .json is allowed for metrics."
            )
        metrics_filepath = os.path.join(TEMP_FILES_DIR, metrics_file.filename)
        with open(metrics_filepath, "wb") as buffer:
            shutil.copyfileobj(metrics_file.file, buffer)
        await metrics_file.close() # Close handle for uploaded metrics file

        # Process the context file to build its index in the service
        await evaluator_service.process_eval_context_files([context_filepath])
        # Store the content of the metrics file in the service's global state
        await evaluator_service.set_current_metrics_data(metrics_filepath)

        return {"message": "Context and metrics files processed successfully."}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred during file processing: {e}")
    finally:
        # Clean up temporary files regardless of success or failure
        if context_filepath and os.path.exists(context_filepath):
            try:
                os.remove(context_filepath)
            except OSError as e:
                print(f"Error removing context file {context_filepath}: {e}")
        if metrics_filepath and os.path.exists(metrics_filepath):
            try:
                os.remove(metrics_filepath)
            except OSError as e:
                print(f"Error removing metrics file {metrics_filepath}: {e}")

@router.post("/ask_evaluation/", response_model=dict, summary="Ask evaluation assistant for feedback")
async def ask_evaluation(
    request: EvaluationRequest # Now only accepts the JSON request body
):
    """
    Asks the evaluation assistant a question, leveraging previously uploaded context documents
    and the metrics JSON file.
    """
    try:
        # FIX: Parse the history string back into List[Tuple[str, str]]
        parsed_history: List[Tuple[str, str]] = json.loads(request.history)
        if len(parsed_history)>MAX_CHAT_HISTORY_TURNS:
            parsed_history=parsed_history[-MAX_CHAT_HISTORY_TURNS:]

        # Call the evaluator service to get feedback
        feedback = await evaluator_service.get_evaluation_feedback(
            question=request.question,
            history=parsed_history, # Pass the parsed history
            max_tokens=request.max_tokens
        )
        return {"feedback": feedback}

    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON format for 'history' field.")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except FileNotFoundError as e: # Catch specific service errors
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Service error: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred during evaluation: {e}")

