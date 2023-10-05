from flask import Blueprint, render_template, jsonify, session

from app.routes.auth import require_spotify_auth
from app.util.database_utils import UserData
from app.util.spotify_utils import calculate_averages_for_period

bp = Blueprint('stats', __name__)


@bp.route('/stats')
@require_spotify_auth
def stats():
    spotify_user_id = session["USER_ID"]
    data = {
        "images": [{"url": session.get("PROFILE_PIC", "")}],
        "display_name": session.get("DISPLAY_NAME", "")
    }

    user_data_entry = UserData.query.filter_by(spotify_user_id=spotify_user_id).first()

    if not user_data_entry:
        return jsonify(error="User data not found"), 404

    top_tracks = user_data_entry.top_tracks
    top_artists = user_data_entry.top_artists
    sorted_genres_by_period = user_data_entry.sorted_genres_by_period
    genre_specific_data = user_data_entry.genre_specific_data
    audio_features = user_data_entry.audio_features

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
                           data=data,
                           top_tracks=top_tracks,
                           top_artists=top_artists,
                           sorted_genres=sorted_genres_by_period,
                           genre_specific_data=genre_specific_data,
                           user_data=user_data_entry,
                           period_data=period_data)
