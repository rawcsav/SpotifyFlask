import json

from flask import session
from sqlalchemy.exc import SQLAlchemyError
from app import db
from app.models.mixins import TimestampMixin
from modules.auth.auth_util import init_session_client


class GenreArtistAssociation(db.Model):
    __tablename__ = "genre_artist_association"
    genre_id = db.Column(db.String(255), db.ForeignKey("genres.name"), primary_key=True)
    artist_id = db.Column(db.String(255), db.ForeignKey("artists.id"), primary_key=True)


class Artist(db.Model, TimestampMixin):
    __tablename__ = "artists"
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    popularity = db.Column(db.Integer)
    followers = db.Column(db.Integer, default=0)
    external_url = db.Column(db.String(255))
    image_url = db.Column(db.String(255))
    tracks = db.relationship("Track", secondary="track_artist_association", back_populates="artists")
    genres = db.relationship("Genre", secondary="genre_artist_association", back_populates="artists")

    def to_dict(self):
        data = self.__dict__.copy()
        data.pop("_sa_instance_state", None)
        return data

    @classmethod
    def from_spotify_artists(cls, artists_info):
        sp, error = init_session_client(session)
        if error:
            return json.dumps(error), 401
        updated_artists = []
        for artist_info in artists_info:
            try:
                artist = cls.query.get(artist_info["id"])
                if not artist:
                    artist = cls(id=artist_info["id"])
                if artist_info.get("popularity") is None and artist_info.get("followers", {}).get("total") is None:
                    artist_info = sp.artist(artist_info["id"])
                artist.name = artist_info["name"]
                artist.popularity = artist_info.get("popularity", 0)
                artist.followers = artist_info.get("followers", {}).get("total", 0)
                artist.external_url = artist_info.get("external_urls", {}).get("spotify")
                artist.image_url = artist_info.get("images")[0]["url"] if artist_info.get("images") else None
                db.session.add(artist)
                db.session.flush()  # Flush to assign an ID without committing the transaction
                if "genres" in artist_info:
                    for genre_name in artist_info["genres"]:
                        genre = Genre.query.filter_by(name=genre_name).first()
                        if not genre:
                            genre = Genre(name=genre_name)
                            db.session.add(genre)
                            db.session.flush()
                        if genre not in artist.genres:
                            artist.genres.append(genre)
                updated_artists.append(artist)
            except SQLAlchemyError as e:
                db.session.rollback()
                print(f"Failed to update artist {artist_info['id']}: {e}")
                continue
            db.session.commit()
        return updated_artists


class Genre(db.Model, TimestampMixin):
    __tablename__ = "genres"
    name = db.Column(db.String(255), primary_key=True, unique=True, nullable=False)
    artists = db.relationship("Artist", secondary="genre_artist_association", back_populates="genres")
