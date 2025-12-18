import os
import tempfile
from unittest import TestCase, skipIf
from akumasubtitler import AkumaSubtitler, SubStyle

WHISPER_AVAILABLE = True
try:
    import whisper
except ImportError:
    WHISPER_AVAILABLE = False

class TestAkumaSubtitler(TestCase):
    def setUp(self):
        self.subtitler = AkumaSubtitler()
        # Create a tiny test video file
        self.video_path = os.path.join(tempfile.gettempdir(), "test_video.mp4")
        self.output_path = os.path.join(tempfile.gettempdir(), "output_video.mp4")

    def tearDown(self):
        # Clean up test files
        for path in [self.video_path, self.output_path]:
            if os.path.exists(path):
                os.unlink(path)

    def test_substyle_default_values(self):
        """Test that SubStyle has correct default values"""
        style = SubStyle()
        self.assertEqual(style.font, "Impact")
        self.assertEqual(style.size, 28)
        self.assertEqual(style.color, "#FF0000")
        self.assertEqual(style.border, 3)
        self.assertEqual(style.position, "bottom-center")

    @skipIf(not WHISPER_AVAILABLE, "Whisper not installed")
    def test_forge_video_basic(self):
        """Test basic video forging (requires whisper)"""
        # Create a 1-second black video for testing
        import numpy as np
        from moviepy.editor import VideoClip
        def make_frame(t):
            return np.zeros((720,1280,3))
        clip = VideoClip(make_frame, duration=1)
        clip.write_videofile(self.video_path, fps=24)

        # Try to forge it with default settings
        try:
            self.subtitler.forge_video(
                video_input=self.video_path,
                output_path=self.output_path
            )
            self.assertTrue(os.path.exists(self.output_path))
        except Exception as e:
            self.fail(f"forge_video failed: {e}")