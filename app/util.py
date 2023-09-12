import os
import shutil
from datetime import datetime, timedelta

from spotipy import Spotify

from app import config


def remove_directory(directory_path):
    if not os.path.exists(directory_path):
        print(f"The directory {directory_path} does not exist.")
        return
    shutil.rmtree(directory_path)
    print(f"The directory {directory_path} has been removed.")


def is_stale(path, threshold_minutes=180):
    mtime = datetime.fromtimestamp(os.path.getmtime(path))
    return datetime.utcnow() - mtime > timedelta(minutes=threshold_minutes)


def cleanup_path(path, threshold_minutes=180):
    for root, dirs, files in os.walk(path, topdown=False):  # `topdown=False` ensures we iterate from leaves to root
        for file in files:
            file_path = os.path.join(root, file)
            if is_stale(file_path, threshold_minutes):
                try:
                    os.remove(file_path)
                    print(f"Deleted stale file: {file_path}")
                except (OSError, Exception) as e:
                    print(f"Error deleting file {file_path}: {e}")

        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if is_stale(dir_path, threshold_minutes):
                try:
                    shutil.rmtree(dir_path)
                    print(f"Deleted stale directory: {dir_path}")
                except (OSError, Exception) as e:
                    print(f"Error deleting directory {dir_path}: {e}")


def scheduled_cleanup():
    cleanup_path('/tmp')
    cleanup_path(config.MAIN_USER_DIR)


def get_top_tracks(access_token, period):
    sp = Spotify(auth=access_token)
    return sp.current_user_top_tracks(time_range=period, limit=50)


def get_top_artists(access_token, period):
    sp = Spotify(auth=access_token)
    return sp.current_user_top_artists(time_range=period, limit=50)
