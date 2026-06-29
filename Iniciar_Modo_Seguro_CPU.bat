@echo off
title AI Multimedia Enhancer - Modo Seguro CPU
echo Iniciando AI Multimedia Enhancer en MODO SEGURO (CPU)...
echo Este modo evita el uso de la GPU para prevenir errores de compatibilidad.

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

:: Forzar la ejecucion en CPU ocultando dispositivos CUDA
set CUDA_VISIBLE_DEVICES=-1

:: Iniciar la aplicacion
echo Iniciando aplicacion...
python main.py

pause
