import json
import os
from collections import defaultdict

from flask import Blueprint, session, render_template, jsonify

bp = Blueprint('stats', __name__)

FEATURES = [
    'acousticness', 'danceability', 'duration_ms', 'energy', 'instrumentalness',
    'liveness', 'loudness', 'speechiness', 'tempo', 'valence', 'popularity'
]


@bp.route('/stats')
def stats():
    user_directory = session["UPLOAD_DIR"]
    json_path = os.path.join(user_directory, 'user_data.json')

    if not os.path.exists(json_path):
        return jsonify(error="User data not found"), 404

    with open(json_path, 'r') as f:
        user_data = json.load(f)

    top_tracks = user_data['top_tracks']
    top_artists = user_data['top_artists']
    sorted_genres_by_period = user_data['sorted_genres']
    genre_specific_data = user_data['genre_specific_data']
    audio_features = user_data['audio_features']

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
                if feature == 'popularity':
                    value = track.get('popularity', 0)
                else:
                    value = audio_features[track_id].get(feature, 0)

                feature_sums[feature] += value
                track_counts[feature] += 1

                # identify min/max tracks and values
                if value < min_values[feature]:
                    min_values[feature] = value
                    min_track[feature] = track
                if value > max_values[feature]:
                    max_values[feature] = value
                    max_track[feature] = track

        # calculate average
        averaged_features = {
            feature: total / track_counts[feature] if track_counts[feature] else 0
            for feature, total in feature_sums.items()
        }
        return averaged_features, min_track, max_track, min_values, max_values

    time_periods = ['short_term', 'medium_term', 'long_term', 'overall']
    period_data = {}
    for period in time_periods:
        if period == 'overall':
            period_data[period] = {}
            period_data[period]['averages'], period_data[period]['min_track'], period_data[period]['max_track'], \
                period_data[period]['min_values'], period_data[period]['max_values'] = calculate_averages_for_period(
                {'items': [track for sublist in top_tracks.values() for track in sublist['items']]},
                audio_features
            )
        else:
            period_data[period] = {}
            period_data[period]['averages'], period_data[period]['min_track'], period_data[period]['max_track'], \
                period_data[period]['min_values'], period_data[period]['max_values'] = calculate_averages_for_period(
                top_tracks[period],
                audio_features
            )

    return render_template('stats.html',
                           top_tracks=top_tracks,
                           top_artists=top_artists,
                           sorted_genres=sorted_genres_by_period,
                           genre_specific_data=genre_specific_data,
                           user_data=user_data,
                           period_data=period_data)
