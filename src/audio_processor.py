import os
import sounddevice as sd
from typing import Optional

from df.enhance import enhance, init_df, load_audio, save_audio
from moviepy import VideoFileClip, AudioFileClip


class AudioProcessor:
    """
    Clase encargada de procesar archivos multimedia para reducir el ruido de fondo
    usando el modelo de IA DeepFilterNet.
    """

    def __init__(self) -> None:
        """
        Inicializa el procesador definiendo las extensiones compatibles.
        """
        self.video_extensions = {".mp4", ".mkv", ".mov", ".avi"}
        self.audio_extensions = {".mp3", ".wav", ".flac", ".aac", ".ogg"}

    def is_video_file(self, file_path: str) -> bool:
        """
        Determina si un archivo es un video basándose en su extensión.
        """
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.video_extensions

    def process_file(self, input_path: str, output_path: str, atten_lim_db: float = 100.0) -> None:
        """
        Procesa un archivo de entrada, reduce el ruido y lo guarda en la ruta indicada.
        Dependiendo del tipo (audio o video) ejecutará una lógica específica.
        
        Args:
            input_path (str): Ruta del archivo original con ruido.
            output_path (str): Ruta donde se guardará el archivo procesado.
            atten_lim_db (float): Filtro (0 a 100 dB).
        """
        if self.is_video_file(input_path):
            self._process_video(input_path, output_path, atten_lim_db)
        else:
            self._apply_deepfilternet(input_path, output_path, atten_lim_db)

    def _process_video(self, input_path: str, output_path: str, atten_lim_db: float) -> None:
        """
        Extrae el audio de un archivo de video, le aplica la limpieza de IA
        y reensambla el video final para mantener la sincronización.
        """
        temp_audio_in = f"{input_path}_temp_in.wav"
        temp_audio_out = f"{input_path}_temp_out.wav"

        try:
            with VideoFileClip(input_path) as video_clip:
                video_clip.audio.write_audiofile(temp_audio_in, logger=None)
                
                self._apply_deepfilternet(temp_audio_in, temp_audio_out, atten_lim_db)
                
                with AudioFileClip(temp_audio_out) as clean_audio_clip:
                    video_clip_with_clean_audio = video_clip.set_audio(clean_audio_clip)
                    video_clip_with_clean_audio.write_videofile(
                        output_path, 
                        audio_codec="aac",
                        logger=None
                    )
        finally:
            if os.path.exists(temp_audio_in):
                os.remove(temp_audio_in)
            if os.path.exists(temp_audio_out):
                os.remove(temp_audio_out)

    def _apply_deepfilternet(self, input_audio: str, output_audio: str, atten_lim_db: float) -> None:
        """
        Aplica el modelo de inferencia de DeepFilterNet al archivo de audio ingresado.
        """
        model, df_state, _ = init_df()
        audio, _ = load_audio(input_audio, sr=df_state.sr())
        enhanced_audio = enhance(model, df_state, audio, atten_lim_db=atten_lim_db)
        save_audio(output_audio, enhanced_audio, df_state.sr())

    def preview_audio(self, input_path: str, atten_lim_db: float = 100.0) -> None:
        """
        Extrae un fragmento de 20 segundos del archivo de entrada, le aplica la
        reducción de ruido en memoria y lo reproduce.
        """
        temp_audio_preview = f"{input_path}_preview.wav"
        try:
            with AudioFileClip(input_path) as clip:
                duration = min(20.0, clip.duration) if clip.duration else 20.0
                sub_clip = clip.subclip(0, duration)
                sub_clip.write_audiofile(temp_audio_preview, logger=None)
            
            # Cargar y aplicar IA
            model, df_state, _ = init_df()
            audio, _ = load_audio(temp_audio_preview, sr=df_state.sr())
            enhanced_audio = enhance(model, df_state, audio, atten_lim_db=atten_lim_db)
            
            # Convertir a numpy [muestras, canales] y reproducir
            audio_array = enhanced_audio.cpu().numpy().T
            sd.play(audio_array, samplerate=df_state.sr())
            sd.wait() # Esperar hasta terminar la reproducción
            
        finally:
            if os.path.exists(temp_audio_preview):
                os.remove(temp_audio_preview)

    def stop_preview(self) -> None:
        """
        Detiene cualquier reproducción en curso de sounddevice.
        """
        sd.stop()
