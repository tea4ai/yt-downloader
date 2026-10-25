import sys

import questionary

from audio import download_audio
from video import download_video
from common import DEFAULT_DIR

def ask(question):
    """Run a questionary prompt; exit cleanly if the user presses Ctrl+C."""
    answer = question.ask()  # returns None when canceled
    if answer is None:
        print("Bye!")
        sys.exit(0)
    return answer


def main():
    download = ask(
        questionary.select(
            "Format:",
            choices=[
                questionary.Choice("MP4 (video)", value=download_video),
                questionary.Choice("MP3 (audio only)", value=download_audio),
            ],
        )
    )

    playlist = ask(
        questionary.select(
            "Mode:",
            choices=[
                questionary.Choice("Single video", value=False),
                questionary.Choice("Whole playlist", value=True),
            ],
        )
    )

    url = ask(
        questionary.text(
            "Paste the URL:",
            validate=lambda t: t.strip().startswith(("http://", "https://"))
            or "The URL must start with http:// or https://",
        )
    ).strip().strip('"').strip("'")

    output_dir = ask(questionary.text("Output folder:", default=DEFAULT_DIR)).strip()

    download(url, output_dir or DEFAULT_DIR, playlist)


if __name__ == "__main__":
    main()
