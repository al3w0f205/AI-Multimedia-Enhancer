import os
import sys
import subprocess

def detect_gpus():
    """Detecta si el sistema cuenta con GPU NVIDIA, AMD o Intel."""
    has_nvidia = False
    has_amd_intel = False
    try:
        if sys.platform.startswith("win"):
            out = subprocess.check_output(["wmic", "path", "win32_VideoController", "get", "name"]).decode("utf-8", errors="ignore").lower()
            if "nvidia" in out:
                has_nvidia = True
            if "amd" in out or "radeon" in out or "intel" in out:
                has_amd_intel = True
        else:
            out = subprocess.check_output(["lspci"]).decode("utf-8", errors="ignore").lower()
            if "nvidia" in out:
                has_nvidia = True
            if "amd" in out or "ati" in out or "intel" in out:
                has_amd_intel = True
    except Exception:
        pass
    return has_nvidia, has_amd_intel

def install_deps():
    # Verificar instalación de torch
    try:
        import torch
        import torchaudio
        torch_installed = True
    except ImportError:
        torch_installed = False

    has_nvidia, has_amd_intel = detect_gpus()
    need_install_torch = not torch_installed

    # Si hay NVIDIA pero no tiene soporte de CUDA en torch
    if torch_installed and has_nvidia and not torch.cuda.is_available():
        print("Se detecto una GPU NVIDIA, pero la instalacion actual de PyTorch no tiene soporte CUDA. Reinstalando...")
        need_install_torch = True

    if need_install_torch:
        print("Configurando PyTorch optimizado para su hardware...")
        if has_nvidia:
            print("GPU NVIDIA detectada. Instalando PyTorch con aceleracion por hardware CUDA 12.4...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "torch", "torchaudio",
                "--index-url", "https://download.pytorch.org/whl/cu124", "--force-reinstall"
            ], check=True)
        elif has_amd_intel and sys.platform.startswith("win"):
            print("GPU AMD o Intel detectada en Windows. Instalando PyTorch base y soporte DirectML para aceleracion por hardware...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "torch", "torchaudio", "--force-reinstall"
            ], check=True)
            subprocess.run([
                sys.executable, "-m", "pip", "install", "torch-directml"
            ], check=True)
        else:
            print("No se detecto GPU dedicada compatible. Instalando PyTorch estándar para CPU...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "torch", "torchaudio", "--force-reinstall"
            ], check=True)
    else:
        print("PyTorch ya se encuentra configurado para su hardware.")
        # Si tiene AMD/Intel pero falta torch-directml en Windows
        if has_amd_intel and not has_nvidia and sys.platform.startswith("win"):
            try:
                import torch_directml
            except ImportError:
                print("Instalando soporte DirectML adicional para GPU AMD/Intel...")
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "torch-directml"
                ], check=True)

    # Instalar el resto de dependencias de requirements.txt
    print("Verificando el resto de dependencias en requirements.txt...")
    if os.path.exists("requirements.txt"):
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        
    print("Todas las dependencias estan listas y configuradas.")

if __name__ == "__main__":
    install_deps()
