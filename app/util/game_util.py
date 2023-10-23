import subprocess
import requests
from app.database import Songfull, PastGame, db


def trim_audio(input_path, output_path, clip_length):
    subprocess.run([
        "ffmpeg", "-i", input_path, "-ss", "0", "-t", str(clip_length), output_path
    ])


def download_song(url, path):
    try:
        response = requests.get(url)
        response.raise_for_status()

        with open(path, 'wb') as f:
            f.write(response.content)
        return True
    except requests.exceptions.RequestException as e:
        print(f"Download failed due to exception: {e}")
        return False
