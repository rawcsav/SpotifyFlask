import json

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


def add_artist_to_db(artist_data):
    new_artist = artist_sql(
        id=artist_data['id'],
        name=artist_data['name'],
        external_url=json.dumps(artist_data['external_urls']),
        followers=artist_data.get('followers', {'total': 0})['total'],
        genres=json.dumps(artist_data['genres']),
        href=artist_data['href'],
        images=json.dumps(artist_data['images']),
        popularity=artist_data['popularity'],
    )
    db.session.merge(new_artist)
    db.session.commit()


def get_or_fetch_artist_info(sp, artist_ids):
    if isinstance(artist_ids, str):
        artist_ids = [artist_ids]
    existing_artists = artist_sql.query.filter(artist_sql.id.in_(artist_ids)).all()
    existing_artist_ids = {artist.id: artist for artist in existing_artists}

    to_fetch = [artist_id for artist_id in artist_ids if artist_id not in existing_artist_ids]

    batch_size = 50

    for i in range(0, len(to_fetch), batch_size):
        batch = [x for x in to_fetch[i:i + batch_size] if x is not None]
        fetched_artists = sp.artists(batch)['artists']

        for artist in fetched_artists:
            new_artist = artist_sql(
                id=artist['id'],
                name=artist['name'],
                external_url=json.dumps(artist['external_urls']),
                followers=artist['followers']['total'],
                genres=json.dumps(artist['genres']),
                href=artist['href'],
                images=json.dumps(artist['images']),
                popularity=artist['popularity'],
            )
            existing_artist_ids[new_artist.id] = new_artist  # Update the existing artists dict
            db.session.merge(new_artist)
            db.session.commit()

    # Create the final dictionary
    final_artists = {}
    for artist_id in artist_ids:
        artist = existing_artist_ids.get(artist_id)  # Use .get() to avoid KeyError
        if artist:  # Check if artist exists in the dict
            final_artists[artist_id] = {
                'id': artist.id,
                'name': artist.name,
                'external_url': json.loads(artist.external_url),
                'followers': artist.followers,
                'genres': json.loads(artist.genres or '[]'),  # Handle null genres
                'href': artist.href,
                'images': json.loads(artist.images),
                'popularity': artist.popularity,
            }
    return final_artists


def get_or_fetch_audio_features(sp, track_ids):
    existing_features = features_sql.query.filter(features_sql.id.in_(track_ids)).all()
    existing_feature_ids = {feature.id: feature for feature in existing_features}

    to_fetch = [track_id for track_id in track_ids if track_id not in existing_feature_ids]
    if to_fetch:
        fetched_features = sp.audio_features(to_fetch)
        for feature in fetched_features:
            if feature:
                new_feature = features_sql(
                    id=feature['id'],
                    danceability=feature['danceability'],
                    energy=feature['energy'],
                    key=feature['key'],
                    loudness=feature['loudness'],
                    mode=feature['mode'],
                    speechiness=feature['speechiness'],
                    acousticness=feature['acousticness'],
                    instrumentalness=feature['instrumentalness'],
                    liveness=feature['liveness'],
                    valence=feature['valence'],
                    tempo=feature['tempo'],
                    time_signature=feature['time_signature'],
                )
                db.session.merge(new_feature)
                existing_feature_ids[feature['id']] = new_feature

        db.session.commit()

    final_features = {}
    for track_id in track_ids:
        feature = existing_feature_ids.get(track_id)
        if feature:
            final_features[track_id] = {
                'id': feature.id,
                'danceability': feature.danceability,
                'energy': feature.energy,
                'key': feature.key,
                'loudness': feature.loudness,
                'mode': feature.mode,
                'speechiness': feature.speechiness,
                'acousticness': feature.acousticness,
                'instrumentalness': feature.instrumentalness,
                'liveness': feature.liveness,
                'valence': feature.valence,
                'tempo': feature.tempo,
                'time_signature': feature.time_signature,
            }

    return final_features
