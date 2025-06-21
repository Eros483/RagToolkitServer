# 🧠 RAG-Toolkit

A modular, GPU-accelerated Retrieval-Augmented Generation system built for [Critical AI](https://criticalai.in/). This toolkit integrates a FastAPI backend and a Streamlit frontend, with support for `llama-cpp-python` and custom embeddings.

---

## 📦 Repository

Clone the deployment-ready project:
```bash
git clone https://github.com/Eros483/rag-runner-deployment
cd rag-runner-deployment
⚙️ Environment Setup
We recommend using Anaconda for environment management.

Create the environment using the provided environment.yml:

bash
Copy
Edit
conda env create -f environment.yml
This will create an environment named ragEnv.

Activate the environment:

bash
Copy
Edit
conda activate ragEnv
Ensure the following are installed:

Node.js

Microsoft C++ Build Tools (via Visual Studio Build Tools)

NVIDIA CUDA Toolkit (matching your GPU driver and CUDA version)

🧩 Additional Dependencies
Install llama-cpp-python (compiled with CUDA):

bash
Copy
Edit
pip install llama-cpp-python
Install tileserver-gl-light globally:

bash
Copy
Edit
npm install -g tileserver-gl-light
🚀 Running the App
In Terminal 1 (backend):

bash
Copy
Edit
uvicorn backend.main:app --reload
In Terminal 2 (frontend):

bash
Copy
Edit
streamlit run frontend/app.py
📁 Project Structure
bash
Copy
Edit
rag-runner-deployment/
├── backend/               # FastAPI backend
├── frontend/              # Streamlit UI
├── environment.yml        # Conda environment config
├── README.md              # You're reading this!
└── ...
🧠 Notes
Uses llama.cpp backend for fast local inference (CUDA accelerated).

Built for research-grade RAG pipelines, customizable with different LLMs, vector stores, and UI components.

🧑‍💻 Maintainer
Developed by Arnab for Critical AI

📍 criticalai.in
🔗 github.com/Eros483

vbnet
Copy
Edit

Let me know if you want to add badges (license, build, GPU support), Docker instructions, or contribu
