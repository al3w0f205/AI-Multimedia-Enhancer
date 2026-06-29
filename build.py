import os
import sys
import subprocess

def build():
    # Detectar customtkinter en el entorno virtual
    try:
        import customtkinter
    except ImportError:
        print("Error: customtkinter no esta instalado en el entorno de Python actual.")
        sys.exit(1)
        
    ctk_path = os.path.dirname(customtkinter.__file__)
    print(f"Ruta de customtkinter detectada: {ctk_path}")
    
    # Separador de paths para PyInstaller (--add-data)
    # En Windows es ';', en Linux/macOS es ':'
    sep = ";" if sys.platform.startswith("win") else ":"
    
    # Comando de PyInstaller para compilar la aplicacion a un directorio
    cmd = [
        "pyinstaller",
        "--noconsole",
        "--onedir",
        "--clean",
        "--name=AI-Multimedia-Enhancer",
        f"--add-data={ctk_path}{sep}customtkinter",
        f"--add-data=src{sep}src",
        "main.py"
    ]
    
    print("Ejecutando PyInstaller con el siguiente comando:")
    print(" ".join(cmd))
    
    subprocess.run(cmd, check=True)
    print("Compilacion completada con exito.")

if __name__ == "__main__":
    build()
