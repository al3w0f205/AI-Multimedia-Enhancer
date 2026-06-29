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

:: Activar entorno virtual
call .\venv\Scripts\activate.bat

:: Ejecutar instalacion inteligente de dependencias segun tarjeta grafica
echo Verificando y configurando dependencias de hardware...
python setup_dependencies.py

:: Iniciar la aplicacion
echo Iniciando aplicacion...
python main.py

pause
