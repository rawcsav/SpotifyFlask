from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def validate_artist_data(data):
    required_keys = ['id', 'name', 'external_urls', 'followers', 'genres', 'href', 'images', 'popularity']
    return all(key in data for key in required_keys)


def validate_audio_data(data):
    required_keys = ['id', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
                     'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature']
    return all(key in data for key in required_keys)


class artist_sql(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    external_url = db.Column(db.String)
    followers = db.Column(db.Integer)
    genres = db.Column(db.String)
    href = db.Column(db.String)
    images = db.Column(db.String)
    popularity = db.Column(db.Integer)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class features_sql(db.Model):
    id = db.Column(db.String, primary_key=True)
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
