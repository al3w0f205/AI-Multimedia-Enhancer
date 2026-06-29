# AI Multimedia Enhancer

[![GitHub stars](https://img.shields.io/github/stars/al3w0f205/AI-Multimedia-Enhancer?style=flat&label=Stars&logo=github&labelColor=444&color=DAAA3F&cacheSeconds=3600)](https://github.com/al3w0f205/AI-Multimedia-Enhancer/stargazers)
&nbsp;[![Total downloads](https://img.shields.io/github/downloads/al3w0f205/AI-Multimedia-Enhancer/total?style=flat&label=Downloads&labelColor=444&logo=hack-the-box&logoColor=white&cacheSeconds=600)](https://github.com/al3w0f205/AI-Multimedia-Enhancer/releases)
&nbsp;[![Latest downloads](https://img.shields.io/github/downloads/al3w0f205/AI-Multimedia-Enhancer/latest/total?style=flat&label=Downloads%20@latest&labelColor=444&logo=hack-the-box&logoColor=white&cacheSeconds=600)](https://github.com/al3w0f205/AI-Multimedia-Enhancer/releases/latest)
&nbsp;[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

AI Multimedia Enhancer es una herramienta de escritorio disenada para la optimizacion, reduccion de ruido, escalado e interpolacion de archivos multimedia de forma completamente local, garantizando la privacidad absoluta de los datos.

Unifica modelos de Inteligencia Artificial para el procesamiento de audio y video acelerados por hardware en una interfaz de dos columnas intuitiva, facilitando el procesamiento avanzado de archivos sin requerir configuraciones de consola.

---

## Caracteristicas Principales

### Procesamiento de Audio con IA
* **Reduccion de Ruido**: Impulsado por DeepFilterNet v3, un modelo que aisla la voz humana y elimina ruidos de fondo (trafico, ventiladores, estatica, eco).
* **Filtro Post-Procesamiento**: Opcion para supresiones adicionales de ruido acustico.
* **Control de Ganancia Manual**: Deslizador de ganancia de voz (+0.0 dB a +10.0 dB) para mejorar audios de bajo volumen.
* **Mejora Activa**: Filtro paso alto suave, realce de agudos en ~3000 Hz y normalizacion automatica de picos a -1 dB.
* **Formatos de Salida**: Guardado y conversion a formatos WAV (sin perdida), MP3 (comprimido) y FLAC (alta fidelidad).
* **Bitrate Ajustable**: Seleccion de bitrate (128k, 192k y 320k de estudio).

### Inferencia y Mejora de Video
* **Super Muestreo de Imagen**: Escalado x2 nativo mediante RealESRGAN, reconstruyendo detalles en la GPU.
* **Resoluciones Flexibles**: Permite guardar en 1080p (Super-Sampling), x2 (Doble resolucion) o ambas de manera simultanea.
* **Reescalado de FPS**: Permite aumentar la tasa de fotogramas a 30 FPS o 60 FPS usando algoritmos de mezcla temporal de FFmpeg para lograr una mayor fluidez de movimiento.
* **Factor de Calidad (CRF)**: Control de compresion (Maxima CRF 14, Alta CRF 18, Balanceada CRF 23).
* **Compatibilidad de Color**: Codificacion en el perfil de pixeles yuv420p H.264 para asegurar compatibilidad en sistemas operativos standard y navegadores.

### Experiencia de Usuario
* **Diseno Unificado**: Interfaz moderna de dos columnas lado a lado para control directo de audio y video.
* **Barra de Progreso Real**: Visualizacion del avance acumulado fotograma a fotograma durante el procesamiento.
* **Cancelacion Instantanea**: Boton dinamico para detener el procesamiento en cualquier momento, el cual limpia los procesos activos y elimina archivos temporales incompletos de disco.
* **Auto-Apertura**: El sistema abre el directorio de destino y selecciona el archivo final al completarse el renderizado.

---

## Download

[<img src="./assets/download_windows_installer.png" width="190">](https://github.com/al3w0f205/AI-Multimedia-Enhancer/releases)
[<img src="./assets/download_windows_zip.png" width="190">](https://github.com/al3w0f205/AI-Multimedia-Enhancer/releases)
[<img src="./assets/download_mac_dmg_arm64.png" width="190">](https://github.com/al3w0f205/AI-Multimedia-Enhancer/releases)
[<img src="./assets/download_mac_dmg_x64.png" width="190">](https://github.com/al3w0f205/AI-Multimedia-Enhancer/releases)
[<img src="./assets/download_linux_tar.png" width="190">](https://github.com/al3w0f205/AI-Multimedia-Enhancer/releases)

Las versiones ejecutables empaquetadas estan disponibles en la seccion de lanzamientos de GitHub. Para ejecutar desde el codigo fuente local, consulte las instrucciones a continuacion.

---

## Requisitos del Sistema

* **Sistema Operativo**: Windows 10 / 11 (64-bit).
* **Hardware Recomendado**:
  * CPU Intel Core i5 / AMD Ryzen 5 o superior.
  * 8 GB de RAM.
  * Tarjeta grafica dedicada NVIDIA (RTX o GTX) compatible con CUDA para aceleracion por GPU.
* **Modo Seguro CPU**: Si no dispone de GPU NVIDIA o presenta fallos de controladores, puede ejecutar el sistema en modo seguro CPU de forma estable.

---

## Instalacion y Desarrollo

### 1. Clonar el repositorio
```bash
git clone https://github.com/al3w0f205/AI-Multimedia-Enhancer.git
cd AI-Multimedia-Enhancer
```

### 2. Entorno virtual y dependencias
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

*Para aceleracion por hardware CUDA 12.4:*
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu124 --force-reinstall
```

### 3. Ejecucion de la aplicacion
* **Modo GPU**: Haga doble clic en `Iniciar_Aplicacion.bat` o ejecute `python main.py`.
* **Modo CPU**: Haga doble clic en `Iniciar_Modo_Seguro_CPU.bat` para evitar uso de GPU.

### 4. Pruebas Unitarias
```bash
python -m pytest tests/
```

---

## Licencia

Este proyecto esta licenciado bajo los terminos de la Licencia MIT. Consulte el archivo [LICENSE](LICENSE) para mas detalles.
