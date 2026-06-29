@echo off
echo Iniciando Reductor de Ruido con IA en MODO SEGURO (CPU)...
echo Este modo evita el uso de la tarjeta grafica (GPU) para prevenir errores de compatibilidad.
echo Por favor espera unos segundos mientras carga el entorno local...

:: Cambiar al directorio donde esta el .bat
cd /d "%~dp0"

:: Forzar la ejecucion en CPU ocultando dispositivos CUDA
set CUDA_VISIBLE_DEVICES=-1

:: Activar el entorno e iniciar
call .\venv\Scripts\activate.bat
python main.py

pause
