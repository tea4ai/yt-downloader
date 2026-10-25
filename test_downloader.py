from pathlib import Path

import pytest
from yt_dlp.utils import DownloadError

import audio
import common
import video


# ---------- helpers ----------

class FakeYDL:
    """Stands in for yt_dlp.YoutubeDL so no network is used."""
    last_options = None
    retcode = 0
    error = None

    def __init__(self, options):
        FakeYDL.last_options = options

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def download(self, urls):
        if FakeYDL.error:
            raise FakeYDL.error
        return FakeYDL.retcode


@pytest.fixture(autouse=True)
def reset_fake():
    FakeYDL.last_options = None
    FakeYDL.retcode = 0
    FakeYDL.error = None


class FakeBar:
    """Stands in for tqdm."""
    def __init__(self, **kwargs):
        self.total = kwargs.get("total")
        self.n = 0

    def update(self, amount):
        self.n += amount

    def close(self):
        pass


# ---------- DEFAULT_DIR ----------

def test_default_dir_is_absolute_downloads_folder():
    assert Path(common.DEFAULT_DIR).is_absolute()
    assert Path(common.DEFAULT_DIR).name == "downloads"


# ---------- audio.py / video.py ----------

def _capture(monkeypatch, module):
    captured = {}

    def fake_run(url, output_dir, playlist, extra, archive):
        captured.update(
            url=url, output_dir=output_dir, playlist=playlist,
            extra=extra, archive=archive,
        )
        return True

    monkeypatch.setattr(module, "run_download", fake_run)
    return captured


def test_audio_requests_mp3_with_own_archive(monkeypatch):
    captured = _capture(monkeypatch, audio)

    assert audio.download_audio("https://example.com/v", "out", True) is True

    assert captured["extra"]["format"] == "bestaudio/best"
    codecs = [p.get("preferredcodec") for p in captured["extra"]["postprocessors"]]
    assert "mp3" in codecs
    assert captured["archive"] == "archive_mp3.txt"
    assert captured["playlist"] is True


def test_video_requests_mp4_with_own_archive(monkeypatch):
    captured = _capture(monkeypatch, video)

    assert video.download_video("https://example.com/v", "out", False) is True

    assert captured["extra"]["merge_output_format"] == "mp4"
    assert "1080" in captured["extra"]["format"]
    assert captured["archive"] == "archive_mp4.txt"
    assert captured["playlist"] is False


# ---------- run_download ----------

def test_run_download_success_sets_playlist_options(monkeypatch, tmp_path):
    monkeypatch.setattr(common, "YoutubeDL", FakeYDL)

    ok = common.run_download("https://example.com/v", str(tmp_path), True, {}, "a.txt")

    assert ok is True
    opts = FakeYDL.last_options
    assert opts["noplaylist"] is False
    assert opts["ignoreerrors"] is True
    assert "playlist_index" in opts["outtmpl"]
    assert opts["download_archive"] == str(tmp_path / "a.txt")


def test_run_download_single_video_options(monkeypatch, tmp_path):
    monkeypatch.setattr(common, "YoutubeDL", FakeYDL)

    common.run_download("https://example.com/v", str(tmp_path), False, {}, "a.txt")

    opts = FakeYDL.last_options
    assert opts["noplaylist"] is True
    assert opts["outtmpl"] == "%(title)s.%(ext)s"


def test_run_download_creates_output_folder(monkeypatch, tmp_path):
    monkeypatch.setattr(common, "YoutubeDL", FakeYDL)
    target = tmp_path / "new" / "folder"

    common.run_download("https://example.com/v", str(target), False, {}, "a.txt")

    assert target.is_dir()


def test_run_download_merges_extra_options(monkeypatch, tmp_path):
    monkeypatch.setattr(common, "YoutubeDL", FakeYDL)

    common.run_download("https://example.com/v", str(tmp_path), False, {"format": "x"}, "a.txt")

    assert FakeYDL.last_options["format"] == "x"


def test_run_download_returns_false_on_download_error(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(common, "YoutubeDL", FakeYDL)
    FakeYDL.error = DownloadError("Video unavailable")

    ok = common.run_download("https://example.com/v", str(tmp_path), False, {}, "a.txt")

    assert ok is False
    assert "Download failed" in capsys.readouterr().out


def test_run_download_returns_false_on_ctrl_c(monkeypatch, tmp_path):
    monkeypatch.setattr(common, "YoutubeDL", FakeYDL)
    FakeYDL.error = KeyboardInterrupt()

    assert common.run_download("https://example.com/v", str(tmp_path), False, {}, "a.txt") is False


# ---------- ProgressBar ----------

def test_progress_bar_counts_increments_not_totals(monkeypatch):
    monkeypatch.setattr(common, "tqdm", FakeBar)
    progress = common.ProgressBar()

    progress({"status": "downloading", "filename": "x.mp4",
              "total_bytes": 100, "downloaded_bytes": 30})
    progress({"status": "downloading", "filename": "x.mp4",
              "total_bytes": 100, "downloaded_bytes": 80})

    assert progress.bar.n == 80   # not 110


def test_progress_bar_closes_when_finished(monkeypatch):
    monkeypatch.setattr(common, "tqdm", FakeBar)
    progress = common.ProgressBar()

    progress({"status": "downloading", "filename": "x.mp4",
              "total_bytes": 100, "downloaded_bytes": 10})
    progress({"status": "finished"})

    assert progress.bar is None