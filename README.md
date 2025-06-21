# 🧠 RAG-Toolkit

A modular, GPU-accelerated Retrieval-Augmented Generation system built for [Critical AI](https://criticalai.in/). This toolkit integrates a FastAPI backend and a Streamlit frontend, with support for `llama-cpp-python` LLMs and custom embeddings.

Everything runs completely locally, and offline, protecting your data, and removing any privacy concerns.

---

## 📦 Repository

Clone the deployment-ready project:
```
git clone https://github.com/Eros483/rag-runner-deployment
cd rag-runner-deployment
```
---
## ⚙️ Environment Setup
1. We recommend using Anaconda for environment management.

2. Create the environment using the provided environment.yml, and activate it:
```
conda env create -f environment.yml
conda activate ragEnv
npm install -g tileserver-gl-light
```
3. Ensure the following are installed:

    - Node.js
    - Microsoft C++ Build Tools (via Visual Studio Build Tools)
    - NVIDIA CUDA Toolkit (matching your GPU driver and CUDA version)

4. Install llama-cpp-python with CUDA compatibility, by following the below instructions:
```
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
where cl
where cmake
set CMAKE_ARGS=-DGGML_CUDA=ON
set FORCE_CMAKE=1
pip install llama-cpp-python --no-cache-dir --verbose
```
#### Note: Installation of llama-cpp-python can take well over an hour.
---

## 🚀 Running the App
```
python run_app.py
```
---
## 💡 Project Structure
```
D:.
|   .env
|   .gitignore
|   environment.yml
|   README.md
|   requirements.txt
|   run_app.py
|   test.ipynb
|   todo.txt
|
+---backend
|   |   main.py
|   |   setup.py
|   |
|   +---core
|   |   |   config.py
|   |   |   models.py
|   |
|   +---database
|   |   |   mongodb_client.py
|   |
|   +---metrics
|   |
|   +---models
|   |   |   Llama-3.2-8B-Instruct-Q5_K_M.gguf
|   |   |   llm_model.py
|   |
|   +---mongodb_sample_images
|   |
|   +---persistent_data
|   |       permanent_rag_index.faiss
|   |       permanent_rag_index.json
|   |
|   +---routers
|   |   |   evaluator_router.py
|   |   |   image_router.py
|   |   |   persistent_rag_router.py
|   |   |   rag_router.py
|   |   |   summarizer_router.py
|   |
|   +---sample_documents
|   |
|   +---services
|   |   |   evaluator_service.py
|   |   |   image_indexing_service.py
|   |   |   persistent_index.py
|   |   |   rag_service.py
|   |   |   summarizer_service.py

+---frontend
|   |   app.py
|   |
|   +---company_logo
|   |       logo.png
|   |
|   \---map_cache
|           mumbai_basic.pkl
```
---
## 🛠️ Frontend Preview
![Preview of Features](assets/dashboard.png)

---
## ⭐ Guide to available features
1. Knowledge Base Manager
    - Allows you to upload documents (supports .pdf, .docx, .txt) for persistent indexing.
    - Is retained independent of session, and can be utilised in RAG Chatbot.
2. RAG Chatbot
    - Allows you to chat with specialised llama 3.2, based on information fed to the knowledge base manager.
    - Allows functionality to further upload documents, for additionally specialised conversations.
    - Pulls images from MongoDB as relevant to query for greater detailing.
    - Pulls OSM mapping to any relevant cities and locations as mentioned in the query/response. 
        - Supported Cities: Mumbai
3. Document Summariser
    - Provides succinct summary of any and all documents provided.
4. Evaluation Assistant
    - Allows upload of a metrics file containing evaluation information
        - supports: *.json, *.pdf, *.txt, *.docx
    - Allows upload of a context file document for specialised chat
5. Max Tokens
    - Allows control over response lengths.
---
## 🧑‍💻 Upcoming Features
1. Adding support for asking questions by voice.
2. Extending supported OSM mapping.
---
## 💜 Notes
1. Must run first instance of the app with internet connection, to ensure all relevant files and dependencies are installed. Subsequent runs can run locally.
2. Modify mongoDB access in .env so that the app can access the relevant database.
    - Alternatively create custom mongoDB database by
        - Ensuring `mongod` and `mongosh` are accessible by terminal.
        - Utilising `test.ipynb`to manually upload images to mongoDB.
---
