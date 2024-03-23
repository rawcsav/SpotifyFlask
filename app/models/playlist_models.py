from app import db
from app.models.mixins import TimestampMixin
from app.models.track_models import Track


class Playlist(db.Model, TimestampMixin):
    __tablename__ = "playlists"
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    owner = db.Column(db.String(255))
    user_id = db.Column(db.String(255), db.ForeignKey("users.id"), index=True)
    public = db.Column(db.Boolean)
    collaborative = db.Column(db.Boolean)
    cover_art = db.Column(db.String(255))
    followers = db.Column(db.Integer, default=0)
    total_tracks = db.Column(db.Integer, default=0)
    snapshot_id = db.Column(db.String(255))

    def to_dict(self):
        data = self.__dict__.copy()
        data.pop("_sa_instance_state", None)
        return data

    @classmethod
    def from_spotify_playlist(cls, user_id, playlist_info):
        playlist = cls.query.get(playlist_info["id"])
        if not playlist:
            playlist = cls(id=playlist_info["id"])

        playlist.name = playlist_info["name"]
        playlist.owner = playlist_info["owner"]["id"]
        playlist.user_id = user_id
        playlist.public = playlist_info["public"]
        playlist.collaborative = playlist_info["collaborative"]
        playlist.cover_art = playlist_info["images"][0]["url"] if playlist_info.get("images") else None
        playlist.followers = playlist_info["followers"]["total"] if playlist_info.get("followers") else 0
        playlist.total_tracks = playlist_info["tracks"]["total"]
        playlist.snapshot_id = playlist_info["snapshot_id"]

        db.session.add(playlist)
        db.session.commit()

        return playlist


class PlaylistTrack(db.Model, TimestampMixin):
    __tablename__ = "playlist_track"
    playlist_id = db.Column(db.String(255), db.ForeignKey("playlists.id"), primary_key=True)
    track_id = db.Column(db.String(255), db.ForeignKey("tracks.id"), primary_key=True)
    track_order = db.Column(db.Integer)
    added_at = db.Column(db.DateTime)
    track = db.relationship("Track")

    def to_dict(self):
        data = self.__dict__.copy()
        data.pop("_sa_instance_state", None)
        return data

    @classmethod
    def add_track_to_playlist(cls, playlist_id, track_info, track_order, added_at):
        track = Track.from_spotify_track(track_info)
        playlist_track = cls.query.filter_by(playlist_id=playlist_id, track_id=track.id).first()
        if not playlist_track:
            playlist_track = cls(playlist_id=playlist_id, track_id=track.id)

        playlist_track.track_order = track_order
        playlist_track.added_at = added_at

        db.session.add(playlist_track)
        db.session.commit()


class PlaylistTemporalStats(db.Model, TimestampMixin):
    __tablename__ = "playlist_temporal_stats"
    playlist_id = db.Column(db.String(255), db.ForeignKey("playlists.id"), primary_key=True)
    newest_track_id = db.Column(db.String(255), db.ForeignKey("tracks.id"))
    oldest_track_id = db.Column(db.String(255), db.ForeignKey("tracks.id"))

    def to_dict(self):
        data = self.__dict__.copy()
        data.pop("_sa_instance_state", None)
        return data


class PlaylistYearlyStats(db.Model, TimestampMixin):
    __tablename__ = "playlist_yearly_decade_stats"
    playlist_id = db.Column(db.String(255), db.ForeignKey("playlists.id"), primary_key=True)
    year_label = db.Column(db.String(50), primary_key=True)
    track_count = db.Column(db.Integer)

    def to_dict(self):
        data = self.__dict__.copy()
        data.pop("_sa_instance_state", None)
        return data


class PlaylistFeatureStats(db.Model, TimestampMixin):
    __tablename__ = "playlist_feature_stats"
    playlist_id = db.Column(db.String(255), db.ForeignKey("playlists.id"), primary_key=True)
    feature = db.Column(db.String(50), primary_key=True)
    avg_value = db.Column(db.Float)
    max_value = db.Column(db.Float)
    min_value = db.Column(db.Float)
    total_value = db.Column(db.Float)

    def to_dict(self):
        data = self.__dict__.copy()
        data.pop("_sa_instance_state", None)
        return data


class PlaylistGenreStats(db.Model, TimestampMixin):
    __tablename__ = "playlist_genre_stats"
    playlist_id = db.Column(db.String(255), db.ForeignKey("playlists.id"), primary_key=True)
    genre_id = db.Column(db.String(255), db.ForeignKey("genres.name"), primary_key=True)
    track_count = db.Column(db.Integer)

    def to_dict(self):
        data = self.__dict__.copy()
        data.pop("_sa_instance_state", None)
        return data


class PlaylistTopArtists(db.Model, TimestampMixin):
    __tablename__ = "playlist_top_artists"
    playlist_id = db.Column(db.String(255), db.ForeignKey("playlists.id"), primary_key=True)
    artist_id = db.Column(db.String(255), db.ForeignKey("artists.id"), primary_key=True)
    track_count = db.Column(db.Integer)

    def to_dict(self):
        data = self.__dict__.copy()
        data.pop("_sa_instance_state", None)
        return data
