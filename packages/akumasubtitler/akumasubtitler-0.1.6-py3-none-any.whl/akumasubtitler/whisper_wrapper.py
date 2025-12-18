import whisper
from pathlib import Path

class WhisperWrapper:
    """Wrapper para Whisper (IA de OpenAI)."""

    def __init__(self, model_size: str = "base"):
        self.model = whisper.load_model(model_size)

    def transcribe(self, video_path: str, output_path: str):
        """Transcribe el audio de un video a subtítulos."""
        result = self.model.transcribe(video_path)
        with open(output_path, "w", encoding="utf-8") as f:
            for idx, segment in enumerate(result["segments"]):
                f.write(f"{idx + 1}\n")
                f.write(f"{self._format_time(segment['start'])} --> {self._format_time(segment['end'])}\n")
                f.write(f"{segment['text'].strip()}\n\n")

    def _format_time(self, seconds: float) -> str:
        """Formatea el tiempo para SRT."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"