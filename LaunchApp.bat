@echo off
cd /d "%~dp0"

.venv\Scripts\python.exe -m streamlit run main.py

REM Activate the virtual environment
:: call .venv\Scripts\activate.bat && pty

REM Run the app
:: app

REM Deactivate the virtual environment (optional)
:: deactivate
pause