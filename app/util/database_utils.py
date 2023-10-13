import csv
import json
from datetime import datetime, timedelta

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def validate_artist_data(data):
    required_keys = ['id', 'name', 'external_urls', 'followers', 'genres', 'href', 'images', 'popularity']
    return all(key in data for key in required_keys)


def validate_audio_data(data):
    required_keys = ['id', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
                     'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature']
    return all(key in data for key in required_keys)


class UserData(db.Model):
    spotify_user_id = db.Column(db.String, primary_key=True, index=True)
    top_tracks = db.Column(db.PickleType, nullable=True)
    top_artists = db.Column(db.PickleType, nullable=True)
    all_artists_info = db.Column(db.PickleType, nullable=True)
    audio_features = db.Column(db.PickleType, nullable=True)
    genre_specific_data = db.Column(db.PickleType, nullable=True)
    sorted_genres_by_period = db.Column(db.PickleType, nullable=True)
    recent_tracks = db.Column(db.PickleType, nullable=True)
    playlist_info = db.Column(db.PickleType, nullable=True)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    api_key_encrypted = db.Column(db.String, nullable=True)
    isDarkMode = db.Column(db.Boolean, nullable=True)


class artist_sql(db.Model):
    id = db.Column(db.String, primary_key=True, index=True)
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
    id = db.Column(db.String, primary_key=True, index=True)
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
    id = db.Column(db.String, primary_key=True, index=True)
    name = db.Column(db.String)
    owner = db.Column(db.String)
    cover_art = db.Column(db.String)
    public = db.Column(db.Boolean)
    collaborative = db.Column(db.Boolean)
    total_tracks = db.Column(db.Integer)
    snapshot_id = db.Column(db.String)
    tracks = db.Column(db.PickleType)
    genre_counts = db.Column(db.PickleType)
    top_artists = db.Column(db.PickleType)
    feature_stats = db.Column(db.PickleType)
    temporal_stats = db.Column(db.PickleType)


class artgen_sql(db.Model):
    genre_name = db.Column(db.String, index=True, primary_key=True)
    parent_genre = db.Column(db.String)
    place_1 = db.Column(db.String)
    place_2 = db.Column(db.String)
    place_3 = db.Column(db.String)
    place_4 = db.Column(db.String)
    place_5 = db.Column(db.String)
    role_1 = db.Column(db.String)
    role_2 = db.Column(db.String)
    role_3 = db.Column(db.String)
    role_4 = db.Column(db.String)
    role_5 = db.Column(db.String)
    item_1 = db.Column(db.String)
    item_2 = db.Column(db.String)
    item_3 = db.Column(db.String)
    item_4 = db.Column(db.String)
    item_5 = db.Column(db.String)
    symbol_1 = db.Column(db.String)
    symbol_2 = db.Column(db.String)
    symbol_3 = db.Column(db.String)
    symbol_4 = db.Column(db.String)
    symbol_5 = db.Column(db.String)
    concept_1 = db.Column(db.String)
    concept_2 = db.Column(db.String)
    concept_3 = db.Column(db.String)
    concept_4 = db.Column(db.String)
    concept_5 = db.Column(db.String)
    event_1 = db.Column(db.String)
    event_2 = db.Column(db.String)
    event_3 = db.Column(db.String)
    event_4 = db.Column(db.String)
    event_5 = db.Column(db.String)


class artgenstyle_sql(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    art_style = db.Column(db.String(255), nullable=False)


class artgenurl_sql(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    genre_name = db.Column(db.String, nullable=True)
    playlist_id = db.Column(db.String, nullable=False)  # Added this line to store the playlist ID
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class genre_sql(db.Model):
    genre = db.Column(db.String, primary_key=True)
    sim_genres = db.Column(db.String, nullable=True)
    sim_weights = db.Column(db.String, nullable=True)
    opp_genres = db.Column(db.String, nullable=True)
    opp_weights = db.Column(db.String, nullable=True)
    spotify_url = db.Column(db.String, nullable=True)
    color = db.Column(db.String, nullable=True)
    font_size = db.Column(db.String, nullable=True)
    left = db.Column(db.String, nullable=True)
    top = db.Column(db.String, nullable=True)


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

    batch_size = 100

    if to_fetch:
        for i in range(0, len(to_fetch), batch_size):
            batch = to_fetch[i:i + batch_size]
            fetched_features = sp.audio_features(batch)

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

    final_features = {track_id: {
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
        'time_signature': feature.time_signature
    } for track_id, feature in existing_feature_ids.items()}

    return final_features


def load_data_into_artgen():
    with open('app/static/data/structured_genres_with_parents.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header row

        for row in reader:
            record = artgen_sql(
                genre_name=row[0],
                parent_genre=row[1],
                place_1=row[2],
                place_2=row[3],
                place_3=row[4],
                place_4=row[5],
                place_5=row[6],
                role_1=row[7],
                role_2=row[8],
                role_3=row[9],
                role_4=row[10],
                role_5=row[11],
                item_1=row[12],
                item_2=row[13],
                item_3=row[14],
                item_4=row[15],
                item_5=row[16],
                symbol_1=row[17],
                symbol_2=row[18],
                symbol_3=row[19],
                symbol_4=row[20],
                symbol_5=row[21],
                concept_1=row[22],
                concept_2=row[23],
                concept_3=row[24],
                concept_4=row[25],
                concept_5=row[26],
                event_1=row[27],
                event_2=row[28],
                event_3=row[29],
                event_4=row[30],
                event_5=row[31]
            )
            db.session.merge(record)

    db.session.commit()


def load_data_into_artgenstyle():
    with open('app/static/data/stylesgen.csv', 'r') as f:
        reader = csv.reader(f)

        for row in reader:
            record = artgenstyle_sql(
                id=row[0],
                art_style=row[1],
            )
            db.session.merge(record)

    db.session.commit()


def delete_expired_images_for_playlist(playlist_id):
    expiry_threshold = datetime.utcnow() - timedelta(hours=1)

    expired_images = artgenurl_sql.query.filter(
        artgenurl_sql.playlist_id == playlist_id,
        artgenurl_sql.timestamp <= expiry_threshold
    ).all()

    for image in expired_images:
        db.session.delete(image)

    db.session.commit()
    db.session.close()
