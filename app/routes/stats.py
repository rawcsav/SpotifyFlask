import os

from flask import Blueprint, render_template, jsonify, session

from app.routes.auth import require_spotify_auth
from app.util.session_utils import load_from_json
from app.util.spotify_utils import calculate_averages_for_period

bp = Blueprint('stats', __name__)


@bp.route('/stats')
@require_spotify_auth
def stats():
    user_directory = session["UPLOAD_DIR"]
    json_path = os.path.join(user_directory, 'user_data.json')
    user_data = load_from_json(json_path)

    if not user_data:
        return jsonify(error="User data not found"), 404

    top_tracks = user_data['top_tracks']
    top_artists = user_data['top_artists']
    sorted_genres_by_period = user_data['sorted_genres']
    genre_specific_data = user_data['genre_specific_data']
    audio_features = user_data['audio_features']

    time_periods = ['short_term', 'medium_term', 'long_term', 'overall']
    period_data = {}
    for period in time_periods:
        period_tracks = top_tracks[period] if period != 'overall' else {
            'items': [track for sublist in top_tracks.values() for track in sublist['items']]}
        period_data[period] = {}
        period_data[period]['averages'], period_data[period]['min_track'], period_data[period]['max_track'], \
            period_data[period]['min_values'], period_data[period]['max_values'] = calculate_averages_for_period(
            period_tracks, audio_features)

    return render_template('stats.html',
                           top_tracks=top_tracks,
                           top_artists=top_artists,
                           sorted_genres=sorted_genres_by_period,
                           genre_specific_data=genre_specific_data,
                           user_data=user_data,
                           period_data=period_data)
