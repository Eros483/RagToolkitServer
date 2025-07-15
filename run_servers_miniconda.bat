@echo off
echo Starting Backend and Frontend Applications...

REM Initialize conda for this session
call "%USERPROFILE%\miniconda3\Scripts\activate.bat"

REM Start backend server in new Anaconda prompt window
start "Backend Server" cmd /k "call %USERPROFILE%\miniconda3\Scripts\activate.bat && conda activate ragEnv && cd backend && uvicorn main:app --reload"

REM Start frontend application in new Anaconda prompt window  
start "Frontend App" cmd /k "call %USERPROFILE%\miniconda3\Scripts\activate.bat && conda activate ragEnv && cd frontend && streamlit run app.py"

echo Both applications are starting...
echo Backend will be available at: http://localhost:8000
echo Frontend will be available at: http://localhost:8501
<<<<<<< HEAD
pause
=======
<<<<<<< HEAD
pause
=======
pause
>>>>>>> 154b8867ef2ffc6145706b3a205784aedc8daf0d
>>>>>>> d6822043b0ac7ebe74e866ec2f37bdc1d92282a2
