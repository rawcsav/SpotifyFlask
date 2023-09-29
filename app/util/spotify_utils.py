import json
from collections import defaultdict
from datetime import datetime
from flask import jsonify
from spotipy import Spotify
from spotipy.client import SpotifyException

from app import config
from app.routes.auth import refresh
from app.util.database_utils import db, artist_sql, features_sql, add_artist_to_db

from sqlalchemy.exc import IntegrityError

FEATURES = config.AUDIO_FEATURES


def get_top_tracks(sp, period):
    return sp.current_user_top_tracks(time_range=period, limit=50)


def get_top_artists(sp, period):
    return sp.current_user_top_artists(time_range=period, limit=50)


def get_audio_features_for_tracks(sp, track_ids):
    features = {}
    for i in range(0, len(track_ids), 100):
        batch = track_ids[i: i + 100]
        batch_features = sp.audio_features(batch)
        for feature in batch_features:
            if feature:
                features[feature["id"]] = feature
    return features


def get_genre_counts_from_artists_and_tracks(top_artists, top_tracks, all_artists_info):
    genre_counts = defaultdict(int)

    for artist in top_artists["items"]:
        for genre in artist["genres"]:
            genre_counts[genre] += 1

    for track in top_tracks["items"]:
        for artist in track["artists"]:
            artist_info = all_artists_info.get(artist["id"])
            if artist_info:
                genres = artist_info["genres"]  # genres is a list
                for genre in genres:
                    genre_counts[genre] += 1

    return sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:20]


def get_artists_for_genre(all_artists_info, genre, artist_ids):
    return [
        artist
        for artist_id, artist in all_artists_info.items()
        if genre in artist["genres"] and artist_id in artist_ids
    ]


def get_tracks_for_artists(tracks, artist_ids):
    return [
        track
        for track in tracks
        if any(artist["id"] in artist_ids for artist in track["artists"])
    ]


def fetch_and_process_data(sp, time_periods):
    try:
        top_tracks = {period: get_top_tracks(sp, period) for period in time_periods}

        top_artists = {period: get_top_artists(sp, period) for period in time_periods}

        all_artist_ids = []
        all_track_ids = []
        for period in time_periods:
            all_artist_ids.extend([artist["id"] for artist in top_artists[period]["items"]])

            all_artist_ids.extend(
                [artist["id"] for track in top_tracks[period]["items"] for artist in track["artists"]])

            all_track_ids.extend([track["id"] for track in top_tracks[period]["items"]])

        unique_artist_ids = list(set(all_artist_ids))

        unique_track_ids = list(set(all_track_ids))

        all_artists_info = get_or_fetch_artist_info(sp, unique_artist_ids)

        audio_features = get_or_fetch_audio_features(sp, unique_track_ids)

        genre_specific_data = {period: {} for period in time_periods}

        sorted_genres_by_period = {}

        for period in time_periods:
            sorted_genres = get_genre_counts_from_artists_and_tracks(top_artists[period], top_tracks[period],
                                                                     all_artists_info)

            sorted_genres_by_period[period] = sorted_genres

            artist_ids_for_period = {
                                        artist["id"] for artist in top_artists[period]["items"]
                                    } | {
                                        artist["id"]
                                        for track in top_tracks[period]["items"]
                                        for artist in track["artists"]
                                    }

            for genre, count in sorted_genres:
                top_genre_artists = get_artists_for_genre(
                    all_artists_info, genre, artist_ids_for_period
                )
                top_genre_tracks = get_tracks_for_artists(
                    top_tracks[period]["items"],
                    [artist["id"] for artist in top_genre_artists],
                )
                genre_specific_data[period][genre] = {
                    "top_artists": top_genre_artists,
                    "top_tracks": top_genre_tracks,
                }
        recent_tracks = sp.current_user_recently_played(limit=50)["items"]

        playlist_info = []
        offset = 0
        while True:
            playlists = sp.current_user_playlists(limit=50, offset=offset)

            if not playlists["items"]:
                break

            for playlist in playlists["items"]:
                info = {
                    "id": playlist["id"],
                    "name": playlist["name"],
                    "owner": playlist["owner"]["display_name"],
                    "cover_art": playlist["images"][0]["url"]
                    if playlist["images"]
                    else None,
                    "public": playlist["public"],
                    "collaborative": playlist["collaborative"],
                    "total_tracks": playlist["tracks"]["total"],

                }
                playlist_info.append(info)

            offset += 50  # Move to the next page of playlists
            return (
                top_tracks,
                top_artists,
                all_artists_info,
                audio_features,
                genre_specific_data,
                sorted_genres_by_period,
                recent_tracks,
                playlist_info,
            )
    except Exception as e:
        print("Exception:", str(e))
        return (None, None, None, None, None, None, None, None)


def calculate_averages_for_period(tracks, audio_features):
    feature_sums = defaultdict(int)
    track_counts = defaultdict(int)
    min_track = {feature: None for feature in FEATURES}
    max_track = {feature: None for feature in FEATURES}
    min_values = {feature: float("inf") for feature in FEATURES}
    max_values = {feature: float("-inf") for feature in FEATURES}

    for track in tracks["items"]:
        track_id = track["id"]
        for feature in FEATURES:
            value = (
                track.get(feature, 0)
                if feature == "popularity"
                else audio_features[track_id].get(feature, 0)
            )

            feature_sums[feature] += value
            track_counts[feature] += 1

            if value < min_values[feature]:
                min_values[feature] = value
                min_track[feature] = track
            if value > max_values[feature]:
                max_values[feature] = value
                max_track[feature] = track

    averaged_features = {
        feature: feature_sums[feature] / track_counts[feature]
        if track_counts[feature]
        else 0
        for feature in FEATURES
    }
    return averaged_features, min_track, max_track, min_values, max_values


# Handle Spotify Search
def spotify_search(sp, query, type, limit=6):
    try:
        results = sp.search(q=query, type=type, limit=limit)
        if results.get('artists', {}).get('items'):
            for artist_data in results['artists']['items']:
                add_artist_to_db(artist_data)

        return results
    except SpotifyException as e:
        return {"error": str(e)}


def init_session_client(session):
    access_token = session.get("tokens", {}).get("access_token")
    expiry_time_str = session.get("tokens", {}).get("expiry_time")

    if expiry_time_str:
        expiry_time = datetime.fromisoformat(expiry_time_str)
        if datetime.now() >= expiry_time:
            access_token = None

    if not access_token:
        refresh_response = json.loads(refresh())
        if "error" in refresh_response:
            return None, jsonify({"error": "Failed to refresh token"})

        # Update access token from session
        access_token = session["tokens"].get("access_token")

    return Spotify(auth=access_token), None


def get_recommendations(sp, limit, market, **kwargs):
    seed_tracks = kwargs.get("track", None)
    seed_artists = kwargs.get("artist", None)
    try:
        return sp.recommendations(
            seed_tracks=seed_tracks,
            seed_artists=seed_artists,
            limit=limit,
            **kwargs
        )
    except Exception as e:
        return {"error": str(e)}


def format_track_info(track):
    return {
        "trackid": track["id"],
        "artistid": track["artists"][0]["id"] if track["artists"] else None,
        "preview": track["preview_url"],
        "cover_art": track["album"]["images"][0]["url"]
        if track["album"]["images"]
        else None,
        "artist": track["artists"][0]["name"],
        "trackName": track["name"],
        "trackUrl": track["external_urls"]["spotify"],
        "albumName": track["album"]["name"],
    }


def get_or_fetch_artist_info(sp, artist_ids):
    # Fetch existing artists from the DB
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
    print(existing_feature_ids)
    to_fetch = [track_id for track_id in track_ids if track_id not in existing_feature_ids]
    batch_size = 100

    for i in range(0, len(to_fetch), batch_size):
        batch = [x for x in to_fetch[i:i + batch_size] if x is not None]
        fetched_features = sp.audio_features(batch)

        for feature in fetched_features:
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
            db.session.commit()

    final_features = {}
    for track_id in track_ids:
        feature = existing_feature_ids[track_id]
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


def get_playlist_details(sp, playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    next_page = results['next']

    while next_page:
        results = sp.next(results)
        tracks.extend(results['items'])
        next_page = results['next']

    track_info_list = []
    artist_ids = []
    for track_data in tracks:
        track = track_data['track']
        artists = track['artists']

        for artist in artists:
            artist_ids.append(artist['id'])

    # Fetch data for all artists at once
    artist_info_dict = get_or_fetch_artist_info(sp, artist_ids)  # Assuming this function now returns a dictionary

    for track_data in tracks:
        track = track_data['track']
        artists = track['artists']

        artist_info = []
        for artist in artists:
            artist_id = artist['id']
            artist_data = artist_info_dict[artist_id]  # Get the artist data from the dictionary
            artist_info.append(artist_data)

        track_info = {
            'id': track['id'],
            'name': track['name'],
            'popularity': track['popularity'],
            'album': track['album']['name'],
            'release_date': track['album']['release_date'],
            'explicit': track['explicit'],
            'artists': artist_info  # Store all artist information
        }

        track_info_list.append(track_info)

    return track_info_list
