@echo off
echo Starting Backend and Frontend Applications...

REM Initialize conda for this session
call "%USERPROFILE%\anaconda3\Scripts\activate.bat"

REM Start backend server in new Anaconda prompt window
start "Backend Server" cmd /k "call %USERPROFILE%\anaconda3\Scripts\activate.bat && conda activate ragEnv && cd backend && uvicorn main:app --reload"

REM Start frontend application in new Anaconda prompt window  
start "Frontend App" cmd /k "call %USERPROFILE%\anaconda3\Scripts\activate.bat && conda activate ragEnv && cd frontend && streamlit run app.py"

echo Both applications are starting...
echo Backend will be available at: http://localhost:8000
echo Frontend will be available at: http://localhost:8501
<<<<<<< HEAD
pause
=======
pause
>>>>>>> 154b8867ef2ffc6145706b3a205784aedc8daf0d
