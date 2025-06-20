from pydantic import BaseModel
from typing import List, Tuple, Optional

class ChatRequest(BaseModel):
    """
    Pydantic model for the chat request.
    Question: The user's current question or message
    History: A list of tuples consisting of questions and answers representing the chat history
    Max_Tokens: The maximum number of tokens to generate in the response
    """
    question: str
    history: List[Tuple[str, str]] = []
    max_tokens: int=512

class SummarizeRequest(BaseModel):
    """
    Pydantic model for the document summarization request.
    num_clusters: The num of clusters for KMeans clustering, default is 10
    max_tokens: The maximum number of tokens to generate in the summary
    """
    num_clusters: int=10
    max_tokens: int = 512

class EvaluationRequest(BaseModel):
    """
    Pydantic model for the evaluation request.
    question: The user's current question or message for evaluation feedback.
    history: A list of (question, answer) tuples for conversation context
    max_tokens: The maximum number of tokens to generate in the response
    """
    question: str
    history: str="[]"
    max_tokens: int = 512

class RAGResponse(BaseModel):
    """
    Pydantic model for the RAG response.
    Includes text and image links
    """
    answer: str
    image_urls: List[str]=[]