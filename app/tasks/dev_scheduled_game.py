import os
import shutil
from datetime import datetime, timedelta

from sqlalchemy.sql.expression import func
from run import app
from app import db
from app.database import Songfull, CurrentGame
from app.util.game_util import trim_audio, download_song

CLIPS_DIR = os.getenv('CLIPS_DIR')
SONGS_PER_DAY = 1  # Number of songs to process daily


def archive_current_songs():
    # Only archiving the last three songs
    current_songs = Songfull.query.filter(Songfull.current != 0).all()

    for song in current_songs:
        song.date_played = (datetime.utcnow() - timedelta(days=1)).date()

    db.session.commit()


def preprocess_songs():
    selected_song_ids = []
    genres = ['General', 'Rock', 'Hip Hop']
    songs = []

    try:
        archive_current_songs()
        CurrentGame.query.delete()

        # For each genre, select three unique songs
        for i, genre in enumerate(genres, start=1):
            genre_songs = Songfull.query.filter(
                Songfull.genre.contains(genre),
                Songfull.current == 0,  # Add this line
                ~Songfull.id.in_(selected_song_ids)
            ).order_by(func.random()).limit(SONGS_PER_DAY).all()

            for song in genre_songs:
                songs.append(song)
                selected_song_ids.append(song.id)
                song.current = i  # Set current to 1, 2, or 3 depending on the genre

        for song in songs:
            input_path = os.path.join(CLIPS_DIR, f"{song.id}.mp3")

            for _ in range(3):
                if download_song(song.spotify_preview_url, input_path):
                    break
                print(f"Retry downloading for song id {song.id}")
            else:
                print(f"Download failed for song id {song.id}. Selecting a new song.")
                new_song = Songfull.query.filter(
                    Songfull.genre.contains(genre),
                    Songfull.current == 0,  # Add this line
                    ~Songfull.id.in_(selected_song_ids)
                ).order_by(func.random()).first()

                if new_song is None:
                    raise Exception(f"No more songs available in the genre {song.genre}")

                song = new_song
                input_path = os.path.join(CLIPS_DIR, f"{song.id}.mp3")
                if not download_song(song.spotify_preview_url, input_path):
                    raise Exception(f"Download failed for new song id {song.id}")

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Preprocessing failed due to exception: {e}")


if __name__ == "__main__":
    with app.app_context():
        preprocess_songs()
    print("Songs preprocessed successfully!")
