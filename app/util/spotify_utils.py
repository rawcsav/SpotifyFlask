import json
from collections import defaultdict

from flask import jsonify
from spotipy import Spotify
from spotipy.client import SpotifyException

from app import config
from app.routes.auth import refresh

FEATURES = config.AUDIO_FEATURES


def get_top_tracks(access_token, period):
    sp = Spotify(auth=access_token)
    return sp.current_user_top_tracks(time_range=period, limit=50)


def get_top_artists(access_token, period):
    sp = Spotify(auth=access_token)
    return sp.current_user_top_artists(time_range=period, limit=50)


def get_audio_features_for_tracks(sp, track_ids):
    features = {}
    for i in range(0, len(track_ids), 100):
        batch = track_ids[i:i + 100]
        batch_features = sp.audio_features(batch)
        for feature in batch_features:
            if feature:
                features[feature['id']] = feature
    return features


def fetch_and_process_data(access_token, time_periods):
    try:
        # Initialize the Spotify API client
        sp = Spotify(auth=access_token)

        # Fetch top tracks and artists for different time periods
        top_tracks = {period: get_top_tracks(access_token, period) for period in time_periods}
        top_artists = {period: get_top_artists(access_token, period) for period in time_periods}

        # Accumulate artist and track IDs
        all_artist_ids = []
        all_track_ids = []
        for period in time_periods:
            all_artist_ids.extend([artist['id'] for artist in top_artists[period]['items']])
            all_artist_ids.extend(
                [artist['id'] for track in top_tracks[period]['items'] for artist in track['artists']])
            all_track_ids.extend([track['id'] for track in top_tracks[period]['items']])

        # Remove duplicate IDs
        unique_artist_ids = list(set(all_artist_ids))
        unique_track_ids = list(set(all_track_ids))

        # Fetch detailed artist info
        all_artists_info = {}
        for i in range(0, len(unique_artist_ids), 50):  # Spotify's API allows max 50 at a time
            batch_ids = unique_artist_ids[i:i + 50]
            artists_data = sp.artists(batch_ids)
            for artist in artists_data['artists']:
                all_artists_info[artist['id']] = artist

        # Fetch audio features for tracks
        audio_features = get_audio_features_for_tracks(sp, unique_track_ids)

        # Initialize genre counts and genre-specific data
        genre_counts = defaultdict(int)
        genre_specific_data = {period: {} for period in time_periods}

        # Process each time period
        for period in time_periods:
            # Count genres
            for artist in top_artists[period]['items']:
                for genre in artist['genres']:
                    genre_counts[genre] += 1
            for track in top_tracks[period]['items']:
                for artist in track['artists']:
                    for genre in all_artists_info[artist['id']]['genres']:
                        genre_counts[genre] += 1

            # More processing logic can be added here if needed...

        # Return the processed data
        return top_tracks, top_artists, all_artists_info, audio_features, genre_counts, genre_specific_data

    except Exception as e:
        # Handle exceptions and return an error response
        return jsonify(error=str(e)), 500


def calculate_averages_for_period(tracks, audio_features):
    feature_sums = defaultdict(int)
    track_counts = defaultdict(int)
    min_track = {feature: None for feature in FEATURES}
    max_track = {feature: None for feature in FEATURES}
    min_values = {feature: float('inf') for feature in FEATURES}
    max_values = {feature: float('-inf') for feature in FEATURES}

    for track in tracks['items']:
        track_id = track['id']
        for feature in FEATURES:
            value = track.get(feature, 0) if feature == 'popularity' else audio_features[track_id].get(feature, 0)

            feature_sums[feature] += value
            track_counts[feature] += 1

            if value < min_values[feature]:
                min_values[feature] = value
                min_track[feature] = track
            if value > max_values[feature]:
                max_values[feature] = value
                max_track[feature] = track

    averaged_features = {feature: feature_sums[feature] / track_counts[feature] if track_counts[feature] else 0 for
                         feature in FEATURES}
    return averaged_features, min_track, max_track, min_values, max_values


def init_spotify_client(access_token):
    return Spotify(auth=access_token)


# Handle Spotify Search
def spotify_search(sp, query, type, limit=5):
    try:
        return sp.search(q=query, type=type, limit=limit)
    except SpotifyException as e:
        return {'error': str(e)}


def init_session_client(session):
    access_token = session['tokens'].get('access_token')
    if not access_token:
        refresh_response = json.loads(refresh())
        if 'error' in refresh_response:
            return None, {'error': 'Failed to refresh token'}
        access_token = refresh_response['access_token']
    return Spotify(auth=access_token), None


def get_recommendations(sp, limit, market, **kwargs):
    seed_tracks = kwargs.get('track', None)
    seed_artists = kwargs.get('artist', None)
    seed_genres = kwargs.get('genre', None)
    try:
        return sp.recommendations(
            seed_tracks=seed_tracks,
            seed_artists=seed_artists,
            seed_genres=seed_genres,
            limit=limit,
            **kwargs
        )
    except Exception as e:
        return {'error': str(e)}


def format_track_info(track):
    return {
        'trackid': track['id'],
        'artistid': track['artists'][0]['id'] if track['artists'] else None,
        'preview': track['preview_url'],
        'cover_art': track['album']['images'][0]['url'] if track['album']['images'] else None,
        'artist': track['artists'][0]['name'],
        'trackName': track['name'],
        'trackUrl': track['external_urls']['spotify'],
        'albumName': track['album']['name'],
    }
