import json
import os
from collections import defaultdict

import requests
from flask import Blueprint, render_template, session, abort, jsonify
from spotipy import Spotify

from app import config
from app.util import get_top_tracks, get_top_artists, get_audio_features_for_tracks

bp = Blueprint('user', __name__)


@bp.route('/profile')
def profile():
    if 'tokens' not in session:
        abort(400)

    headers = {'Authorization': f"Bearer {session['tokens'].get('access_token')}"}
    res = requests.get(config.ME_URL, headers=headers)
    res_data = res.json()

    if res.status_code != 200:
        abort(res.status_code)

    user_directory = session["UPLOAD_DIR"]
    os.makedirs(user_directory, exist_ok=True)
    json_path = os.path.join(user_directory, 'user_data.json')

    # If user_data.json exists, load it and return
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            user_data = json.load(f)
        return render_template('profile.html', data=res_data, tokens=session.get('tokens'), user_data=user_data)

    # If not, proceed with the data collection
    # If not, proceed with the data collection
    access_token = session['tokens'].get('access_token')
    sp = Spotify(auth=access_token)
    time_periods = ['short_term', 'medium_term', 'long_term']

    try:
        top_tracks = {period: get_top_tracks(access_token, period) for period in time_periods}
        top_artists = {period: get_top_artists(access_token, period) for period in time_periods}
    except Exception as e:
        return jsonify(error=str(e)), 500

    all_artist_ids = []
    all_track_ids = []

    for period in time_periods:
        all_artist_ids.extend([artist['id'] for artist in top_artists[period]['items']])
        all_artist_ids.extend([artist['id'] for track in top_tracks[period]['items'] for artist in track['artists']])
        all_track_ids.extend([track['id'] for track in top_tracks[period]['items']])

    unique_artist_ids = list(set(all_artist_ids))
    unique_track_ids = list(set(all_track_ids))

    # Fetching details about all the artists using the sp.artists method.
    all_artists_info = {}
    for i in range(0, len(unique_artist_ids), 50):  # Spotify's API can retrieve a maximum of 50 artists at a time.
        batch_ids = unique_artist_ids[i:i + 50]
        artists_data = sp.artists(batch_ids)
        for artist in artists_data['artists']:
            all_artists_info[artist['id']] = artist

    # Fetching audio features for all the top tracks across every period
    audio_features = get_audio_features_for_tracks(sp, unique_track_ids)

    def get_genre_counts_from_artists_and_tracks(top_artists, top_tracks):
        genre_counts = defaultdict(int)

        for artist in top_artists['items']:
            for genre in artist['genres']:
                genre_counts[genre] += 1

        for track in top_tracks['items']:
            for artist in track['artists']:
                for genre in all_artists_info[artist['id']]['genres']:
                    genre_counts[genre] += 1

        return sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:20]

    def get_artists_for_genre(all_artists_info, genre, artist_ids):
        return [artist for artist_id, artist in all_artists_info.items() if
                genre in artist['genres'] and artist_id in artist_ids]

    def get_tracks_for_artists(tracks, artist_ids):
        return [track for track in tracks if any(artist['id'] in artist_ids for artist in track['artists'])]

    sorted_genres_by_period = {}
    genre_specific_data = {period: {} for period in time_periods}

    for period in time_periods:
        sorted_genres = get_genre_counts_from_artists_and_tracks(top_artists[period], top_tracks[period])
        sorted_genres_by_period[period] = sorted_genres

        artist_ids_for_period = {artist['id'] for artist in top_artists[period]['items']} | {artist['id'] for track in
                                                                                             top_tracks[period]['items']
                                                                                             for artist in
                                                                                             track['artists']}

        for genre, count in sorted_genres:
            top_genre_artists = get_artists_for_genre(all_artists_info, genre, artist_ids_for_period)
            top_genre_tracks = get_tracks_for_artists(top_tracks[period]['items'],
                                                      [artist['id'] for artist in top_genre_artists])

            genre_specific_data[period][genre] = {
                'top_artists': top_genre_artists,
                'top_tracks': top_genre_tracks
            }

    user_data = {
        'top_tracks': top_tracks,
        'top_artists': top_artists,
        'audio_features': audio_features,
        'sorted_genres': sorted_genres_by_period,
        'genre_specific_data': genre_specific_data
    }

    with open(json_path, 'w') as f:
        json.dump(user_data, f, ensure_ascii=False, indent=4)

    return render_template('profile.html', data=res_data, tokens=session.get('tokens'), user_data=user_data)
