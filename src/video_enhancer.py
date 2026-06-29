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
            
        if self.device.type == "cuda":
            print("Cargando modelo de IA en la tarjeta gráfica (GPU)...")
        else:
            print("Cargando modelo de IA en la CPU (¡Atención: El procesamiento en CPU será muy lento!)...")
            
        model_loader = ModelLoader()
        model_arch = model_loader.load_from_file(self.model_path)
        
        self.model = model_arch.eval().to(self.device)
        print("Modelo cargado exitosamente.")

    def enhance_video(self, input_video_path, input_audio_path, output_video_path, resolution_option, audio_bitrate="192k", video_preset="fast", video_crf="18", video_format="mp4", progress_callback=None, video_fps="Original", cancel_check=None):
        self._load_model()
        
        cap = cv2.VideoCapture(input_video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        in_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        in_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Resolucion x2 nativa de la IA
        ai_out_width = in_width * 2
        ai_out_height = in_height * 2
        
        both_options = "Ambas" in resolution_option
        force_1080p = "1080p" in resolution_option or both_options
        
        # Configurar salida 1080p
        out_height_1080 = 1080
        ratio = 1080 / ai_out_height
        out_width_1080 = int(ai_out_width * ratio)
        if out_width_1080 % 2 != 0: out_width_1080 += 1
        if out_height_1080 % 2 != 0: out_height_1080 += 1
        
        # Configurar salida x2
        out_height_x2 = ai_out_height
        out_width_x2 = ai_out_width
        if out_width_x2 % 2 != 0: out_width_x2 += 1
        if out_height_x2 % 2 != 0: out_height_x2 += 1
        
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        
        def create_ffmpeg_proc(width, height, path):
            cmd = [
                ffmpeg_path, '-y', '-f', 'rawvideo', '-vcodec', 'rawvideo',
                '-s', f'{width}x{height}', '-pix_fmt', 'bgr24', '-r', str(fps),
                '-i', '-', '-i', input_audio_path
            ]
            
            # Filtros de video
            vf_filters = []
            if video_fps != "Original":
                try:
                    target_fps = int(video_fps.split()[0])
                    vf_filters.append(f"framerate=fps={target_fps}")
                except Exception:
                    pass
            
            if vf_filters:
                cmd.extend(['-vf', ",".join(vf_filters)])
                
            cmd.extend([
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', video_preset,
                '-crf', str(video_crf), '-c:a', 'aac', '-b:a', audio_bitrate,
                '-map', '0:v:0', '-map', '1:a:0', path
            ])
            
            return subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        procs = []
        base, _ = os.path.splitext(output_video_path)
        ext = f".{video_format.lower()}"
        output_video_path = f"{base}{ext}"
        
        if both_options:
            print(f"Modo: Ambas. Guardando 1080p ({out_width_1080}x{out_height_1080}) y x2 ({out_width_x2}x{out_height_x2}) simultáneamente.")
            proc_1080 = create_ffmpeg_proc(out_width_1080, out_height_1080, f"{base}_1080p{ext}")
            proc_x2 = create_ffmpeg_proc(out_width_x2, out_height_x2, f"{base}_x2{ext}")
            procs = [(proc_1080, out_width_1080, out_height_1080), (proc_x2, out_width_x2, out_height_x2)]
        elif force_1080p:
            print(f"Modo: 1080p. Guardando {out_width_1080}x{out_height_1080}.")
            proc_1080 = create_ffmpeg_proc(out_width_1080, out_height_1080, output_video_path)
            procs = [(proc_1080, out_width_1080, out_height_1080)]
        else:
            print(f"Modo: x2. Guardando {out_width_x2}x{out_height_x2}.")
            proc_x2 = create_ffmpeg_proc(out_width_x2, out_height_x2, output_video_path)
            procs = [(proc_x2, out_width_x2, out_height_x2)]
        
        print("Iniciando procesamiento de frames en la GPU...")
        
        for frame_idx in tqdm(range(total_frames), desc="Mejorando Video"):
            if cancel_check and cancel_check():
                print("Procesamiento de video cancelado por el usuario.")
                for proc, _, _ in procs:
                    try:
                        proc.stdin.close()
                        proc.wait()
                    except Exception:
                        pass
                cap.release()
                raise KeyboardInterrupt("Procesamiento cancelado por el usuario")

            ret, frame = cap.read()
            if not ret:
                break
                
            tensor = torch.from_numpy(frame).permute(2, 0, 1).unsqueeze(0).float().to(self.device) / 255.0
            tensor = tensor[:, [2, 1, 0], :, :]
            
            with torch.no_grad():
                out_tensor = self.model(tensor)
                
            out_tensor = out_tensor.clamp(0, 1).squeeze(0).permute(1, 2, 0).cpu().numpy()
            out_frame = (out_tensor[:, :, [2, 1, 0]] * 255).astype(np.uint8)
            
            for proc, w, h in procs:
                if out_frame.shape[0] != h or out_frame.shape[1] != w:
                    frame_to_write = cv2.resize(out_frame, (w, h), interpolation=cv2.INTER_AREA)
                else:
                    frame_to_write = out_frame
                proc.stdin.write(frame_to_write.tobytes())
                
            if progress_callback:
                progress_callback(frame_idx + 1, total_frames)
            
        for proc, _, _ in procs:
            proc.stdin.close()
            proc.wait()
            
        cap.release()
        print("Mejora de video completada.")
