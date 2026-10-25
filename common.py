import tempfile
from pathlib import Path

import imageio_ffmpeg
from tqdm import tqdm
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

DEFAULT_DIR = str(Path(__file__).resolve().parent / "downloads")

class ProgressBar:
    """yt-dlp progress hook that draws one tqdm bar per downloaded stream."""

    def __init__(self):
        self.bar = None
        self.last_bytes = 0

    def __call__(self, d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            done = d.get("downloaded_bytes", 0)

            if self.bar is None:
                self.bar = tqdm(
                    total=total,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=Path(d["filename"]).name[:40],
                )
                self.last_bytes = 0

            if total and self.bar.total != total:
                self.bar.total = total

            self.bar.update(done - self.last_bytes)
            self.last_bytes = done

        elif d["status"] == "finished":
            self.close()

    def close(self):
        if self.bar is not None:
            self.bar.close()
            self.bar = None


def run_download(url, output_dir, playlist, extra_options, archive_name) -> bool:
    """Shared logic: temp folder, error handling, progress bar.

    extra_options holds whatever is specific to MP4 or MP3.
    """
    progress = ProgressBar()
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    if playlist:
        outtmpl = "%(playlist_title)s/%(playlist_index)03d - %(title)s.%(ext)s"
    else:
        outtmpl = "%(title)s.%(ext)s"

    with tempfile.TemporaryDirectory() as tmp:
        options = {
            "outtmpl": outtmpl,
            "paths": {"home": output_dir, "temp": tmp},
            "noplaylist": not playlist,
            "ignoreerrors": playlist,
            "download_archive": str(Path(output_dir) / archive_name),
            "quiet": True,
            "no_warnings": True,
            "progress_hooks": [progress],
            "ffmpeg_location": imageio_ffmpeg.get_ffmpeg_exe(),
            **extra_options,
        }
        try:
            with YoutubeDL(options) as ydl:
                ydl.download([url])
            print("Success!")
            return True
        except DownloadError as e:
            print(f"\nDownload failed: {e}")
        except KeyboardInterrupt:
            print("\nCancelled by user.")
        except OSError as e:
            print(f"\nFile or disk error: {e}")
        except Exception as e:
            print(f"\nUnexpected error: {e}")
        finally:
            progress.close()
        return False
