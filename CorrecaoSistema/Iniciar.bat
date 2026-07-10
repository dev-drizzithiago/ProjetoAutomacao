@echo off
REM Inicia o CorrecaoSistema sempre com o Python do venv do projeto,
REM evitando depender de qual "python.exe" o Windows associa a arquivos .py.
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Ambiente virtual nao encontrado. Criando .venv e instalando dependencias...
    py -3.13 -m venv .venv || python -m venv .venv
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
)

".venv\Scripts\python.exe" main.py
if errorlevel 1 pause
