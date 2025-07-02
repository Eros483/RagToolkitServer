# Architecture 
## Pipeline structure
### Frontend
- Streamlit app
- Connected to backend via FastAPI api routers.

### Backend
Based on user selection, 4 primary sections and services offered:
- RAG Chatbot
- Summarisation Chat
- Analysis and Evaluation Chatbot
- Central Knowledge Base Manager
Requests are handled via API-> `backend/routers`-> `backend/services`.

## Feature Analysis
### Central Knowledge Base Manager
- `backend/routers/persistent_router.py` -> `backend/services/persistent_index.py`
- Handles persistent knowledge accessed by `RAG Chatbot`.
- Allows upload of documents for creation of common knowledge.
    - Reads documents
    - Splits them into chunks using `pymupdf`
    - Utilise FAISS for vectore store creation and search.
    - Embedding text using lightweight sentenceTransformers.

    - Stored locally at `backend/persistent_data`.
    - Handles status of permanent index and vector store.
### RAG Chatbot
- `backend/routers/rag_router.py` + `backend/routers/image_router.py` -> `backend/services/image_indexing_service.py` + `backend/services/rag_service.py`
- Provides specialised Multimodal chatbot functionality to user.
- Provides both text/audio input-output functionality.
- Also returns relevant `OSM` mapping and semantically similiar images retrieved from `MongoDB` based on labelling.
    - RAG functionality handled similiarly as in `Central Knowledge Base Manager`.

    - embeds query as well.
    - Vector matching is done, utilising euclidean distance as a metric.
    - Relevant chunks mapped to `top_k` matched vectors are returned.
    - Passed as context to the chatbot.
    - `labels` of Images are encoded as well, and stored in a `faiss` index.
    - `semantic` search is done to retrieve relevant feature images.
    - Utilises `folium` to retrieve relevant osm mapping based on location search in user query and chat response.

### Summarisation Chat
- `backend/routers/summarizer_router.py` -> `backend/services/summarizer_service.py`.
- Provides summary of any/all file(s) uploaded by user.
- Applying `kmeans clustering` to find most mentioned topics to find theme of given documents.
- Generated summaries of each cluster.
- Collated summaries to general one overall summary for any information provided by user.

### Analysis and Evaluation Chatbot
- `backend/evaluator_router.py`->`backend/evaluator_serivce.py`
- similiar to `RAG Chatbot`, chunks and vectorises informational document.
- Extract information from `.json` containing evaluation information.
- Creates response analysing evaluation information with respect to contextual information.
