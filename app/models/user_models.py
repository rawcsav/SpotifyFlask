from app import db
from app.models.mixins import TimestampMixin, generate_uuid


class User(db.Model, TimestampMixin):
    __tablename__ = "users"
    id = db.Column(db.String(255), primary_key=True)
    user_name = db.Column(db.String(255), nullable=False)
    profile_img_url = db.Column(db.String(255))
    followers = db.Column(db.Integer, default=0)
    account_type = db.Column(db.Enum("free", "premium"), nullable=False)
    api_key = db.Column(db.String(255))
    dark_mode = db.Column(db.Boolean, default=False)
    playlists = db.relationship("Playlist", backref="user", lazy="dynamic")
    last_active = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        data = self.__dict__.copy()
        data.pop("_sa_instance_state", None)
        return data


class UserTrackStats(db.Model, TimestampMixin):
    __tablename__ = "user_track_stats"
    id = db.Column(db.String(255), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(255), db.ForeignKey("users.id"))
    track_id = db.Column(db.String(255), db.ForeignKey("tracks.id"))
    period = db.Column(db.Enum("long_term", "medium_term", "short_term"))
    popularity_score = db.Column(db.Integer)

    def to_dict(self):
        data = self.__dict__.copy()
        data.pop("_sa_instance_state", None)
        return data


class UserArtistStats(db.Model, TimestampMixin):
    __tablename__ = "user_artist_stats"
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(255), db.ForeignKey("users.id"))  # Ensure this matches the 'id' column in 'users'
    artist_id = db.Column(db.String(255), db.ForeignKey("artists.id"))
    period = db.Column(db.Enum("long_term", "medium_term", "short_term"))
    popularity_score = db.Column(db.Integer)

    def to_dict(self):
        data = self.__dict__.copy()
        data.pop("_sa_instance_state", None)
        return data


class UserGenreStats(db.Model, TimestampMixin):
    __tablename__ = "user_genre_stats"
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(255), db.ForeignKey("users.id"))
    genre_id = db.Column(db.String(255), db.ForeignKey("genres.name"))
    period = db.Column(db.Enum("long_term", "medium_term", "short_term"))
    popularity_score = db.Column(db.Integer)

    def to_dict(self):
        data = self.__dict__.copy()
        data.pop("_sa_instance_state", None)
        return data


class UserGenreTopTracks(db.Model, TimestampMixin):
    __tablename__ = "user_genre_top_tracks"
    user_id = db.Column(db.String(255), db.ForeignKey("users.id"), primary_key=True)
    genre_id = db.Column(db.String(255), db.ForeignKey("genres.name"), primary_key=True)
    track_id = db.Column(db.String(255), db.ForeignKey("tracks.id"), primary_key=True)
    period = db.Column(db.Enum("long_term", "medium_term", "short_term"), primary_key=True)

    def to_dict(self):
        data = self.__dict__.copy()
        data.pop("_sa_instance_state", None)
        return data


class UserGenreTopArtists(db.Model, TimestampMixin):
    __tablename__ = "user_genre_top_artists"
    user_id = db.Column(db.String(255), db.ForeignKey("users.id"), primary_key=True)
    genre_id = db.Column(db.String(255), db.ForeignKey("genres.name"), primary_key=True)
    artist_id = db.Column(db.String(255), db.ForeignKey("artists.id"), primary_key=True)
    period = db.Column(db.Enum("long_term", "medium_term", "short_term"), primary_key=True)

    def to_dict(self):
        data = self.__dict__.copy()
        data.pop("_sa_instance_state", None)
        return data


class RecentlyPlayedTracks(db.Model, TimestampMixin):
    __tablename__ = "recently_played_tracks"
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(255), db.ForeignKey("users.id"))
    track_id = db.Column(db.String(255), db.ForeignKey("tracks.id"))
    played_at = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        data = self.__dict__.copy()
        data.pop("_sa_instance_state", None)
        return data
