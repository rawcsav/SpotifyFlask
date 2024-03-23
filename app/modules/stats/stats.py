from flask import Blueprint, render_template, jsonify, session
from sqlalchemy.orm import joinedload

from modules.auth.auth import require_spotify_auth, fetch_user_data
from modules.user.user_util import calculate_averages_for_period
from modules.auth.auth_util import verify_session
from app.models.user_models import User, UserTrackStats, UserArtistStats, UserGenreStats

stats_bp = Blueprint("stats", __name__, template_folder="templates", static_folder="static")


@stats_bp.route("/stats")
@require_spotify_auth
def stats():
    spotify_user_id = session["USER_ID"]
    access_token = verify_session(session)
    res_data = fetch_user_data(access_token)

    user = User.query.filter_by(id=spotify_user_id).first()
    if not user:
        return jsonify(error="User data not found"), 404

    time_periods = ["short_term", "medium_term", "long_term"]

    # Fetch top tracks and artists for each period
    top_tracks = {
        period: [
            track_stats.track for track_stats in UserTrackStats.query.filter_by(user_id=user.id, period=period).all()
        ]
        for period in time_periods
    }

    top_artists = {
        period: [
            artist_stats.artist
            for artist_stats in UserArtistStats.query.filter_by(user_id=user.id, period=period)
            .options(joinedload(UserArtistStats.artist))
            .all()
        ]
        for period in time_periods
    }

    # Fetch genre-specific data
    genre_specific_data = {
        period: [
            genre_stats.genre
            for genre_stats in UserGenreStats.query.filter_by(user_id=user.id, period=period)
            .options(joinedload(UserGenreStats.genre))
            .all()
        ]
        for period in time_periods
    }

    # Calculate averages for period
    period_data = {}
    for period in time_periods + ["overall"]:
        period_tracks = (
            top_tracks[period]
            if period != "overall"
            else {"items": [track for sublist in top_tracks.values() for track in sublist]}
        )
        period_data[period] = calculate_averages_for_period(period_tracks, user.audio_features)

    return render_template(
        "templates/stats.html",
        data=res_data,
        top_tracks=top_tracks,
        top_artists=top_artists,
        genre_specific_data=genre_specific_data,
        user_data=user,
        period_data=period_data,
    )
