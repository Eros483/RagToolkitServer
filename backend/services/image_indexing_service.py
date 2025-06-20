from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
import traceback

from database import mongodb_client

_image_index: Optional[faiss.IndexFlatL2]=None
_image_id_to_metadata: Dict[int, Dict[str, Any]]={}
_embedder: Optional[SentenceTransformer]=None

EMBEDDER_MODEL_NAME='all-MiniLM-L6-v2'

def _initialise_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBEDDER_MODEL_NAME)

def _prepare_image_text_for_embedding(image_doc: Dict[str, Any])->str:
    '''
    Combines image_name and labels into a single string for embedding
    '''
    image_name=image_doc.get("image_name", "").replace("_", "").replace(".png","").replace(".jpg","")
    labels=", ".join(image_doc.get("labels", []))

    return f"Image of {image_name}. Labels: {labels}." if labels else f"Image of {image_name}."

async def load_and_build_image_index()->bool:
    '''
    Connects to MongoDB, fetches image metadata, and builds an in-memory FAISS index for semantic image search
    '''
    global _image_index, _image_id_to_metadata, _embedder
    if _embedder is None:
        _initialise_embedder()

    print(f"Image indexing")

    try:
        await mongodb_client.connect_to_mongodb()
        all_images_docs=await mongodb_client.get_all_image_metadata()
        if not all_images_docs:
            print("No images in database")
            _image_index=None
            _image_id_to_metadata={}
            return False
        
        texts_to_embed: List[str]=[]
        metadata_list: List[Dict[str, Any]]=[]

        for doc in all_images_docs:
            if "image_name" in doc and "image_path" in doc:
                texts_to_embed.append(_prepare_image_text_for_embedding(doc))   
                metadata_list.append({
                    "image_name": doc["image_name"],
                    "image_path": doc["image_path"],
                    "labels": doc.get("labels", [])
                })
            else:
                print(f"Skipping image {doc['id']} due to missing metadata")

        if not texts_to_embed:
            print("No images to index")
            _image_index=None
            _image_id_to_metadata={}
            return False

        print(f" Image indexing: Embedding {len(texts_to_embed)}")
        embeddings=_embedder.encode(texts_to_embed).astype('float32')

        dimension=embeddings.shape[1]
        _image_index=faiss.IndexFlatL2(dimension)
        _image_index.add(embeddings)

        _image_id_to_metadata={i: metadata_list[i] for i in range(len(metadata_list))}
        return True

    except Exception as e:
        print(f"Error indexing images: {e}")
        traceback.print_exc()
        _image_index=None
        _image_id_to_metadata={}
        return False
    
async def search_image_semantic(query_text: str, top_k: int=3)->List[Dict[str, Any]]:
    """
    Performs semantic search on image metadata index
    """
    global _image_index, _image_id_to_metadata, _embedder

    if _image_index is None or _embedder is None:
        print("Image index not initialized")
        return []
    
    try:
        query_vec=_embedder.encode([query_text]).astype('float32')
        D, I=_image_index.search(query_vec, k=top_k)

        relevant_images_metadata=[]

        relevance_threshold=1.4

        for idx, distance in zip(I[0], D[0]):
            if idx!=-1 and idx in _image_id_to_metadata:
                if distance<=relevance_threshold:
                    relevant_images_metadata.append(_image_id_to_metadata[idx])
                else:
                    print(f"Skipping image {idx} due to low relevance")

        print(f"Image Indexing: Found {len(relevant_images_metadata)} relevant images for query")
        return relevant_images_metadata
    
    except Exception as e:
        print(f"Error searching images: {e}")
        traceback.print_exc()
        return []
    
async def get_image_index_status()-> Dict[str, Any]:
    """
    Returns the status of the image index
    """
    is_loaded=_image_index is not None
    num_indexed_images=_image_index.ntotal if _image_index else 0
    return {
        "is_image_index_loaded": is_loaded,
        "num_indexed_images": num_indexed_images,
        "embedder_status": "Loaded" if _embedder else "Not Loaded"
    }
