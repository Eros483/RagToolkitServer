from fastapi import FastAPI
import uvicorn
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()

from routers import rag_router, summarizer_router, evaluator_router, persistent_rag_router, image_router

from services import persistent_index, image_indexing_service
from database import mongodb_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for application startup and shut down events
    """
    print("Application Startup: Attempting to load permanent rag index and loading indices from mongodb")
    await persistent_index.load_permanent_index()

    await persistent_index.load_permanent_index()
    await image_indexing_service.load_and_build_image_index()

    print("Application start up complete.")
    yield
    print("Application Shut Down: Attempting to save permanent rag index and closing mongodb connection")
    await mongodb_client.close_mongodb_connection
    print("Application shut down finished")

app= FastAPI(
    title="AI Solution provided by Critical AI",
    description="A FastAPI backend for RAG chatbot, summarization, and evaluation features.",
    version="3.0.2",
    lifespan=lifespan,
)

app.include_router(rag_router.router)
app.include_router(summarizer_router.router)
app.include_router(evaluator_router.router)
app.include_router(persistent_rag_router.router)
app.include_router(image_router.router)

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint to check if the API is running.
    """
    return {"message": "Welcome to the AI Solution provided by Critical AI!"}

if __name__ == "__main__":
    port=int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)