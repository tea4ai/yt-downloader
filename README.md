# YouTube downloader

Terminal menu for downloading `.mp3` and `.mp4` files from YouTube and other
sites supported by yt-dlp. Works for single videos and whole playlists.

## Setup

Requires Python 3.10+.

```
pip install -r requirements.txt
python app.py
```

ffmpeg is bundled through `imageio-ffmpeg`, so no separate install is needed.

## Usage

Run `python app.py` in a real terminal (the arrow-key menu doesn't work in some
IDE run windows), then choose format, mode, paste the URL and pick an output
folder. Files go to `downloads/` next to the scripts by default.

## Notes

- Finished downloads are recorded in `archive_mp3.txt` / `archive_mp4.txt` in
  the output folder, so they are skipped on later runs. Delete the file (or the
  line) to download something again.
- If downloads suddenly fail, update yt-dlp: `pip install -U yt-dlp`.

## Disclaimer

For content you have the right to download. Respect YouTube's Terms of Service
and copyright law.
