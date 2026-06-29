import os
import urllib.request
import torch
import cv2
import numpy as np
import subprocess
import imageio_ffmpeg
from spandrel import ModelLoader
from tqdm import tqdm

def download_file(url, dest_path):
    print(f"Descargando modelo desde {url}...")
    urllib.request.urlretrieve(url, dest_path)
    print("Descarga completada.")

class VideoEnhancer:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = os.path.join("models", "RealESRGAN_x2plus.pth")
        self.model_url = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth"
        self.model = None

    def _load_model(self):
        if self.model is not None:
            return

        if not os.path.exists("models"):
            os.makedirs("models")
            
        if not os.path.exists(self.model_path):
            download_file(self.model_url, self.model_path)
            
        print("Cargando modelo de IA en la tarjeta gráfica...")
        model_loader = ModelLoader()
        model_arch = model_loader.load_from_file(self.model_path)
        
        # Necesitamos el tensor de evaluación (eval) y moverlo a CUDA
        self.model = model_arch.eval().to(self.device)
        print("Modelo cargado exitosamente.")

    def enhance_video(self, input_video_path, input_audio_path, output_video_path, resolution_option):
        self._load_model()
        
        cap = cv2.VideoCapture(input_video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        in_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        in_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # El modelo x2plus escala x2
        ai_out_width = in_width * 2
        ai_out_height = in_height * 2
        
        out_width = ai_out_width
        out_height = ai_out_height
        
        force_1080p = "1080p" in resolution_option
        if force_1080p:
            out_height = 1080
            # Mantener la relación de aspecto
            ratio = 1080 / ai_out_height
            out_width = int(ai_out_width * ratio)
            
            # Asegurar que las dimensiones sean pares (requerido por h264)
            if out_width % 2 != 0: out_width += 1
            if out_height % 2 != 0: out_height += 1

        print(f"Resolución Original: {in_width}x{in_height}")
        print(f"Resolución Final: {out_width}x{out_height} (Modo: {resolution_option})")
        
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        command = [
            ffmpeg_path,
            '-y',
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-s', f'{out_width}x{out_height}',
            '-pix_fmt', 'bgr24',
            '-r', str(fps),
            '-i', '-',
            '-i', input_audio_path,
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '18',
            '-c:a', 'aac',
            '-map', '0:v:0',
            '-map', '1:a:0',
            output_video_path
        ]
        
        print("Iniciando procesamiento de frames en la GPU...")
        proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        for _ in tqdm(range(total_frames), desc="Mejorando Video"):
            ret, frame = cap.read()
            if not ret:
                break
                
            # OpenCV BGR a Tensor RGB
            # [H, W, C] -> [C, H, W]
            tensor = torch.from_numpy(frame).permute(2, 0, 1).unsqueeze(0).float().to(self.device) / 255.0
            tensor = tensor[:, [2, 1, 0], :, :] # BGR to RGB
            
            with torch.no_grad():
                out_tensor = self.model(tensor)
                
            # Tensor RGB a numpy BGR
            out_tensor = out_tensor.clamp(0, 1).squeeze(0).permute(1, 2, 0).cpu().numpy()
            out_frame = (out_tensor[:, :, [2, 1, 0]] * 255).astype(np.uint8)
            
            if force_1080p and (out_frame.shape[0] != out_height or out_frame.shape[1] != out_width):
                out_frame = cv2.resize(out_frame, (out_width, out_height), interpolation=cv2.INTER_AREA)
                
            proc.stdin.write(out_frame.tobytes())
            
        proc.stdin.close()
        proc.wait()
        cap.release()
        print("Mejora de video completada.")
