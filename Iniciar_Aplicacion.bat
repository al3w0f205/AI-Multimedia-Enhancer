@echo off
title AI Multimedia Enhancer
echo Inicializando AI Multimedia Enhancer...

:: Cambiar al directorio del script
cd /d "%~dp0"

:: Crear entorno virtual si no existe
if not exist "venv" (
    echo Creando entorno virtual de Python...
    python -m venv venv
)

:: Ejecutar instalacion inteligente de dependencias usando el Python del entorno virtual
echo Verificando y configurando dependencias de hardware...
".\venv\Scripts\python.exe" setup_dependencies.py

:: Iniciar la aplicacion usando el Python del entorno virtual
echo Iniciando aplicacion...
".\venv\Scripts\python.exe" main.py

pause
