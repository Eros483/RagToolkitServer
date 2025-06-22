@echo off
REM === Path to activate.bat ===
set CONDA_BAT="C:\Users\arnab\miniconda3\Scripts\activate.bat"

REM === Launch Backend ===
start "Backend" cmd /k call %CONDA_BAT% ragEnv ^& cd backend ^& uvicorn main:app --reload

REM === Wait to prevent Conda temp file collision ===
timeout /t 3 > nul

REM === Launch Frontend ===
start "Frontend" cmd /k call %CONDA_BAT% ragEnv ^& cd frontend ^& streamlit run app.py
