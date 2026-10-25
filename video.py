from common import run_download

VIDEO_FORMAT = (
    "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080][ext=mp4]"
    "/bv*[height<=1080]+ba/b[height<=1080]"
)


def download_video(url: str, output_dir: str = "yt_downloader/downloads", playlist: bool = False) -> bool:
    extra = {
        "format": VIDEO_FORMAT,
        "merge_output_format": "mp4",
    }
    return run_download(url, output_dir, playlist, extra, "archive_mp4.txt")