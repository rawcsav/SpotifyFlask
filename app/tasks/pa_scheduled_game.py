import os
from datetime import datetime

from sqlalchemy.sql.expression import func

from app import db
from app.database import Songfull, Archive
from app.util.game_util import trim_audio
from run import app

CLIPS_DIR = os.getenv('CLIPS_DIR')


def archive_current_songs():
    """Move the current songs to the archive."""
    current_songs = Songfull.query.filter_by(current=True).all()

    for song in current_songs:
        archived_song = Archive(
            name=song.name,
            artist=song.artist,
            id=song.id,
            artist_id=song.artist_id,
            image_url=song.image_url,
            external_url=song.external_url,
            spotify_preview_url=song.spotify_preview_url,
            popularity=song.popularity,
            genre=song.genre,
            date=datetime.utcnow()
        )
        db.session.add(archived_song)

        db.session.delete(song)

    db.session.commit()


def preprocess_songs():
    with app.app_context():
        try:

            archive_current_songs()

            genres = ['general', 'rock', 'rap']
            songs = [Songfull.query.filter_by(genre=genre).order_by(func.random()).first() for genre in genres]

            for song in songs:
                try:
                    song.current = True
                    db.session.commit()
                except:
                    db.session.rollback()
                    raise

            for song in songs:
                for length in [0.1, 1, 3, 5, 10, 15, 30]:
                    input_path = os.path.join(CLIPS_DIR, f"{song.id}.mp3")
                    output_path = os.path.join(CLIPS_DIR, f"{song.id}_{length}.mp3")
                    trim_audio(input_path, output_path, length)

            print("Songs preprocessing completed successfully.")

        except Exception as e:
            print(f"Error during songs preprocessing: {e}")


if __name__ == "__main__":
    preprocess_songs()
