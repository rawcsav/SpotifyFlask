import json
from collections import defaultdict
from datetime import datetime, timedelta
from spotipy import Spotify
from spotipy.client import SpotifyException

from app import config
from app.routes.auth import refresh
from app.util.database_utils import add_artist_to_db, get_or_fetch_artist_info, \
    get_or_fetch_audio_features, db, UserData

FEATURES = config.AUDIO_FEATURES

from flask import redirect, session


def init_session_client(session):
    access_token = session.get("tokens", {}).get("access_token")
    expiry_time_str = session.get("tokens", {}).get("expiry_time")

    if expiry_time_str:
        expiry_time = datetime.fromisoformat(expiry_time_str)
        if datetime.now() >= expiry_time:
            access_token = None

    if not access_token:
        refresh_response = refresh()

        if refresh_response.status_code == 200:
            access_token = refresh_response.json.get("access_token")
        else:
            return redirect(config.REDIRECT_URL)

    if not access_token:  # Double check in case of any unforeseen issues after refresh
        return redirect(config.REDIRECT_URL)

    return Spotify(auth=access_token), None


def get_top_tracks(sp, period):
    return sp.current_user_top_tracks(time_range=period, limit=50)


def get_top_artists(sp, period):
    return sp.current_user_top_artists(time_range=period, limit=50)


def spotify_search(sp, query, type, limit=6):
    try:
        results = sp.search(q=query, type=type, limit=limit)
        if results.get('artists', {}).get('items'):
            for artist_data in results['artists']['items']:
                add_artist_to_db(artist_data)
            db.session.commit()
        return results
    except SpotifyException as e:
        return {"error": str(e)}


def get_recommendations(sp, limit, market, **kwargs):
    seed_tracks = kwargs.get("track", None)
    seed_artists = kwargs.get("artist", None)
    seed_genres = kwargs.get("genre", None)
    try:
        return sp.recommendations(
            seed_tracks=seed_tracks,
            seed_artists=seed_artists,
            seed_genres=seed_genres,
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
            all_artist_ids.extend([artist.get("id") for artist in top_artists[period]["items"] if artist.get("id")])

            all_artist_ids.extend(
                [artist.get("id") for track in top_tracks[period]["items"] for artist in track["artists"] if
                 artist.get("id")]
            )

            all_track_ids.extend([track["id"] for track in top_tracks[period]["items"]])

        unique_artist_ids = list(set(all_artist_ids))
        unique_track_ids = list(set(all_track_ids))

        all_artists_info = get_or_fetch_artist_info(sp, unique_artist_ids)
        audio_features = get_or_fetch_audio_features(sp, unique_track_ids)

        genre_specific_data = {period: {} for period in time_periods}

        sorted_genres_by_period = {}

        for period in time_periods:
            sorted_genres = get_genre_counts_from_artists_and_tracks(
                top_artists[period], top_tracks[period],
                all_artists_info
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


def update_user_data(user_data_entry):
    sp, error = init_session_client(session)
    if error:
        return json.dumps(error), 401

    time_periods = ["short_term", "medium_term", "long_term"]
    top_tracks, top_artists, all_artists_info, audio_features, genre_specific_data, sorted_genres_by_period, recent_tracks, playlist_info = fetch_and_process_data(
        sp, time_periods)

    user_data_entry.top_tracks = top_tracks
    user_data_entry.top_artists = top_artists
    user_data_entry.all_artists_info = all_artists_info
    user_data_entry.audio_features = audio_features
    user_data_entry.genre_specific_data = genre_specific_data
    user_data_entry.sorted_genres_by_period = sorted_genres_by_period
    user_data_entry.recent_tracks = recent_tracks
    user_data_entry.playlist_info = playlist_info
    user_data_entry.last_active = datetime.utcnow()

    db.session.merge(user_data_entry)
    db.session.commit()

    return "User updated successfully"


def check_and_refresh_user_data(user_data_entry):
    if user_data_entry:
        delta_since_last_active = datetime.utcnow() - user_data_entry.last_active
        if timedelta(days=7) < delta_since_last_active < timedelta(days=30):
            update_user_data(user_data_entry)
        return True
    else:
        return False


def delete_old_user_data():
    threshold_date = datetime.utcnow() - timedelta(days=30)
    old_users = UserData.query.filter(UserData.last_active < threshold_date).all()
    for user in old_users:
        db.session.delete(user)
    db.session.commit()
