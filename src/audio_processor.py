import os
import subprocess
import imageio_ffmpeg
import torch
import sounddevice as sd
import torchaudio.functional as F
from typing import Optional

# Corrección de compatibilidad para versiones modernas de torchaudio (2.2+)
import sys
import torchaudio
try:
    import torchaudio.backend.common
except ImportError:
    import types
    # Crear módulo ficticio en sys.modules para engañar al importador de DeepFilterNet
    dummy_module = types.ModuleType("torchaudio.backend.common")
    dummy_module.AudioMetaData = torchaudio.AudioMetaData
    sys.modules["torchaudio.backend.common"] = dummy_module

from df.enhance import enhance, init_df, load_audio, save_audio
from moviepy import VideoFileClip, AudioFileClip


class AudioProcessor:
    def __init__(self) -> None:
        self.video_extensions = {".mp4", ".mkv", ".mov", ".avi"}
        self.audio_extensions = {".mp3", ".wav", ".flac", ".aac", ".ogg"}

    def is_video_file(self, file_path: str) -> bool:
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.video_extensions

    def process_file(
        self, 
        input_path: str, 
        output_path: str, 
        atten_lim_db: float = 100.0, 
        apply_postprocess: bool = True, 
        enhance_video: bool = False, 
        video_resolution: str = "1080p",
        audio_bitrate: str = "192k",
        video_preset: str = "fast",
        post_filter: bool = False,
        audio_gain: float = 0.0,
        audio_format: str = "wav",
        video_crf: str = "18",
        video_format: str = "mp4",
        progress_callback=None,
        video_fps: str = "Original",
        cancel_check=None
    ) -> None:
        if self.is_video_file(input_path):
            base_name = os.path.splitext(output_path)[0]
            output_path = f"{base_name}.{video_format.lower()}"
            try:
                self._process_video(input_path, output_path, atten_lim_db, apply_postprocess, enhance_video, video_resolution, audio_bitrate, video_preset, post_filter, audio_gain, video_crf, video_format, progress_callback, video_fps, cancel_check)
            except Exception as e:
                print(f"Advertencia: No se pudo procesar {input_path} como video. Intentando como audio puro... Error: {str(e)}")
                audio_output_path = f"{base_name}.{audio_format.lower()}"
                
                temp_fallback_wav = f"{input_path}_fallback.wav"
                try:
                    with AudioFileClip(input_path) as audio_clip:
                        audio_clip.write_audiofile(temp_fallback_wav, logger="bar")
                    self._apply_deepfilternet(temp_fallback_wav, audio_output_path, atten_lim_db, apply_postprocess, post_filter, audio_gain, audio_format, audio_bitrate)
                finally:
                    if os.path.exists(temp_fallback_wav):
                        os.remove(temp_fallback_wav)
        else:
            base_name = os.path.splitext(output_path)[0]
            audio_output_path = f"{base_name}.{audio_format.lower()}"
            self._apply_deepfilternet(input_path, audio_output_path, atten_lim_db, apply_postprocess, post_filter, audio_gain, audio_format, audio_bitrate)

    def _process_video(
        self, 
        input_path: str, 
        output_path: str, 
        atten_lim_db: float, 
        apply_postprocess: bool, 
        enhance_video: bool, 
        video_resolution: str,
        audio_bitrate: str,
        video_preset: str,
        post_filter: bool,
        audio_gain: float,
        video_crf: str,
        video_format: str,
        progress_callback=None,
        video_fps: str = "Original",
        cancel_check=None
    ) -> None:
        temp_audio_in = f"{input_path}_temp_in.wav"
        temp_audio_out = f"{input_path}_temp_out.wav"
        try:
            # Extraer audio original
            with VideoFileClip(input_path) as video_clip:
                video_clip.audio.write_audiofile(temp_audio_in, logger="bar")
            
            # Limpiar audio con IA
            self._apply_deepfilternet(temp_audio_in, temp_audio_out, atten_lim_db, apply_postprocess, post_filter, audio_gain, "wav", audio_bitrate)
            
            # Unir video original (sin alterar) con el nuevo audio usando FFmpeg directamente
            if enhance_video:
                print("Mejorando video con Inteligencia Artificial (Spandrel)...")
                from src.video_enhancer import VideoEnhancer
                enhancer = VideoEnhancer()
                enhancer.enhance_video(input_path, temp_audio_out, output_path, video_resolution, audio_bitrate, video_preset, video_crf, video_format, progress_callback, video_fps, cancel_check)
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
                    "-b:a", audio_bitrate,
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

    def _apply_deepfilternet(self, input_audio: str, output_audio: str, atten_lim_db: float, apply_postprocess: bool, post_filter: bool = False, audio_gain: float = 0.0, audio_format: str = "wav", audio_bitrate: str = "192k") -> None:
        model, df_state, _ = init_df(post_filter=post_filter)
        audio, _ = load_audio(input_audio, sr=df_state.sr())
        enhanced_audio = enhance(model, df_state, audio, atten_lim_db=atten_lim_db)
        
        if apply_postprocess:
            enhanced_audio = self._apply_postprocess(enhanced_audio, df_state.sr(), audio_gain)
            
        # Asegurar salida estéreo (2 canales idénticos)
        if enhanced_audio.shape[0] == 1:
            enhanced_audio = enhanced_audio.repeat(2, 1)
            
        ext = audio_format.lower()
        if ext == "wav":
            save_audio(output_audio, enhanced_audio, df_state.sr())
        else:
            temp_wav = f"{output_audio}_temp_out.wav"
            save_audio(temp_wav, enhanced_audio, df_state.sr())
            try:
                ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
                if ext == "mp3":
                    cmd = [ffmpeg_path, "-y", "-i", temp_wav, "-c:a", "libmp3lame", "-b:a", audio_bitrate, output_audio]
                elif ext == "flac":
                    cmd = [ffmpeg_path, "-y", "-i", temp_wav, "-c:a", "flac", output_audio]
                else:
                    cmd = [ffmpeg_path, "-y", "-i", temp_wav, output_audio]
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            finally:
                if os.path.exists(temp_wav):
                    os.remove(temp_wav)

    def _apply_postprocess(self, audio: torch.Tensor, sr: int, audio_gain: float = 0.0) -> torch.Tensor:
        """Aplica ecualización, normalización y ganancia extra al tensor de audio."""
        # 1. Filtro High-pass suave (quita ruido grave retumbante de <80Hz)
        audio = F.highpass_biquad(audio, sr, cutoff_freq=80.0)
        
        # 2. Boost suave de agudos (aire y claridad en la voz en ~3000Hz)
        audio = F.treble_biquad(audio, sr, gain=3.0, central_freq=3000.0)
        
        # 3. Aplicar ganancia extra de voz si se solicita (en dB)
        if audio_gain > 0:
            gain_factor = 10 ** (audio_gain / 20.0)
            audio = audio * gain_factor
            
        # 4. Normalización a -1 dB Peak (~0.89 linear) para volumen profesional
        max_val = audio.abs().max()
        if max_val > 0:
            audio = audio / max_val * 0.89
            
        return audio

    def preview_audio(self, input_path: str, atten_lim_db: float = 100.0, apply_postprocess: bool = True, post_filter: bool = False, audio_gain: float = 0.0) -> None:
        temp_audio_preview = f"{input_path}_preview.wav"
        try:
            with AudioFileClip(input_path) as clip:
                duration = min(20.0, clip.duration) if clip.duration else 20.0
                sub_clip = clip.subclip(0, duration)
                sub_clip.write_audiofile(temp_audio_preview, logger="bar")
            
            model, df_state, _ = init_df(post_filter=post_filter)
            audio, _ = load_audio(temp_audio_preview, sr=df_state.sr())
            enhanced_audio = enhance(model, df_state, audio, atten_lim_db=atten_lim_db)
            
            if apply_postprocess:
                enhanced_audio = self._apply_postprocess(enhanced_audio, df_state.sr(), audio_gain)
            
            # Asegurar salida estéreo para reproducción
            if enhanced_audio.shape[0] == 1:
                enhanced_audio = enhanced_audio.repeat(2, 1)
                
            audio_array = enhanced_audio.cpu().numpy().T
            sd.play(audio_array, samplerate=df_state.sr())
            sd.wait()
            
        finally:
            if os.path.exists(temp_audio_preview):
                os.remove(temp_audio_preview)

    def stop_preview(self) -> None:
        sd.stop()
