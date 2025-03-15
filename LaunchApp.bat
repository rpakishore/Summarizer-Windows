@echo off
setlocal
cd /d "%~dp0"

:: Check if 'uv' is installed
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo uv is not installed. Installing now...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo  Installation complete. Relaunch File...
    TIMEOUT /T 10
    exit /b
)

:: Define source and destination for the .streamlit folder
set "SOURCE_DIR=%CD%\.streamlit"
set "DEST_DIR=%USERPROFILE%\.streamlit"

:: Check if destination exists, if not, copy the folder
if not exist "%DEST_DIR%" (
    xcopy /E /I "%SOURCE_DIR%" "%DEST_DIR%" >nul
)


:: Run 'uv sync'
echo Running 'uv sync'...
uv sync

:: Run 'uv run streamlit run main.py'
echo Running 'uv run streamlit run main.py'...
uv run streamlit run main.py
