import os
import urllib.request

# --- Model Download Configuration ---
MODEL_URL = "https://huggingface.co/tensorblock/Llama-3.2-8B-Instruct-GGUF/resolve/main/Llama-3.2-8B-Instruct-Q5_K_M.gguf"
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "Llama-3.2-8B-Instruct-Q5_K_M.gguf")

# --- Metrics Folder Download Configuration ---
METRICS_BASE_URL = "https://raw.githubusercontent.com/Eros483/RAG-runner/main/metrics/"
METRICS_DIR = "metrics" # Name of the folder to create locally
# CORRECTED: Only include 'sample1.json' as per the GitHub repository content
METRIC_FILES = [
    "sample1.json"
]

def download_model():
    """Downloads the Llama.cpp model."""
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
        print(f"Created directory: {MODEL_DIR}")
    
    if not os.path.exists(MODEL_PATH):
        print(f"Downloading model from {MODEL_URL} ...")
        try:
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
            print(f"Model downloaded and saved to {MODEL_PATH}")
        except Exception as e:
            print(f"Error downloading model: {e}")
    else:
        print(f"Model already exists at {MODEL_PATH}")

def download_metrics_folder():
    """Downloads the contents of the 'metrics' folder from GitHub."""
    if not os.path.exists(METRICS_DIR):
        os.makedirs(METRICS_DIR)
        print(f"Created directory: {METRICS_DIR}")
    
    print(f"\nChecking for metrics files in {METRICS_DIR}...")
    for filename in METRIC_FILES:
        remote_url = os.path.join(METRICS_BASE_URL, filename).replace("\\", "/") # Ensure forward slashes for URL
        local_path = os.path.join(METRICS_DIR, filename)

        if not os.path.exists(local_path):
            print(f"Downloading {filename} from {remote_url} ...")
            try:
                urllib.request.urlretrieve(remote_url, local_path)
                print(f"Downloaded {filename} to {local_path}")
            except Exception as e:
                print(f"Error downloading {filename}: {e}")
        else:
            print(f"File already exists: {local_path}")

