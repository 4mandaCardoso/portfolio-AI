@echo off
cd /d "%~dp0"
if exist ".venv-llm\Scripts\python.exe" goto install
python -m venv .venv-llm
if errorlevel 1 goto end
:install
.venv-llm\Scripts\python.exe -m pip install -r ml\requirements.txt
if errorlevel 1 goto end
.venv-llm\Scripts\python.exe -X utf8 ml\train.py
:end
pause
