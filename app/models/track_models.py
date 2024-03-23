from datetime import datetime

from app import db
from app.models.mixins import TimestampMixin, generate_uuid
from app.models.artist_models import Artist


class TrackArtistAssociation(db.Model):
    __tablename__ = "track_artist_association"
    track_id = db.Column(db.String(255), db.ForeignKey("tracks.id"), primary_key=True)
    artist_id = db.Column(db.String(255), db.ForeignKey("artists.id"), primary_key=True)


class Track(db.Model, TimestampMixin):
    __tablename__ = "tracks"
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    album_id = db.Column(db.String(255), db.ForeignKey("albums.id"))
    explicit = db.Column(db.Boolean, nullable=False)
    is_local = db.Column(db.Boolean, nullable=False)
    duration_ms = db.Column(db.Integer, nullable=False)
    external_url = db.Column(db.String(255))
    popularity = db.Column(db.Integer)
    album = db.relationship("Album", back_populates="tracks")
    artists = db.relationship("Artist", secondary="track_artist_association", back_populates="tracks")

    def to_dict(self):
        data = self.__dict__.copy()
        data.pop("_sa_instance_state", None)
        return data

    @classmethod
    def from_spotify_track(cls, track_info):
        print("In track method")
        track = cls.query.get(track_info["id"])
        if not track:
            track = cls(id=track_info["id"])
        track.name = track_info["name"]
        track.explicit = track_info["explicit"]
        track.is_local = False  # Assuming fetched tracks are not local
        track.duration_ms = track_info["duration_ms"]
        track.external_url = track_info["external_urls"]["spotify"]
        track.popularity = track_info["popularity"]
        album = Album.from_spotify_album(track_info["album"])
        track.album_id = album.id
        track.artists = Artist.from_spotify_artists(track_info["artists"])
        db.session.add(track)
        db.session.commit()
        return track

    @classmethod
    def from_spotify_tracks(cls, tracks_info):
        processed_tracks = []
        for track_info in tracks_info:
            try:
                track = cls.from_spotify_track(track_info)
                processed_tracks.append(track)
            except Exception as e:
                print(f"Failed to process track {track_info['id']}: {e}")
        return processed_tracks


class Album(db.Model, TimestampMixin):
    __tablename__ = "albums"
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    release_date = db.Column(db.DateTime)
    release_date_precision = db.Column(db.String(10))
    cover_art_url = db.Column(db.String(255))
    tracks = db.relationship("Track", back_populates="album")

    def to_dict(self):
        data = self.__dict__.copy()
        data.pop("_sa_instance_state", None)
        return data

    @classmethod
    def from_spotify_album(cls, album_info):
        album = cls.query.get(album_info["id"])
        if not album:
            album = cls(id=album_info["id"])
        album.name = album_info["name"]

        # Adjust date parsing based on release_date_precision
        release_date = album_info.get("release_date")
        release_date_precision = album_info.get("release_date_precision")
        if release_date:
            if release_date_precision == "year":
                album.release_date = datetime.strptime(release_date, "%Y")
            elif release_date_precision == "month":
                album.release_date = datetime.strptime(release_date, "%Y-%m")
            elif release_date_precision == "day":
                album.release_date = datetime.strptime(release_date, "%Y-%m-%d")
            else:
                album.release_date = None
        else:
            album.release_date = None

        album.release_date_precision = release_date_precision
        album.cover_art_url = album_info["images"][0]["url"] if album_info.get("images") else None

        db.session.add(album)
        db.session.commit()
        return album


class AudioFeature(db.Model, TimestampMixin):
    __tablename__ = "audio_features"
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    track_id = db.Column(db.String(255), db.ForeignKey("tracks.id"))
    key = db.Column(db.Integer)
    mode = db.Column(db.Integer)
    tempo = db.Column(db.Float)
    energy = db.Column(db.Float)
    valence = db.Column(db.Float)
    liveness = db.Column(db.Float)
    loudness = db.Column(db.Float)
    speechiness = db.Column(db.Float)
    acousticness = db.Column(db.Float)
    danceability = db.Column(db.Float)
    time_signature = db.Column(db.Integer)
    instrumentalness = db.Column(db.Float)
    track = db.relationship("Track")

    @classmethod
    def from_spotify_features(cls, track_id, features_info):
        audio_feature = cls.query.filter_by(track_id=track_id).first()
        if not audio_feature:
            audio_feature = cls(track_id=track_id)

        audio_feature.key = features_info.get("key")
        audio_feature.mode = features_info.get("mode")
        audio_feature.tempo = features_info.get("tempo")
        audio_feature.energy = features_info.get("energy")
        audio_feature.valence = features_info.get("valence")
        audio_feature.liveness = features_info.get("liveness")
        audio_feature.loudness = features_info.get("loudness")
        audio_feature.speechiness = features_info.get("speechiness")
        audio_feature.acousticness = features_info.get("acousticness")
        audio_feature.danceability = features_info.get("danceability")
        audio_feature.time_signature = features_info.get("time_signature")
        audio_feature.instrumentalness = features_info.get("instrumentalness")

        db.session.add(audio_feature)

        def to_dict(self):
            data = self.__dict__.copy()
            data.pop("_sa_instance_state", None)
            return data

        return audio_feature
