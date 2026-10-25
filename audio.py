from common import DEFAULT_DIR, run_download


def download_audio(url: str, output_dir: str = DEFAULT_DIR, playlist: bool = False) -> bool:
    extra = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            },
            {"key": "FFmpegMetadata"},
        ],
    }
    return run_download(url, output_dir, playlist, extra, "archive_mp3.txt")
