# AI Multimedia Enhancer

![Estado](https://img.shields.io/badge/Estado-Estable-green)
![Plataforma](https://img.shields.io/badge/Plataforma-Windows-blue)
![GPU Support](https://img.shields.io/badge/GPU_Acelerada-CUDA_12.1%20%2F%2012.4-orange)

Una suite de escritorio profesional y ligera diseñada para la optimización, reducción de ruido, escalado e interpolación de archivos multimedia de forma **100% local**, garantizando la privacidad absoluta de sus datos.

Este software unifica modelos avanzados de Inteligencia Artificial para el procesamiento de audio y video acelerados por hardware en una interfaz intuitiva de dos columnas, eliminando cualquier complejidad técnica de la consola de comandos.

---

## Características Principales

### 🎧 Procesamiento de Audio con IA
* **Reducción de Ruido Inteligente**: Impulsado por **DeepFilterNet v3**, un modelo de aprendizaje profundo que aísla de forma impecable la voz humana y elimina ruidos de fondo constantes (tráfico, ventiladores, estática, ecos, etc.).
* **Reducción Ultra (Post-Filtro)**: Filtro adicional seleccionable para supresiones extremas de ruido acústico.
* **Control de Ganancia Manual**: Deslizador de ganancia de voz (+0.0 dB a +10.0 dB) para rescatar grabaciones o voces con volumen extremadamente bajo.
* **Mejora de Voz Activa**: Algoritmo que aplica de forma automática un filtro paso alto suave (corte en 80 Hz para eliminar ruidos sordos graves), realce de agudos en ~3000 Hz (brindando claridad y presencia) y normalización a -1 dB Peak.
* **Formatos de Salida Profesionales**: Guardado y conversión automática a formatos **WAV** (sin pérdida), **MP3** (comprimido) y **FLAC** (máxima fidelidad).
* **Calidad Personalizable**: Selección de bitrate (128k, 192k y 320k de estudio).

### 🎬 Inferencia y Mejora de Video (IA + FFmpeg)
* **Súper Muestreo de Imagen**: Reescalado x2 nativo mediante **RealESRGAN** (`RealESRGAN_x2plus.pth`), reconstruyendo detalles ópticos en la GPU.
* **Formatos de Salida Flexibles**: Permite guardar en **1080p (Super-Sampling)**, **x2 (Doble resolución)** o **Ambas** resoluciones de manera simultánea en una sola pasada.
* **Reescalado e Interpolación de FPS**: Permite duplicar o aumentar la tasa de fotogramas de salida a **30 FPS** o **60 FPS** usando el algoritmo de mezcla temporal de FFmpeg para lograr una fluidez cinematográfica suave.
* **Factor de Calidad (CRF)**: Control de compresión del codificador (Máxima CRF 14, Alta CRF 18, Balanceada CRF 23).
* **Presets de Velocidad**: Perfiles de codificación H.264 (ultrafast, fast, slow).
* **Compatibilidad de Color Universal**: Todos los videos se codifican en el perfil de píxeles `yuv420p` H.264 para asegurar que se reproduzcan correctamente en el reproductor nativo de Windows y cualquier navegador sin errores de compatibilidad.

### ⚡ Experiencia de Usuario y Diseño
* **Layout Unificado**: Interfaz moderna de dos columnas lado a lado que expone todos los ajustes de audio y video de forma simultánea.
* **Barra de Progreso Real**: Visualización del avance proporcional y acumulativo frame a frame durante el renderizado del video.
* **Cancelación Instantánea**: Botón dinámico para abortar el renderizado en cualquier momento, el cual cierra procesos subordinados y limpia del disco los archivos temporales o corruptos.
* **Vista Previa de Audio**: Permite escuchar al instante una porción del audio limpio sin necesidad de escribir el archivo completo en disco.
* **Auto-Apertura de Explorador**: Al finalizar con éxito, se abre la carpeta de salida y se selecciona el archivo de video o audio resultante automáticamente.

---

## Requisitos del Sistema

* **Sistema Operativo**: Windows 10 / 11 (64-bit).
* **Hardware Mínimo**:
  * CPU Intel Core i5 / AMD Ryzen 5 o superior.
  * 8 GB de Memoria RAM.
  * Tarjeta gráfica dedicada **NVIDIA (GeForce RTX o GTX)** compatible con CUDA para el procesamiento por GPU de video.
* **Modo Seguro CPU**: Si su equipo no dispone de una GPU NVIDIA dedicada o presenta problemas con los controladores, puede iniciar la aplicación en modo seguro CPU. El procesamiento de audio seguirá siendo casi instantáneo, mientras que la mejora de video se ejecutará en la CPU de forma más lenta.

---

## Estructura del Proyecto

* [main.py](file:///c:/Users/power/Desktop/Ale/Repos%20-%20Proyectos/ReductorRuidoIA/main.py): Punto de entrada principal que inicializa el tema visual y lanza la GUI.
* [src/app_gui.py](file:///c:/Users/power/Desktop/Ale/Repos%20-%20Proyectos/ReductorRuidoIA/src/app_gui.py): Código de la interfaz de usuario en CustomTkinter, lógica de hilos y control de flujo.
* [src/audio_processor.py](file:///c:/Users/power/Desktop/Ale/Repos%20-%20Proyectos/ReductorRuidoIA/src/audio_processor.py): Módulo encargado de la extracción de audio, procesamiento por DeepFilterNet, normalización y conversión de formatos.
* [src/video_enhancer.py](file:///c:/Users/power/Desktop/Ale/Repos%20-%20Proyectos/ReductorRuidoIA/src/video_enhancer.py): Módulo encargado de la decodificación de fotogramas con OpenCV, inferencia con RealESRGAN en GPU y codificación con FFmpeg.

---

## Instalación y Desarrollo

### 1. Clonar el repositorio
```bash
git clone https://github.com/SuUsuario/AI-Multimedia-Enhancer.git
cd AI-Multimedia-Enhancer
```

### 2. Entorno virtual y dependencias
Cree un entorno virtual de Python e instale los paquetes requeridos:
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

*Nota: Para asegurar la total estabilidad de su tarjeta gráfica NVIDIA en Windows, se recomienda instalar la compilación de PyTorch optimizada para CUDA 12.4:*
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu124 --force-reinstall
```

### 3. Ejecución de la aplicación
* **Modo GPU Estándar**: Haga doble clic en el archivo `Iniciar_Aplicacion.bat` o ejecute `python main.py` en su terminal activa.
* **Modo CPU Seguro**: Haga doble clic en `Iniciar_Modo_Seguro_CPU.bat` para forzar el procesamiento exclusivo en CPU y evitar pantallazos azules por conflictos de controladores.

### 4. Pruebas Unitarias
El proyecto cuenta con una suite completa de pruebas unitarias implementada con Pytest:
```bash
pytest tests/
```

---

## Licencia e Integridad
Este proyecto fue construido bajo estándares estrictos de Clean Code, el Principio de Responsabilidad Única (SRP) y desarrollo guiado por pruebas (TDD). 

Privacidad Garantizada: **Ningún dato o archivo multimedia sale de su máquina local.**
