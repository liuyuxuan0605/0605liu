@echo off
REM ============================================================
REM  Start DSVisualizer RAG backend (AI tutor service)
REM  Double-click to run. Keep this window open = service running.
REM  Close this window = stop the service.
REM ============================================================
cd /d "D:\ai_canshow\DSVisualizer_push\rag-service"
if errorlevel 1 (
    echo [ERROR] Cannot enter directory D:\ai_canshow\DSVisualizer_push\rag-service
    pause
    exit /b 1
)

if not exist "D:\ai_course\python.exe" (
    echo [ERROR] Python not found: D:\ai_course\python.exe
    echo         Please fix the PYTHON path in this script.
    pause
    exit /b 1
)

echo ============================================================
echo   Starting RAG service on http://localhost:8000 ...
echo   Keep this window open. Close it to stop the service.
echo ============================================================
"D:\ai_course\python.exe" server.py

echo.
echo [RAG service stopped]
pause
