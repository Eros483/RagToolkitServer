import pymupdf
import json
import os
import shutil
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import traceback
from typing import List, Dict, Tuple, Optional

PERSISTENT_INDEX_DIR="persistent_data"
PERSISTENT_FAISS_INDEX_PATH=os.path.join(PERSISTENT_INDEX_DIR, "permanent_rag_index.faiss")
PERSISTENT_TEXT_MAP_PATH=os.path.join(PERSISTENT_INDEX_DIR, "permanent_rag_index.json")

os.makedirs(PERSISTENT_INDEX_DIR, exist_ok=True)

_permanent_index: Optional[faiss.IndexFlatL2]=None
_permanent_id_to_text: Dict[int, str]={}
_embedder=SentenceTransformer('all-MiniLM-L6-v2')

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

def _extract_text_from_txt(filepath: str)-> str:
    '''
    input: filepath of txt
    output: text extracted from the txt
    '''
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()
    
def _extract_text_from_json(filepath: str)-> str:
    '''
    input: filepath of json
    output: text extracted from the json
    '''
    with open(filepath, 'r', encoding='utf-8') as f:
        data=json.load(f)
        return json.dumps(data, ensure_ascii=False, seperators=(',', ':'))

async def save_permanent_index() -> None:
    '''
    saves the in-memory faiss index and mappings to disk
    '''
    global _permanent_index, _permanent_id_to_text
    if _permanent_index is None:
        print("No permanent index to save. ")
        return
    
    faiss.write_index(_permanent_index, PERSISTENT_FAISS_INDEX_PATH)
    with open(PERSISTENT_TEXT_MAP_PATH, 'w', encoding='utf-8') as f:
        serializable_id_to_text={str(k): v for k, v in _permanent_id_to_text.items()}
        json.dump(serializable_id_to_text, f, ensure_ascii=False, separators=(',', ':'))
    print(f"Permanent FAISS index saved to {PERSISTENT_FAISS_INDEX_PATH}")
    print(f"Permanent text map saved to {PERSISTENT_TEXT_MAP_PATH}")

async def load_permanent_index() -> bool:
    global _permanent_index, _permanent_id_to_text
    if os.path.exists(PERSISTENT_FAISS_INDEX_PATH) and os.path.exists(PERSISTENT_TEXT_MAP_PATH):
        _permanent_index = faiss.read_index(PERSISTENT_FAISS_INDEX_PATH)
        with open(PERSISTENT_TEXT_MAP_PATH, 'r', encoding='utf-8') as f:
            loaded_map_str_keys=json.load(f)
            _permanent_id_to_text={int(k): v for k, v in loaded_map_str_keys.items()}
            print("Persistent faiss index loaded from disk")
            return True
    else:
        print("No persistent index to load. ")
        return False
    
async def delete_permanent_index_files()->None:
    '''
    deletes the persistent index files and clears in memory index.
    '''
    global _permanent_index, _permanent_id_to_text
    if os.path.exists(PERSISTENT_FAISS_INDEX_PATH):
        os.remove(PERSISTENT_FAISS_INDEX_PATH)
        print(f"Deleted persistent faiss index file {PERSISTENT_FAISS_INDEX_PATH}")
    
    if os.path.exists(PERSISTENT_TEXT_MAP_PATH):
        os.remove(PERSISTENT_TEXT_MAP_PATH)
        print(f"Deleted persistent text map file {PERSISTENT_TEXT_MAP_PATH}")

    _permanent_id_to_text={}
    _permanent_index=None
    print("Permanent index cleared from memory")

async def process_files_to_build_permanent_index(filepaths: List[str])->None:
    '''
    processes a list of file paths to build the permanent index
    '''
    global _permanent_index, _permanent_id_to_text

    all_chunks=[]
    all_vectors=[]
    for path in filepaths:
        text=""
        if path.lower().endswith('.pdf'):
            text=_extract_text_from_pdf(path)
        elif path.lower().endswith('.txt'):
            text=_extract_text_from_txt(path)
        elif path.lower().endswith('.json'):
            text=_extract_text_from_json(path)
        else:
            print(f"Skipping file {path} as it is not a supported file type")
            continue
        
        if text:
            chunks, vectors=_embed_text(text)
            if chunks and vectors.size>0:
                all_chunks.extend(chunks)
                all_vectors.append(vectors)
            else:
                print(f"Skipping file {path} as no meaningful text")

    if not all_vectors:
        raise ValueError('No text extracted from provided files')
    
    combined_vectors=np.vstack(all_vectors).astype('float32')

    dimension=combined_vectors.shape[1]
    _permanent_index=faiss.IndexFlatL2(dimension)
    _permanent_index.add(combined_vectors)

    _permanent_id_to_text={i: text for i, text in enumerate(all_chunks)}

    await save_permanent_index()

    print(f"Permanent index built and saved with {len(all_chunks)} chunks.")

async def get_permanent_chunks(query: str, top_k: int=5)->List[str]:
    '''
    returns the top k chunks of text that match the query
    '''
    global _permanent_index, _permanent_id_to_text
    query_vec=_embedder.encode([query]).astype('float32')
    D, I = _permanent_index.search(query_vec, k=top_k)
    valid_indices=[i for i in I[0] if i!=-1 and i<len(_permanent_id_to_text)]
    return [_permanent_id_to_text[i] for i in valid_indices]

async def get_permanent_index_status()->Dict:
    '''
    Returns status of permanent index (loaded, file existence, chunk count)
    '''
    is_loaded=_permanent_id_to_text is not None
    file_exists=os.path.exists(PERSISTENT_FAISS_INDEX_PATH) and os.path.exists(PERSISTENT_TEXT_MAP_PATH)
    chunk_count=len(_permanent_id_to_text) if _permanent_id_to_text else 0

    return {
        "is_loaded_in_memory": is_loaded,
        "file_exists_on_disk": file_exists,
        "chunk_count": chunk_count,
        "persistent_dir": os.path.abspath(PERSISTENT_INDEX_DIR)
    }