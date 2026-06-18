import pytest
from unittest.mock import patch, MagicMock
from src.audio_processor import AudioProcessor

class TestAudioProcessor:
    def test_is_video_file(self):
        processor = AudioProcessor()
        assert processor.is_video_file("test.mp4") is True
        assert processor.is_video_file("test.mp3") is False

    @patch("src.audio_processor.AudioProcessor._apply_deepfilternet")
    def test_process_audio_only(self, mock_apply_dfn):
        processor = AudioProcessor()
        
        # Pasamos el nuevo parámetro
        processor.process_file("input.mp3", "output.mp3", atten_lim_db=50.0)
        
        mock_apply_dfn.assert_called_once_with("input.mp3", "output.mp3", 50.0)

    @patch("src.audio_processor.VideoFileClip")
    @patch("src.audio_processor.AudioFileClip")
    @patch("src.audio_processor.AudioProcessor._apply_deepfilternet")
    def test_process_video(self, mock_apply_dfn, mock_audio_clip, mock_video_clip):
        processor = AudioProcessor()
        
        mock_v_clip_instance = MagicMock()
        mock_video_clip.return_value.__enter__.return_value = mock_v_clip_instance
        
        mock_a_clip_instance = MagicMock()
        mock_audio_clip.return_value.__enter__.return_value = mock_a_clip_instance

        # Ejecución con el nuevo parámetro
        processor.process_file("input.mp4", "output.mp4", atten_lim_db=70.0)
        
        mock_v_clip_instance.audio.write_audiofile.assert_called_once()
        mock_apply_dfn.assert_called_once()
        
        # Verificar que el tercer argumento de la llamada sea 70.0
        args, kwargs = mock_apply_dfn.call_args
        assert args[2] == 70.0
        
        mock_v_clip_instance.set_audio.assert_called_once_with(mock_a_clip_instance)

    @patch("src.audio_processor.sd")
    @patch("src.audio_processor.load_audio") # Asumiendo que simulamos carga y enhance para evitar escribir a disco
    @patch("src.audio_processor.enhance")
    @patch("src.audio_processor.AudioFileClip")
    def test_preview_audio(self, mock_audio_clip, mock_enhance, mock_load_audio, mock_sd):
        processor = AudioProcessor()
        
        mock_a_clip_instance = MagicMock()
        mock_a_clip_instance.duration = 50.0
        mock_audio_clip.return_value.__enter__.return_value = mock_a_clip_instance
        
        # Configuramos los mocks de la IA
        mock_load_audio.return_value = (MagicMock(), 48000)
        mock_enhance.return_value = MagicMock()

        processor.preview_audio("input.mp3", atten_lim_db=30.0)
        
        # El clip debe ser cortado a 20 segundos
        mock_a_clip_instance.subclip.assert_called_once_with(0, 20.0)
        # La librería de sonido debió haber llamado a play
        mock_sd.play.assert_called_once()
