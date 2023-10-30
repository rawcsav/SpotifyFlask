from datetime import datetime
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, validates

db = SQLAlchemy()


class UserData(db.Model):
    spotify_user_id = db.Column(db.VARCHAR(255), primary_key=True, index=True)
    top_tracks = db.Column(db.JSON, nullable=True)
    top_artists = db.Column(db.JSON, nullable=True)
    all_artists_info = db.Column(db.JSON, nullable=True)
    audio_features = db.Column(db.JSON, nullable=True)
    genre_specific_data = db.Column(db.JSON, nullable=True)
    sorted_genres_by_period = db.Column(db.JSON, nullable=True)
    recent_tracks = db.Column(db.JSON, nullable=True)
    playlist_info = db.Column(db.JSON, nullable=True)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    api_key_encrypted = db.Column(db.VARCHAR(255), nullable=True)
    isDarkMode = db.Column(db.Boolean, nullable=True)


class artist_sql(db.Model):
    id = db.Column(db.String(100), primary_key=True, index=True)
    name = db.Column(db.VARCHAR(255))
    external_url = db.Column(db.VARCHAR(255))
    followers = db.Column(db.Integer)
    genres = db.Column(db.VARCHAR(255))
    images = db.Column(db.JSON)
    popularity = db.Column(db.Integer)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class features_sql(db.Model):
    id = db.Column(db.VARCHAR(255), primary_key=True, index=True)
    danceability = db.Column(db.Float)
    energy = db.Column(db.Float)
    key = db.Column(db.Integer)
    loudness = db.Column(db.Float)
    mode = db.Column(db.Integer)
    speechiness = db.Column(db.Float)
    acousticness = db.Column(db.Float)
    instrumentalness = db.Column(db.Float)
    liveness = db.Column(db.Float)
    valence = db.Column(db.Float)
    tempo = db.Column(db.Float)
    time_signature = db.Column(db.Integer)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class playlist_sql(db.Model):
    id = db.Column(db.VARCHAR(255), primary_key=True, index=True)
    name = db.Column(db.VARCHAR(255))
    owner = db.Column(db.VARCHAR(255))
    cover_art = db.Column(db.VARCHAR(255))
    public = db.Column(db.Boolean)
    collaborative = db.Column(db.Boolean)
    total_tracks = db.Column(db.Integer)
    snapshot_id = db.Column(db.VARCHAR(255))
    tracks = db.Column(db.JSON)
    genre_counts = db.Column(db.JSON)
    top_artists = db.Column(db.JSON)
    feature_stats = db.Column(db.JSON)
    temporal_stats = db.Column(db.JSON)


class artgen_sql(db.Model):
    genre_name = db.Column(db.VARCHAR(50), db.ForeignKey('genre_sql.genre'), primary_key=True)
    place_1 = db.Column(db.TEXT)
    place_2 = db.Column(db.TEXT)
    place_3 = db.Column(db.TEXT)
    place_4 = db.Column(db.TEXT)
    place_5 = db.Column(db.TEXT)
    role_1 = db.Column(db.TEXT)
    role_2 = db.Column(db.TEXT)
    role_3 = db.Column(db.TEXT)
    role_4 = db.Column(db.TEXT)
    role_5 = db.Column(db.TEXT)
    item_1 = db.Column(db.TEXT)
    item_2 = db.Column(db.TEXT)
    item_3 = db.Column(db.TEXT)
    item_4 = db.Column(db.TEXT)
    item_5 = db.Column(db.TEXT)
    symbol_1 = db.Column(db.TEXT)
    symbol_2 = db.Column(db.TEXT)
    symbol_3 = db.Column(db.TEXT)
    symbol_4 = db.Column(db.TEXT)
    symbol_5 = db.Column(db.TEXT)
    event_1 = db.Column(db.TEXT)
    event_2 = db.Column(db.TEXT)
    event_3 = db.Column(db.TEXT)
    event_4 = db.Column(db.TEXT)
    event_5 = db.Column(db.TEXT)
    genre = relationship("genre_sql", back_populates="artgen")


class artgenstyle_sql(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    art_style = db.Column(db.String(255), nullable=False)


class artgenurl_sql(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.VARCHAR(255), nullable=False)
    genre_name = db.Column(db.VARCHAR(255), nullable=True)
    art_style = db.Column(db.VARCHAR(255), nullable=True)
    random_attribute = db.Column(db.VARCHAR(255), nullable=True)
    prompt = db.Column(db.VARCHAR(255), nullable=True)
    playlist_id = db.Column(db.VARCHAR(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class genre_sql(db.Model):
    genre = db.Column(db.VARCHAR(50), primary_key=True)
    sim_genres = db.Column(db.TEXT, nullable=True)
    sim_weights = db.Column(db.TEXT, nullable=True)
    opp_genres = db.Column(db.TEXT, nullable=True)
    opp_weights = db.Column(db.TEXT, nullable=True)
    spotify_url = db.Column(db.TEXT, nullable=True)
    color_hex = db.Column(db.TEXT, nullable=True)
    color_rgb = db.Column(db.TEXT, nullable=True)
    x = db.Column(db.Float, nullable=True)
    y = db.Column(db.Float, nullable=True)
    closest_stat_genres = db.Column(db.TEXT, nullable=True)
    artgen = relationship("artgen_sql", back_populates="genre")


class Songfull(db.Model):
    name = db.Column(db.String(150), nullable=False)
    artist = db.Column(db.String(150), nullable=False)
    id = db.Column(db.String(150), primary_key=True)
    artist_id = db.Column(db.String(150), nullable=False)
    album = db.Column(db.String(150))  # added
    release = db.Column(db.String(4))  # added
    image_url = db.Column(db.String(250))
    external_url = db.Column(db.String(250))
    spotify_preview_url = db.Column(db.String(250), nullable=False)
    popularity = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String(50), nullable=False, index=True)
    current = db.Column(db.SmallInteger, default=0)
    played = db.Column(db.SmallInteger, default=0)

    def __repr__(self):
        return f"<Song {self.name} by {self.artist}>"


class Archive(db.Model):
    date_played = db.Column(db.Date, primary_key=True, nullable=False, index=True)
    general_track = db.Column(db.String(150), db.ForeignKey('songfull.id'))  # Added
    rock_track = db.Column(db.String(150), db.ForeignKey('songfull.id'))  # Added
    hiphop_track = db.Column(db.String(150), db.ForeignKey('songfull.id'))  # Added
    past_games = db.relationship('PastGame', backref='archive', lazy=True)

    general_song = db.relationship('Songfull', foreign_keys=[general_track])
    rock_song = db.relationship('Songfull', foreign_keys=[rock_track])
    hiphop_song = db.relationship('Songfull', foreign_keys=[hiphop_track])

    def __repr__(self):
        return f"<Archive on {self.date_played}>"


class PastGame(db.Model):
    user_id_or_session = db.Column(db.String(100), primary_key=True, nullable=False)  # replaces the user_id column
    date = db.Column(db.Date, nullable=False, index=True)
    attempts_made_general = db.Column(db.Integer, default=0)
    attempts_made_rock = db.Column(db.Integer, default=0)
    attempts_made_hiphop = db.Column(db.Integer, default=0)
    correct_guess_general = db.Column(db.Boolean, default=False)
    correct_guess_rock = db.Column(db.Boolean, default=False)
    correct_guess_hiphop = db.Column(db.Boolean, default=False)
    archive_date = db.Column(db.Date, db.ForeignKey('archive.date_played'), nullable=False)

    def __repr__(self):
        return f"<PastGame on {self.date} for user/session {self.user_id_or_session}>"

    @validates('attempts_made_general', 'attempts_made_rock', 'attempts_made_hiphop')
    def validate_attempts(self, key, value):
        if value < 0 or value > 6:
            raise ValueError(f"{key} should be between 0 and 6 inclusive.")
        return value


class CurrentGame(db.Model):
    user_id_or_session = db.Column(db.String(100), primary_key=True, nullable=False)
    current_genre = db.Column(db.String(50), default='General')
    guesses_left = db.Column(db.Integer, default=6)
    date = db.Column(db.Date, nullable=False, default=func.current_date())
    archive_date = db.Column(db.Date, db.ForeignKey('archive.date_played'), nullable=False)
    archive = db.relationship('Archive', backref='games')

    def __repr__(self):
        return f"<CurrentGame on {self.date} for user/session {self.user_id_or_session}>"

    @validates('guesses_left')
    def validate_guesses_left(self, key, value):
        if value < 0:
            raise ValueError(f"{key} should not be less than 0.")
        return value
