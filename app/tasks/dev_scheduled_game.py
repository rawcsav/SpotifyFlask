import os
import shutil
from datetime import datetime
from sqlalchemy.sql.expression import func, or_
from app.util.database_utils import Songfull, Archive, db
from app.util.game_util import trim_audio, download_song

CLIPS_DIR = os.getenv('CLIPS_DIR')


def archive_current_songs():
    current_songs = Songfull.query.filter_by(current=True).all()

    for song in current_songs:
        # Move song to the Archive
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

        # Delete the song from the Songfull table
        db.session.delete(song)

    db.session.commit()


def preprocess_songs():
    archive_current_songs()

    selected_song_ids = []  # To keep track of songs that have already been selected
    genres = ['General', 'Rock', 'Hip Hop']
    songs = []

    for genre in genres:
        # Get a song that contains the genre and hasn't been selected yet
        song = Songfull.query.filter(
            Songfull.genre.contains(genre),
            ~Songfull.id.in_(selected_song_ids)  # Exclude already selected songs
        ).order_by(func.random()).first()

        if song:
            songs.append(song)
            selected_song_ids.append(song.id)

    # Mark these songs as the current songs
    for song in songs:
        try:
            song.current = True
            db.session.commit()
        except:
            db.session.rollback()
            raise

        input_path = os.path.join(CLIPS_DIR, f"{song.id}.mp3")
        download_song(song.spotify_preview_url, input_path)

        # Process the song clips
        for length in [0.1, 1, 3, 5, 10, 15, 30]:
            length_str = '01' if length == 0.1 else str(int(length))
            output_path = os.path.join(CLIPS_DIR, f"{song.id}_{length_str}.mp3")

            if length != 30:
                trim_audio(input_path, output_path, length)
            else:
                shutil.copy(input_path, output_path)
        os.remove(input_path)  # Delete the original file


if __name__ == "__main__":
    preprocess_songs()
    print("Songs preprocessed successfully!")
