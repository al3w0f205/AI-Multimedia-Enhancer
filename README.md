# Reductor de Ruido con IA Local

![Estado](https://img.shields.io/badge/Estado-Estable-green)
![Plataforma](https://img.shields.io/badge/Plataforma-Windows-blue)

Una aplicacion de escritorio disenada para limpiar el ruido de fondo en archivos multimedia de forma completamente local, garantizando la privacidad de los datos. Esta impulsada por DeepFilterNet, una Inteligencia Artificial avanzada que aisla la voz y suprime el ruido no deseado (trafico, ventiladores, eco, etc.).

---

## Caracteristicas Principales

- **Privacidad Total**: Todo el procesamiento se realiza en el equipo local. Ningun archivo se carga a servidores externos.
- **Soporte Universal**:
  - **Audios**: `.mp3`, `.wav`, `.flac`, `.aac` y `.ogg` (Formato estandar para notas de voz de WhatsApp).
  - **Videos**: `.mp4`, `.mkv`, `.mov`, `.avi`. El sistema extrae el audio, lo procesa y reensambla el video original manteniendo la sincronizacion exacta.
- **Filtro Ajustable**: Incorpora un control de "Fuerza del Filtro" (0 a 100 dB) para permitir ajustes precisos en la agresividad de la limpieza, evitando distorsiones en la voz principal.
- **Vista Previa en Tiempo Real**: Permite reproducir instantaneamente los primeros 20 segundos del archivo bajo la configuracion actual, agilizando el flujo de trabajo sin generar archivos temporales persistentes en disco.
- **Auto-Apertura**: Al concluir el procesamiento, la carpeta de destino se abre automaticamente seleccionando el archivo final.

---

## Instrucciones de Uso

El software ha sido disenado para requerir conocimientos tecnicos nulos.

1. Navegue a la carpeta del proyecto.
2. Ejecute el archivo **`Iniciar_Aplicacion.bat`**.
3. En la interfaz principal, haga clic en **"Seleccionar Archivo"** e ingrese el medio deseado.
4. Ajuste la **Fuerza del Filtro** en el panel derecho (el valor 100 equivale a limpieza maxima).
5. Utilice el boton **"Vista Previa (20s)"** para verificar los resultados auditivos de la configuracion.
6. Haga clic en **"Procesar Archivo Completo"** una vez confirmada la calibracion.
7. El sistema abrira el directorio con el archivo procesado al terminar.

---

## Detalles Tecnicos

El proyecto sigue el Principio de Responsabilidad Unica (SRP) y fue construido mediante Test-Driven Development (TDD).

### Arquitectura y Dependencias
- **Core / Backend:** Python 3, PyTorch.
- **Modelo de Inferencia:** DeepFilterNet v3.
- **Procesamiento de Archivos:** MoviePy (FFmpeg), Soundfile, Torchaudio.
- **Interfaz Grafica (GUI):** CustomTkinter.
- **Reproduccion en Memoria RAM:** Sounddevice.
- **Pruebas Automatizadas:** Pytest con uso intensivo de dependencias simuladas (Mocks).

### Instalacion Manual y Desarrollo
1. Clonar el repositorio.
2. Crear un entorno virtual: `python -m venv venv`
3. Activar el entorno: `.\venv\Scripts\activate`
4. Instalar las dependencias requeridas: `pip install -r requirements.txt`
5. Ejecutar la aplicacion principal: `python main.py`
6. Correr la suite de pruebas unitarias: `pytest tests/`

---
Desarrollado para entornos locales de alto rendimiento y privacidad estricta.
