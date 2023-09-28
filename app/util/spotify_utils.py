import json
from collections import defaultdict
from datetime import datetime
from flask import jsonify
from spotipy import Spotify
from spotipy.client import SpotifyException

from app import config
from app.routes.auth import refresh

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
            for genre in all_artists_info[artist["id"]]["genres"]:
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
        top_tracks = {
            period: get_top_tracks(sp, period) for period in time_periods
        }
        top_artists = {
            period: get_top_artists(sp, period) for period in time_periods
        }

        # Accumulate artist and track IDs
        all_artist_ids = []
        all_track_ids = []
        for period in time_periods:
            all_artist_ids.extend(
                [artist["id"] for artist in top_artists[period]["items"]]
            )
            all_artist_ids.extend(
                [
                    artist["id"]
                    for track in top_tracks[period]["items"]
                    for artist in track["artists"]
                ]
            )
            all_track_ids.extend([track["id"] for track in top_tracks[period]["items"]])

        # Remove duplicate IDs
        unique_artist_ids = list(set(all_artist_ids))
        unique_track_ids = list(set(all_track_ids))

        # Fetch detailed artist info
        all_artists_info = {}
        for i in range(
                0, len(unique_artist_ids), 50
        ):  # Spotify's API allows max 50 at a time
            batch_ids = unique_artist_ids[i: i + 50]
            artists_data = sp.artists(batch_ids)
            for artist in artists_data["artists"]:
                all_artists_info[artist["id"]] = artist

        # Fetch audio features for tracks
        audio_features = get_audio_features_for_tracks(sp, unique_track_ids)

        # Initialize genre counts and genre-specific data
        genre_specific_data = {period: {} for period in time_periods}
        sorted_genres_by_period = {}  # Added this line to store sorted genres by period

        for period in time_periods:
            sorted_genres = get_genre_counts_from_artists_and_tracks(
                top_artists[period], top_tracks[period], all_artists_info
            )
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

            # More processing logic can be added here if needed...
        recent_tracks = sp.current_user_recently_played(limit=50)["items"]

        playlist_info = []
        offset = 0
        while True:
            playlists = sp.current_user_playlists(limit=50, offset=offset)
            if not playlists["items"]:
                break  # Exit the loop if no more playlists are found

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

        # Return the processed data
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
        # Handle exceptions and return an error response
        return jsonify(error=str(e)), 500


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
        return sp.search(q=query, type=type, limit=limit)
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


def get_or_fetch_artist_info(sp, artist_id, all_artists_info):
    if artist_id in all_artists_info:
        return all_artists_info[artist_id]
    else:
        artist_info = sp.artist(artist_id)
        all_artists_info[artist_id] = artist_info  # Save all information about the artist
        return artist_info


def get_playlist_details(sp, playlist_id, all_artists_info):
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    next_page = results['next']

    # Pagination loop
    while next_page:
        results = sp.next(results)
        tracks.extend(results['items'])
        next_page = results['next']

    track_info_list = []

    for track_data in tracks:
        track = track_data['track']
        artists = track['artists']

        artist_info = []
        for artist in artists:
            artist_id = artist['id']
            artist_data = get_or_fetch_artist_info(sp, artist_id, all_artists_info)
            artist_info.append(artist_data)  # Add all saved artist information

        track_info = {
            'id': track['id'],
            'name': track['name'],
            'duration': track['duration_ms'],
            'popularity': track['popularity'],
            'album': track['album']['name'],
            'release_date': track['album']['release_date'],
            'explicit': track['explicit'],
            'artists': artist_info  # Store all artist information
        }

        track_info_list.append(track_info)

    return track_info_list
