@echo off
setlocal EnableExtensions

:: ===================== Toolchain (detected from Qt Creator config) =====================
set "QMAKE=D:\file\5.12.11\mingw73_64\bin\qmake.exe"
set "MINGW=D:\file\Tools\mingw730_64\bin"

:: ===================== Project paths =====================
set "PROJECT_DIR=D:\ai_canshow\DSVisualizer_push"
set "PYTHON=D:\ai_course\python.exe"
set "BIN_DIR=%PROJECT_DIR%\bin"
set "DS_EXE=%BIN_DIR%\DSVisualizer.exe"

:: ===================== Verify toolchain =====================
if not exist "%QMAKE%" (
    echo [ERROR] qmake not found: %QMAKE%
    echo         Edit the QMAKE variable at the top of this script to your Qt 5.12 MinGW 64-bit path.
    pause & exit /b 1
)
if not exist "%MINGW%\mingw32-make.exe" (
    echo [ERROR] mingw32-make not found: %MINGW%\mingw32-make.exe
    pause & exit /b 1
)
:: Add MinGW toolchain to PATH (gcc/ar needed for compile)
set "PATH=%MINGW%;%PATH%"

:: ===================== [1/4] Python =====================
echo [1/4] Checking Python: %PYTHON%
if not exist "%PYTHON%" (
    echo [ERROR] Python not found. Fix PYTHON at the top of this script.
    pause & exit /b 1
)

:: ===================== [2/4] Build main app (Release) =====================
echo [2/4] Building DSVisualizer (Release)...
cd /d "%PROJECT_DIR%"
if not exist build_release mkdir build_release
cd build_release
"%QMAKE%" -o Makefile CONFIG+=release ..\DSVisualizer.pro
if errorlevel 1 ( echo [BUILD FAILED] qmake step & pause & exit /b 1 )
mingw32-make
if errorlevel 1 ( echo [BUILD FAILED] compile step (see error above) & pause & exit /b 1 )
echo       OK -^> %DS_EXE%

:: ===================== [3/4] Build AI plugin (Release) =====================
echo [3/4] Building AI plugin (Release)...
cd /d "%PROJECT_DIR%\src\ai"
if not exist build_release mkdir build_release
cd build_release
"%QMAKE%" -o Makefile CONFIG+=release ..\aiplugin.pro
if errorlevel 1 ( echo [PLUGIN BUILD FAILED] qmake step & pause & exit /b 1 )
mingw32-make
if errorlevel 1 ( echo [PLUGIN BUILD FAILED] compile step & pause & exit /b 1 )
echo       OK -^> %BIN_DIR%\plugins\aichatplugin.dll

:: ===================== [4/4] Launch RAG + app =====================
echo [4/4] Starting RAG backend and application...
if not exist "%PROJECT_DIR%\rag-service\server.py" (
    echo [ERROR] server.py missing: %PROJECT_DIR%\rag-service\server.py
    pause & exit /b 1
)
start "RAG Service" cmd /k "cd /d %PROJECT_DIR%\rag-service && %PYTHON% server.py"
echo       RAG window should appear (keep it open).
echo       If it shows ModuleNotFoundError, run:
echo         %PYTHON% -m pip install -r %PROJECT_DIR%\rag-service\requirements.txt
ping -n 3 127.0.0.1 >nul

if not exist "%DS_EXE%" (
    echo [ERROR] %DS_EXE% missing after build!
    pause & exit /b 1
)
start "" "%DS_EXE%"

echo.
echo ============================================================
echo  Done. Running:
echo    - RAG backend : the "RAG Service" window (keep it open)
echo    - DSVisualizer : main window (title should show [LIGHT])
echo  Press any key to close THIS window (both keep running).
echo ============================================================
pause
endlocal
