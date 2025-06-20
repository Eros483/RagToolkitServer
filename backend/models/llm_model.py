import llama_cpp
import os
import sys

from setup import download_metrics_folder, download_model

BASE_DIR= os.path.dirname(os.path.abspath(__file__))

models_dir=BASE_DIR

os.makedirs(models_dir, exist_ok=True)

download_metrics_folder()
download_model()

model_filename="Llama-3.2-8B-Instruct-Q5_K_M.gguf"
model_path=os.path.join(models_dir, model_filename)

if not os.path.exists(model_path):
    print(f"ERROR: Model file not found at: {model_path}")
    print("Please ensure the model has been downloaded correctly into the 'models' directory.")
    print("Exiting application as the core LLM model is missing.")
    sys.exit(1)

try:
    llm_model = llama_cpp.Llama(model_path=model_path, chat_format="llama-2", n_ctx=8192, n_gpu_layers=-1)
    print(f"LLM model loaded successfully from {model_path}")
except Exception as e:
    print(f"ERROR: Failed to load LLM model from {model_path}")
    print(f"Exception: {e}")
    print("Exiting application due to model loading failure.")
    sys.exit(1)