@echo off
REM ============================================================
REM  One-click launcher: start RAG backend + open DSVisualizer
REM  Pure ASCII only (Chinese Windows cmd is GBK codepage).
REM  Double-click this file.
REM ============================================================

set "PROJECT_DIR=D:\ai_canshow\DSVisualizer_push"
set "PYTHON=D:\ai_course\python.exe"

REM ---- sanity check: python exists ----
if not exist "%PYTHON%" (
    echo [ERROR] Python not found: %PYTHON%
    echo         Fix the PYTHON path at the top of this script.
    pause
    exit /b 1
)

REM ---- 1. Start RAG backend in its own window (stays open = service running) ----
start "RAG Service" cmd /k "cd /d %PROJECT_DIR%\rag-service && %PYTHON% server.py"
if errorlevel 1 (
    echo [ERROR] Failed to start RAG backend window.
    pause
    exit /b 1
)

REM ---- 2. Give RAG a moment to load its semantic cache ----
timeout /t 3 /nobreak >nul

REM ---- 3. Auto-detect newest DSVisualizer.exe (recursive, by modification time) ----
REM 用户可能在 debug/release/build-xxx 等不同目录生成 exe；直接递归取最新的，
REM 避免 release/ 里残留旧 exe 导致每次启动都是旧版本。
set "DS_EXE="
for /f "delims=" %%f in ('dir /s /b /o:-d "%PROJECT_DIR%\DSVisualizer.exe" 2^>nul') do (
    if not defined DS_EXE set "DS_EXE=%%f"
)

if not defined DS_EXE (
    echo [ERROR] DSVisualizer.exe not found anywhere under:
    echo   %PROJECT_DIR%
    echo.
    echo Build it first (Qt Creator: Build - Rebuild All), then re-run this script.
    echo Or edit DS_EXE path at the top of this script.
    pause
    exit /b 1
)

REM ---- 4. Launch DSVisualizer ----
echo Starting DSVisualizer: %DS_EXE%
start "" "%DS_EXE%"

echo.
echo ============================================================
echo   Done. Two things are now running:
echo     - RAG backend  : the "RAG Service" cmd window (keep open)
echo     - DSVisualizer  : the main app window
echo   Close the "RAG Service" window to stop the AI tutor.
echo ============================================================
timeout /t 4 /nobreak >nul
