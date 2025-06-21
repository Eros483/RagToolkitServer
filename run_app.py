import subprocess

# Start FastAPI backend
backend = subprocess.Popen(["uvicorn", "backend.main:app", "--reload"])

# Start Streamlit frontend
frontend = subprocess.Popen(["streamlit", "run", "frontend/app.py"])

# Optional: Wait for both (Ctrl+C will interrupt both)
backend.wait()
frontend.wait()
