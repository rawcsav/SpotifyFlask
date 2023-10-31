import os
import shutil
from datetime import datetime, timedelta

from sqlalchemy.sql.expression import func
from run import app
from app import db
from app.database import Songfull, CurrentGame, Archive
from app.util.game_util import trim_audio, download_song

CLIPS_DIR = os.getenv('CLIPS_DIR')
SONGS_PER_DAY = 1  # Number of songs to process daily


def preprocess_songs():
    # Set all tracks with a non-0 current value to have a "1" in their played column.
    Songfull.query.filter(Songfull.current != 0).update({'played': 1})

    # Initialize lists and constants
    selected_song_ids = []
    genres = ['General', 'Rock', 'Hip Hop']
    songs = []

    try:
        # Erase all existing CurrentGame data
        CurrentGame.query.delete()

        # For each genre, select three unique songs that haven't been played
        for i, genre in enumerate(genres, start=1):
            genre_songs = Songfull.query.filter(
                Songfull.genre.contains(genre),
                Songfull.played == 0,
                ~Songfull.id.in_(selected_song_ids)
            ).order_by(func.random()).limit(SONGS_PER_DAY).all()

            for song in genre_songs:
                songs.append(song)
                selected_song_ids.append(song.id)
                song.current = i  # Set current to 1, 2, or 3 depending on the genre

        # Download process remains the same
        for song in songs:
            input_path = os.path.join(CLIPS_DIR, f"{song.id}.mp3")

            for _ in range(3):
                if download_song(song.spotify_preview_url, input_path):
                    break
                print(f"Retry downloading for song id {song.id}")
            else:
                # Same logic, but using played column for new songs
                new_song = Songfull.query.filter(
                    Songfull.genre.contains(genre),
                    Songfull.played == 0,
                    ~Songfull.id.in_(selected_song_ids)
                ).order_by(func.random()).first()

                if new_song is None:
                    raise Exception(f"No more songs available in the genre {song.genre}")

                song = new_song
                input_path = os.path.join(CLIPS_DIR, f"{song.id}.mp3")
                if not download_song(song.spotify_preview_url, input_path):
                    raise Exception(f"Download failed for new song id {song.id}")

        # Add tracks to the archive for today's date
        today = datetime.utcnow().date()
        archive_entry = Archive(date_played=today,
                                general_track=songs[0].id,
                                rock_track=songs[1].id,
                                hiphop_track=songs[2].id)
        db.session.add(archive_entry)

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Preprocessing failed due to exception: {e}")


if __name__ == "__main__":
    with app.app_context():
        preprocess_songs()
    print("Songs preprocessed successfully!")
