from pyutube.handlers.PlaylistHandler import PlaylistHandler
import os
import sys

from pytubefix import YouTube
from pytubefix.helpers import safe_filename

from pyutube.utils import asking_video_or_audio, console, error_console
from pyutube.services.AudioService import AudioService
from pyutube.services.VideoService import VideoService
from pyutube.services.FileService import FileService


class DownloadService:
    def __init__(
        self,
        url: str,
        path: str,
        quality: str,
        is_audio: bool = False,
        make_playlist_in_order: bool = False,
    ):
        self.url = url
        self.path = path
        self.quality = quality
        self.is_audio = is_audio
        self.make_playlist_in_order = make_playlist_in_order

        self.video_service = VideoService(self.url, self.quality, self.path)
        self.audio_service = AudioService(url)
        self.file_service = FileService()

    # =========================
    # Helpers
    # =========================
    def _filename_from_stream(self, stream, video_id: str) -> str:
        try:
            ext = "m4a" if stream.type == "audio" else (stream.subtype or "mp4")
        except Exception:
            ext = "m4a" if self.is_audio else "mp4"

        return f"{video_id}.{ext}"

    def _already_downloaded(self, filename: str) -> bool:
        return os.path.exists(os.path.join(self.path, filename))

    # =========================
    # Main download
    # =========================
    def download(self, title_number: int = 0) -> bool:
        video, video_id, video_stream, audio_stream, self.quality = self.download_preparing()

        if self.is_audio:
            self.download_audio(video, audio_stream, video_id)
            return True

        return self.download_video(video, video_id, video_stream, audio_stream)

    # =========================
    # Audio
    # =========================
    def download_audio(
        self,
        video: YouTube,
        audio_stream: YouTube,
        video_id: str,
        title_number: int = 0,
    ) -> str:

        if not audio_stream:
            return ""

        audio_filename = self._filename_from_stream(audio_stream, video_id)

        if self._already_downloaded(audio_filename):
            console.print("⏭ Audio already exists, skipping download", style="warning")
            return os.path.join(self.path, audio_filename)

        try:
            console.print("⏳ Downloading the audio...", style="info")
            self.file_service.save_file(audio_stream, audio_filename, self.path)
        except Exception as error:
            error_console.print(
                f"❗ Error (report it here: https://github.com/Hetari/pyutube/issues):\n{error}"
            )
            sys.exit()

        return os.path.join(self.path, audio_filename)

    # =========================
    # Video
    # =========================
    def download_video(
        self,
        video: YouTube,
        video_id: str,
        video_stream: YouTube,
        audio_stream: YouTube,
        title_number: int = 0,
    ) -> bool:

        video_filename = self._filename_from_stream(video_stream, video_id)

        if self._already_downloaded(video_filename):
            console.print("⏭ Video already exists, skipping download", style="warning")
        else:
            try:
                console.print("⏳ Downloading the video...", style="info")
                self.file_service.save_file(video_stream, video_filename, self.path)
            except Exception as error:
                error_console.print(
                    f"❗ Error (report it here: @CB6BB :\n{error}"
                )
                sys.exit()

        # 🔊 تحميل الصوت بشكل مستقل
        self.download_audio(video, audio_stream, video_id)

        console.print("\n\n✅ Download completed", style="success")
        return self.quality


    def get_playlist_links(self):
        handler = PlaylistHandler(self.url, self.path)
        new_path, is_audio, videos_selected, make_in_order, playlist_videos = (
            handler.process_playlist()
        )

        self.make_playlist_in_order = make_in_order

        for index, video_id in enumerate(videos_selected):
            self.url = f"https://www.youtube.com/watch?v={video_id}"
            self.path = new_path
            self.is_audio = is_audio

            self.video_service = VideoService(self.url, self.quality, self.path)

            if index == 0:
                quality = self.download()
                continue

            self.quality = quality
            self.download()

    # =========================
    # Preparing
    # =========================
    def download_preparing(self):
        video = self.video_service.search_process()
        console.print(f"Title: {video.title}\n", style="info")

        video_id = video.video_id
        video_stream, audio_stream, self.quality = self.video_service.get_selected_stream(
            video, self.is_audio
        )

        return video, video_id, video_stream, audio_stream, self.quality