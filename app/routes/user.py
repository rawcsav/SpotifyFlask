import json
import os

from flask import Blueprint, render_template, session, jsonify

from app.routes.auth import require_spotify_auth
from app.util.session_utils import (
    verify_session,
    fetch_user_data,
    manage_user_directory,
    store_to_json,
    load_from_json,
)
from app.util.spotify_utils import fetch_and_process_data, init_session_client

bp = Blueprint("user", __name__)


@bp.route("/profile")
@require_spotify_auth
def profile():
    access_token = verify_session(session)

    res_data = fetch_user_data(access_token)
    spotify_user_id = res_data.get("id")

    spotify_user_display_name = res_data.get("display_name")
    session["DISPLAY_NAME"] = spotify_user_display_name
    sp, error = init_session_client(session)
    if error:
        return json.dumps(error), 401
    manage_user_directory(spotify_user_id, session)
    user_directory = session["UPLOAD_DIR"]
    json_path = os.path.join(user_directory, "user_data.json")

    if os.path.exists(json_path):
        user_data = load_from_json(json_path)
        return render_template(
            "profile.html",
            data=res_data,
            tokens=session.get("tokens"),
            user_data=user_data,
        )

    # Define time periods for Spotify data
    time_periods = ["short_term", "medium_term", "long_term"]

    # Fetch and process Spotify data
    (
        top_tracks,
        top_artists,
        all_artists_info,
        audio_features,
        genre_specific_data,
        sorted_genres_by_period,
        recent_tracks,
        playlist_info,
    ) = fetch_and_process_data(sp, time_periods)

    # Aggregate user data
    user_data = {
        "top_tracks": top_tracks,
        "top_artists": top_artists,
        "all_artists_info": all_artists_info,
        "audio_features": audio_features,
        "sorted_genres": sorted_genres_by_period,
        "genre_specific_data": genre_specific_data,
        "recent_tracks": recent_tracks,
        "playlists": playlist_info,
    }

    # Store the processed data as JSON
    store_to_json(user_data, json_path)

    return render_template(
        "profile.html", data=res_data, tokens=session.get("tokens"), user_data=user_data
    )


@bp.route('/refresh-data', methods=['POST'])
def refresh_data():
    access_token = verify_session(session)
    spotify_user_id = fetch_user_data(access_token).get("id")
    sp, error = init_session_client(session)
    if error:
        return json.dumps(error), 401
    manage_user_directory(spotify_user_id, session)
    user_directory = session["UPLOAD_DIR"]

    # Define time periods for Spotify data
    time_periods = ["short_term", "medium_term", "long_term"]

    (
        top_tracks,
        top_artists,
        all_artists_info,
        audio_features,
        genre_specific_data,
        sorted_genres_by_period,
        recent_tracks,
        playlist_info,
    ) = fetch_and_process_data(sp, time_periods)

    # Aggregate user data
    user_data = {
        "top_tracks": top_tracks,
        "top_artists": top_artists,
        "all_artists_info": all_artists_info,
        "audio_features": audio_features,
        "sorted_genres": sorted_genres_by_period,
        "genre_specific_data": genre_specific_data,
        "recent_tracks": recent_tracks,
        "playlists": playlist_info,
    }
    return jsonify(user_data), 200
