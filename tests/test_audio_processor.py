import pytest
import torch
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
        processor.process_file("input.mp3", "output.mp3", atten_lim_db=50.0, apply_postprocess=True)
        mock_apply_dfn.assert_called_once_with("input.mp3", "output.mp3", 50.0, True)

    @patch("src.audio_processor.VideoFileClip")
    @patch("src.audio_processor.AudioFileClip")
    @patch("src.audio_processor.AudioProcessor._apply_deepfilternet")
    def test_process_video(self, mock_apply_dfn, mock_audio_clip, mock_video_clip):
        processor = AudioProcessor()
        mock_v_clip_instance = MagicMock()
        mock_video_clip.return_value.__enter__.return_value = mock_v_clip_instance
        mock_a_clip_instance = MagicMock()
        mock_audio_clip.return_value.__enter__.return_value = mock_a_clip_instance

        processor.process_file("input.mp4", "output.mp4", atten_lim_db=70.0, apply_postprocess=False)
        mock_v_clip_instance.audio.write_audiofile.assert_called_once()
        mock_apply_dfn.assert_called_once()
        args, kwargs = mock_apply_dfn.call_args
        assert args[2] == 70.0
        assert args[3] is False

    @patch("src.audio_processor.F")
    def test_postprocess(self, mock_F):
        processor = AudioProcessor()
        # Create a dummy tensor of shape [1, 100] with max val 0.5
        dummy_audio = torch.ones((1, 100)) * 0.5
        mock_F.highpass_biquad.return_value = dummy_audio
        mock_F.treble_biquad.return_value = dummy_audio
        
        result = processor._apply_postprocess(dummy_audio, 48000)
        
        mock_F.highpass_biquad.assert_called_once()
        mock_F.treble_biquad.assert_called_once()
        
        # Max val must be normalized to 0.89
        assert torch.isclose(result.abs().max(), torch.tensor(0.89), atol=1e-5)
