import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
import subprocess
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
from .whisper_wrapper import WhisperWrapper

@dataclass
class SubStyle:
    """Estilo para subtítulos."""
    font: str = "Impact"
    size: int = 28
    color: str = "#FF0000"  # Rojo intenso
    border: int = 3         # Borde tipo llama
    position: str = "bottom-center"

class AkumaSubtitler:
    """Clase principal para generar videos con subtítulos."""

    def __init__(self):
        self.temp_files = []

    def forge_video(self, video_input: str, output_path: str, audio_track: str = None, subs_file: str = None, style: SubStyle = SubStyle()):
        """
        Crea videos con la furia de Akuma 🔥

        Args:
            video_input: Ruta del video a procesar.
            output_path: Destino del video final.
            audio_track: Pista de audio adicional (opcional).
            subs_file: Subtítulos externos (.srt/.ass).
            style: Estilo visual de los subtítulos.
        """
        success = False
        try:
            # Cargar el video
            video_clip = VideoFileClip(video_input)

            # Mezclar audio si se proporciona
            if audio_track:
                audio_clip = AudioFileClip(audio_track)
                final_audio = CompositeAudioClip([video_clip.audio, audio_clip])
                video_clip = video_clip.set_audio(final_audio)

            # Generar subtítulos si no se proporcionan
            if not subs_file:
                subs_file = self._generate_subtitles(video_input)

            # Crear archivo temporal para video con audio
            temp_video = self._create_temp_file(suffix=".mp4")
            video_clip.write_videofile(temp_video, codec="libx264", audio_codec="aac")

            # Aplicar subtítulos con FFmpeg
            self._apply_subtitles(temp_video, subs_file, output_path, style)
            success = True

        finally:
            if success:
                self._cleanup_temp_files()
            else:
                # Mantener los archivos temporales para depuración
                print("Warning: hubo un error durante el procesamiento — se mantienen archivos temporales:")
                for p in self.temp_files:
                    print("  ", p)

    def _generate_subtitles(self, video_path: str) -> str:
        """Genera subtítulos automáticos usando Whisper."""
        whisper = WhisperWrapper()
        subs_file = self._create_temp_file(suffix=".srt")
        whisper.transcribe(video_path, subs_file)
        return subs_file

    def _apply_subtitles(self, video_path: str, subs_path: str, output_path: str, style: SubStyle):
        """Aplica subtítulos al video usando FFmpeg."""
        def _hex_to_ass_color(hex_color: str) -> str:
            """Convert #RRGGBB to ASS/FFmpeg PrimaryColour format &H00BBGGRR."""
            if not hex_color:
                return "&H00FFFFFF"
            h = hex_color.lstrip('#')
            if len(h) != 6:
                return "&H00FFFFFF"
            r, g, b = h[0:2], h[2:4], h[4:6]
            # ASS expects BBGGRR after &H00
            return f"&H00{b}{g}{r}"
        # Normalize subtitle path to use forward slashes for ffmpeg filter
        subs_path_norm = subs_path.replace('\\', '/')
        # Escape colon (drive letter) and single quotes so the filter parser doesn't treat them as separators
        subs_path_escaped = subs_path_norm.replace(':', '\\:').replace("'", "\\'")
        ass_color = _hex_to_ass_color(style.color)

        subtitle_filter = (
            f"subtitles='{subs_path_escaped}':force_style="
            f"'Fontname={style.font},Fontsize={style.size},"
            f"PrimaryColour={ass_color},BorderStyle={style.border},"
            f"Alignment=2,MarginV=30'"
        )

        ffmpeg_cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vf", subtitle_filter,
            "-c:a", "copy",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-y",
            output_path
        ]

        print('Running ffmpeg with command:')
        print(' '.join(ffmpeg_cmd))
        try:
            completed = subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            # Mostrar salida de ffmpeg para depuración y relanzar con contexto
            print("FFmpeg failed with return code:", e.returncode)
            if e.stdout:
                print("--- ffmpeg stdout ---\n", e.stdout)
            if e.stderr:
                print("--- ffmpeg stderr ---\n", e.stderr)
            raise

    def _create_temp_file(self, suffix: str) -> str:
        """Crea un archivo temporal."""
        temp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        self.temp_files.append(temp.name)
        temp.close()
        return temp.name

    def _cleanup_temp_files(self):
        """Elimina archivos temporales."""
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        self.temp_files = []