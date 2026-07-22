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

REM ---- 3. Auto-detect DSVisualizer.exe ----
set "DS_EXE="
if exist "%PROJECT_DIR%\release\DSVisualizer.exe" set "DS_EXE=%PROJECT_DIR%\release\DSVisualizer.exe"
if not defined DS_EXE if exist "%PROJECT_DIR%\bin\DSVisualizer.exe" set "DS_EXE=%PROJECT_DIR%\bin\DSVisualizer.exe"
if not defined DS_EXE if exist "%PROJECT_DIR%\debug\DSVisualizer.exe" set "DS_EXE=%PROJECT_DIR%\debug\DSVisualizer.exe"
if not defined DS_EXE if exist "%PROJECT_DIR%\DSVisualizer.exe" set "DS_EXE=%PROJECT_DIR%\DSVisualizer.exe"
if not defined DS_EXE (
    echo [INFO] Not in release/bin/debug/root. Searching recursively...
    for /r "%PROJECT_DIR%" %%f in (DSVisualizer.exe) do (
        if not defined DS_EXE set "DS_EXE=%%f"
    )
)

if not defined DS_EXE (
    echo [ERROR] DSVisualizer.exe not found in:
    echo   %PROJECT_DIR%\release\
    echo   %PROJECT_DIR%\debug\
    echo   %PROJECT_DIR%\
    echo.
    echo Build it first:
    echo   cd /d %PROJECT_DIR%
    echo   git reset --hard origin/feature/ai-tutor
    echo   qmake
    echo   mingw32-make
    echo.
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
