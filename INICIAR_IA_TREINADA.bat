@echo off
chcp 65001 >nul
cd /d "%~dp0"
if exist ".venv-llm\Scripts\python.exe" goto check
set "PORTFOLIO_PY=python"
where python >nul 2>nul
if errorlevel 1 set "PORTFOLIO_PY=py"
echo Criando ambiente para a LLM. O primeiro uso precisa de internet.
%PORTFOLIO_PY% -m venv .venv-llm
if errorlevel 1 goto fail
:check
.venv-llm\Scripts\python.exe -c "import torch,transformers,safetensors,psutil" >nul 2>nul
if not errorlevel 1 goto run
.venv-llm\Scripts\python.exe -m pip install -r ml\requirements.txt
if errorlevel 1 goto fail
:run
.venv-llm\Scripts\python.exe -X utf8 iniciar.py
goto end
:fail
echo Não foi possível preparar o ambiente. Consulte ml/README.md.
:end
pause
