# services/evaluator_service.py
import pymupdf
import json
import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List, Dict, Tuple, Optional

# Import the actual LLM model from the models directory
from models.llm_model import llm_model

# Global variables for the RAG-like component within the evaluator
# These will store the index for evaluation context documents
_eval_context_index: Optional[faiss.IndexFlatL2] = None
_eval_context_id_to_text: Dict[int, str] = {}
_embedder = SentenceTransformer('all-MiniLM-L6-v2')

# NEW: Global variable to store the loaded metrics data
_current_metrics_data: Optional[Dict] = None

def _extract_json_information(filepath: str) -> dict:
    """
    Extracts information from a JSON file.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Metrics JSON file not found at: {filepath}")
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data

def _split_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Splits text into chunks with a specified overlap.
    """
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks

def _embed_text(text: str) -> Tuple[List[str], np.ndarray]:
    """
    Embeds text using the sentence transformer model.
    Returns chunks and their corresponding embeddings.
    """
    chunks = _split_into_chunks(text)
    vectors = _embedder.encode(chunks)
    return chunks, vectors

def _extract_text_from_pdf(filepath: str) -> str:
    """
    Extracts text from a PDF file using PyMuPDF.
    """
    doc = pymupdf.open(filepath)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return full_text

def _create_faiss_index_for_eval_context(vectors: np.ndarray, chunks: List[str]):
    """
    Creates and populates a FAISS index for evaluation context documents.
    """
    global _eval_context_index
    global _eval_context_id_to_text
    dimension = vectors.shape[1]
    _eval_context_index = faiss.IndexFlatL2(dimension)
    _eval_context_index.reset()
    _eval_context_index.add(np.array(vectors).astype('float32'))
    _eval_context_id_to_text = {i: text for i, text in enumerate(chunks)}

def _search_eval_context_chunks(query: str, top_k: int = 3) -> List[str]:
    """
    Searches the evaluation context FAISS index for the top_k most similar chunks to the query.
    """
    if _eval_context_index is None:
        raise ValueError("Evaluation context index has not been created. Please upload evaluation context documents first.")
    query_vec = _embedder.encode([query]).astype('float32')
    D, I = _eval_context_index.search(query_vec, k=top_k)
    return [_eval_context_id_to_text[i] for i in I[0]]

async def process_eval_context_files(filepaths: List[str]) -> None:
    """
    Public function to process evaluation context documents for text extraction and embedding,
    then creates the FAISS index. This is called by the new upload endpoint.
    """
    all_chunks = []
    all_vectors = []
    for path in filepaths:
        text = ""
        if path.lower().endswith('.pdf'):
            text = _extract_text_from_pdf(path)
        elif path.lower().endswith('.json'):
            with open(path, 'r') as f:
                text = f.read()
        else:
            continue # Skip unsupported file types

        if text:
            chunks, vectors = _embed_text(text)
            all_chunks.extend(chunks)
            all_vectors.append(vectors)

    if all_vectors:
        combined_vectors = np.vstack(all_vectors)
        _create_faiss_index_for_eval_context(combined_vectors, all_chunks)
    else:
        raise ValueError('No text extracted from the provided evaluation context files.')

async def set_current_metrics_data(filepath: str) -> None:
    """
    NEW PUBLIC FUNCTION: Loads the metrics JSON file and stores its content globally.
    """
    global _current_metrics_data
    try:
        _current_metrics_data = _extract_json_information(filepath)
    except FileNotFoundError as e:
        raise ValueError(f"Metrics JSON file not found: {filepath}. {e}")
    except json.JSONDecodeError:
        raise ValueError(f"Could not decode metrics JSON file at {filepath}. It might be malformed.")


async def get_evaluation_feedback(
    question: str,
    history: List[Tuple[str, str]],
    max_tokens: int
) -> str:
    """
    Generates evaluation feedback using the LLM, integrating context from already processed documents
    and globally stored metrics data.
    """
    # Check if metrics data has been loaded
    if _current_metrics_data is None:
        raise ValueError("Metrics data not loaded. Please upload the metrics JSON file first.")

    # Check if context index has been created
    if _eval_context_index is None:
        raise ValueError("Evaluation context not loaded. Please upload context documents first.")

    # Step 1: Retrieve context from the RAG index based on the question
    context = "\n\n".join(_search_eval_context_chunks(question))

    # Step 2: Use the globally stored metrics data
    metrics = _current_metrics_data

    # Step 3: Format chat history for the LLM prompt
    chat_history_str = ""
    for q, a in history:
        chat_history_str += f"Q: {q}\nA: {a}\n\n"

    # Step 4: Construct the final prompt for the LLM
    final_prompt = f"""<|im_start|>system
You are a helpful assistant in a document Q&A app set up, where the task is to generate evaluation feedback. Consider the metrics to contain information on the conducted evaluation. Use the added context, to enhance the answers created from the metrics. If the answer is not present in the context, print "Insufficient context" and nothing else. Structure your response in markdown, using bullet points or headings if appropriate. Ensure that if there is no relevant information, you provide "Insufficient context" and nothing else at all. <|im_end|>
{chat_history_str}
<|im_start|>user
Use the following metrics to answer the question. Enhance the answer using the given context, and print only the answer in markdown. Do not print information irrelevant to the question. If information is present in the context, do not print anything about insufficient context.

Metrics:
{metrics}

Context:
{context}

Question:
{question}<|im_end|>
<|im_start|>assistant
"""
    temp = 0.7

    # Step 5: Call the LLM to get a completion
    response = llm_model.create_completion(
        prompt=final_prompt,
        temperature=temp,
        max_tokens=max_tokens
    )

    assistant_reply = response['choices'][0]['text']
    assistant_reply = assistant_reply.replace("[/INST]", "").strip()
    return assistant_reply

