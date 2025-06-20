import pymupdf
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import traceback
from typing import List, Tuple, Dict, Optional
import os

from models.llm_model import llm_model
from services import persistent_index, image_indexing_service
from core.models import RAGResponse

model=llm_model
_embedder=SentenceTransformer('all-MiniLM-L6-v2')

_index: Optional[faiss.IndexFlatL2]=None
_id_to_text: Dict[int, str]={}


def _split_into_chunks(text, chunk_size=500, overlap=50):
    '''
    input: text in the form of  a string
    output: list of chunks of text, each of size chunk_size
    '''
    
    chunks=[]
    for i in range(0, len(text), chunk_size-overlap):
        chunks.append(text[i:i+chunk_size])
    return chunks

def _embed_text(text:str)->Tuple[List[str],np.ndarray]:
    # embed the text using the sentence transformer model
    '''
    input: text in the form of a string
    output: embedding of the text in the form of a numpy array, and the relevant chunks
    '''

    chunks=_split_into_chunks(text)
    vectors=_embedder.encode(chunks)
    return chunks, vectors

def _extract_text_from_pdf(filepath: str)-> str:
    '''
    input: filepath of pdf
    output: text extracted from the pdf
    '''
    doc=pymupdf.open(filepath)
    full_text=""
    for page in doc:
        full_text+=page.get_text()
    return full_text

def _create_index(vectors, chunks):
    '''
    input: list of vectors and list of chunks
    output: faiss index
    '''
    global _index
    global _id_to_text
    dimension=vectors.shape[1]
    _index=faiss.IndexFlatL2(dimension)
    _index.reset()
    _index.add(np.array(vectors).astype('float32'))
    _id_to_text={i:text for i,text in enumerate(chunks)}

def _search_chunks(query, top_k=3):
    '''
    input: query in the form of a string
    output: top_k most similar chunks
    '''
    query_vec=_embedder.encode([query]).astype('float32')
    D, I = _index.search(query_vec, k=top_k)
    valid_indices=[i for i in I[0] if i!=-1 and i<len(_id_to_text)]
    return [_id_to_text[i] for i in valid_indices]

async def process_files_for_rag(filepaths: list[str])-> None:
    '''
    input: list of filepaths
    processes files for text extraction and embedding, only for session specific index
    output: None
    '''
    all_chunks=[]
    all_vectors=[]
    for path in filepaths:
        if path.lower().endswith('.pdf'):
            text=_extract_text_from_pdf(path)

        elif path.endswith('.json'):
            with open(path, 'r') as f:
                text=f.read()
        
        else:
            continue
        chunks, vectors=_embed_text(text)
        all_chunks.extend(chunks)
        all_vectors.append(vectors)

    if all_vectors:
        all_vectors=np.vstack(all_vectors)
        _create_index(all_vectors, all_chunks)

    else:
        raise ValueError('No text extracted')
    
async def ask_model(question: str, history: list[tuple[str, str]], max_tokens: int)->RAGResponse:
    '''
    input: question as a string, and history of previous questions and answers, and max tokens to decide output length
    output: answer as a string
    '''
    all_context_chunks=[]
    session_chunks=[]
    if _index is not None:
        try:
            session_chunks=_search_chunks(question, top_k=5)
            all_context_chunks.extend(session_chunks)
        except Exception as e:
            print(f'Error in session specific search: {e}')

    permanent_chunks=await persistent_index.get_permanent_chunks(question, top_k=3)
    all_context_chunks.extend(permanent_chunks)

    combined_unique_context=list(dict.fromkeys(all_context_chunks))

    final_context_str = "\n\n".join(combined_unique_context)

    relevant_images_metadata=await image_indexing_service.search_image_semantic(question, top_k=3)
    FASTAPI_BASE_URL = os.getenv("FASTAPI_URL")

    image_urls=[]
    for img_meta in relevant_images_metadata:
        image_name=img_meta.get("image_name")
        if image_name:
            image_urls.append(f"{FASTAPI_BASE_URL}/images/{image_name}")
        else:
            print(f"Warning: Image metadata incomplete, missing image_name: {img_meta}")

    if not final_context_str.strip():
        if not image_urls:
            return RAGResponse(answer="Sorry, I couldn't find any relevant information.", image_urls=[])
        else:
            return RAGResponse(answer="Sorry, I couldn't find any relevant text.", image_urls=image_name)

    chat_history=""
    for q,a in history:
        chat_history+="Q: "+q+"\nA: "+a+"\n\n"
    #previous system prompt 
    '''
    final_prompt=f"""<|im_start|>system
    You are a helpful assistant in a document Q&A app. If the answer is not present in the context, print "Insufficient context" and nothing else. Structure your response in markdown, using bullet points or headings if appropriate. Ensure that if there is no relevant information, you provide "Insufficient context" and nothing else at all. <|im_end|>
    {chat_history}
    <|im_start|>user
    Use the following context to answer the question.

    Context:
    {context}

    Question:
    {question}<|im_end|>
    <|im_start|>assistant
    """

    temp=0.7
    max_tokens=512
    '''
    final_prompt=f"""<|im_start|>system
    ###instruction###
    Act as a helpful assistant in a document Q&A app.
    Assume the reader is college-educated, but not an expert.
    Answer the question with a clear and concise response. The question will be enclosed in ("").
    Use only the given context to answer the question. The context will be enclosed in (''').
    The output should be a structured response in markdown, using bullet points or headings if appropriate, and should answer the question.
    Be concise in your responses.
    If the answer is not present in the context, print "Insufficient context" and nothing else.
    If the user is not asking a question, but telling you their opinion or is giving feedback, acknowledge it, and prompt them to ask their next question. 
    Answer only questions relevant to the context.
    {chat_history}
    <|im_end|>
    <|im_start|>user

    ###user question details###
    Use the following context to answer the question.

    Context:
    '''{final_context_str}'''

    Question:
    ""{question}""<|im_end|>
    <|im_start|>assistant

    ###response###
    """

    temp=0.7

    response=model.create_completion(
        prompt=final_prompt,
        temperature=temp,
        max_tokens=max_tokens
    )

    assistant_reply=response['choices'][0]['text']
    assistant_reply=assistant_reply.replace("[/INST]", "")
    return RAGResponse(answer=assistant_reply, image_urls=image_urls)
