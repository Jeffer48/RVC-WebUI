@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
echo Iniciando servidor RVC en http://127.0.0.1:8000 ...
start "" http://127.0.0.1:8000
.venv\Scripts\python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
