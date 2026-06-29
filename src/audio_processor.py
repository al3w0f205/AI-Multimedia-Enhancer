import os
import subprocess
import imageio_ffmpeg
import torch
import sounddevice as sd
import torchaudio.functional as F
from typing import Optional

from df.enhance import enhance, init_df, load_audio, save_audio
from moviepy import VideoFileClip, AudioFileClip


class AudioProcessor:
    def __init__(self) -> None:
        self.video_extensions = {".mp4", ".mkv", ".mov", ".avi"}
        self.audio_extensions = {".mp3", ".wav", ".flac", ".aac", ".ogg"}

    def is_video_file(self, file_path: str) -> bool:
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.video_extensions

    def process_file(self, input_path: str, output_path: str, atten_lim_db: float = 100.0, apply_postprocess: bool = True, enhance_video: bool = False, video_resolution: str = "1080p") -> None:
        if self.is_video_file(input_path):
            try:
                self._process_video(input_path, output_path, atten_lim_db, apply_postprocess, enhance_video, video_resolution)
            except Exception as e:
                print(f"Advertencia: No se pudo procesar {input_path} como video. Intentando como audio puro... Error: {str(e)}")
                # Cambiamos la extensión de salida a .wav ya que el original tenía extensión de video
                base_name = os.path.splitext(output_path)[0]
                audio_output_path = f"{base_name}.wav"
                
                temp_fallback_wav = f"{input_path}_fallback.wav"
                try:
                    with AudioFileClip(input_path) as audio_clip:
                        audio_clip.write_audiofile(temp_fallback_wav, logger="bar")
                    self._apply_deepfilternet(temp_fallback_wav, audio_output_path, atten_lim_db, apply_postprocess)
                finally:
                    if os.path.exists(temp_fallback_wav):
                        os.remove(temp_fallback_wav)
        else:
            self._apply_deepfilternet(input_path, output_path, atten_lim_db, apply_postprocess)

    def _process_video(self, input_path: str, output_path: str, atten_lim_db: float, apply_postprocess: bool, enhance_video: bool, video_resolution: str) -> None:
        temp_audio_in = f"{input_path}_temp_in.wav"
        temp_audio_out = f"{input_path}_temp_out.wav"
        try:
            # Extraer audio original
            with VideoFileClip(input_path) as video_clip:
                video_clip.audio.write_audiofile(temp_audio_in, logger="bar")
            
            # Limpiar audio con IA
            self._apply_deepfilternet(temp_audio_in, temp_audio_out, atten_lim_db, apply_postprocess)
            
            # Unir video original (sin alterar) con el nuevo audio usando FFmpeg directamente
            if enhance_video:
                print("Mejorando video con Inteligencia Artificial (Spandrel)...")
                from src.video_enhancer import VideoEnhancer
                enhancer = VideoEnhancer()
                enhancer.enhance_video(input_path, temp_audio_out, output_path, video_resolution)
            else:
                print("Uniendo video y audio limpio...")
                ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
                subprocess.run([
                    ffmpeg_path,
                    "-y", 
                    "-i", input_path,
                    "-i", temp_audio_out,
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-map", "0:v:0",
                    "-map", "1:a:0",
                    output_path
                ], check=True)
            print("Video guardado exitosamente.")
            
        finally:
            if os.path.exists(temp_audio_in):
                os.remove(temp_audio_in)
            if os.path.exists(temp_audio_out):
                os.remove(temp_audio_out)

    def _apply_deepfilternet(self, input_audio: str, output_audio: str, atten_lim_db: float, apply_postprocess: bool) -> None:
        model, df_state, _ = init_df()
        audio, _ = load_audio(input_audio, sr=df_state.sr())
        enhanced_audio = enhance(model, df_state, audio, atten_lim_db=atten_lim_db)
        
        if apply_postprocess:
            enhanced_audio = self._apply_postprocess(enhanced_audio, df_state.sr())
            
        save_audio(output_audio, enhanced_audio, df_state.sr())

    def _apply_postprocess(self, audio: torch.Tensor, sr: int) -> torch.Tensor:
        """Aplica ecualización y normalización al tensor de audio."""
        # 1. Filtro High-pass suave (quita ruido grave retumbante de <80Hz)
        audio = F.highpass_biquad(audio, sr, cutoff_freq=80.0)
        
        # 2. Boost suave de agudos (aire y claridad en la voz en ~3000Hz)
        audio = F.treble_biquad(audio, sr, gain=3.0, central_freq=3000.0)
        
        # 3. Normalización a -1 dB Peak (~0.89 linear) para volumen profesional
        max_val = audio.abs().max()
        if max_val > 0:
            audio = audio / max_val * 0.89
            
        return audio

    def preview_audio(self, input_path: str, atten_lim_db: float = 100.0, apply_postprocess: bool = True) -> None:
        temp_audio_preview = f"{input_path}_preview.wav"
        try:
            with AudioFileClip(input_path) as clip:
                duration = min(20.0, clip.duration) if clip.duration else 20.0
                sub_clip = clip.subclip(0, duration)
                sub_clip.write_audiofile(temp_audio_preview, logger="bar")
            
            model, df_state, _ = init_df()
            audio, _ = load_audio(temp_audio_preview, sr=df_state.sr())
            enhanced_audio = enhance(model, df_state, audio, atten_lim_db=atten_lim_db)
            
            if apply_postprocess:
                enhanced_audio = self._apply_postprocess(enhanced_audio, df_state.sr())
            
            audio_array = enhanced_audio.cpu().numpy().T
            sd.play(audio_array, samplerate=df_state.sr())
            sd.wait()
            
        finally:
            if os.path.exists(temp_audio_preview):
                os.remove(temp_audio_preview)

    def stop_preview(self) -> None:
        sd.stop()
