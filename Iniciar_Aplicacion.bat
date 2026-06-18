@echo off
echo Iniciando Reductor de Ruido con IA...
echo Por favor espera unos segundos mientras carga el entorno local...

:: Cambiar al directorio donde esta el .bat
cd /d "%~dp0"

:: Activar el entorno e iniciar
call .\venv\Scripts\activate.bat
python main.py

pause
