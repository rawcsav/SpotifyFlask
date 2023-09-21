import os

from flask import Blueprint, render_template, session

from app.util.session_utils import (
    verify_session,
    fetch_user_data,
    manage_user_directory,
    store_to_json,
    load_from_json,
)
from app.util.spotify_utils import fetch_and_process_data

bp = Blueprint("user", __name__)


@bp.route("/profile")
def profile():
    # Verify if the session has tokens and fetch access_token
    access_token = verify_session(session)

    # Fetch Spotify user data
    res_data = fetch_user_data(access_token)
    spotify_user_id = res_data.get("id")

    # Manage user directory
    manage_user_directory(spotify_user_id, session)
    user_directory = session["UPLOAD_DIR"]
    json_path = os.path.join(user_directory, "user_data.json")

    # Check if user data already exists
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
        genre_counts,
        genre_specific_data,
        sorted_genres_by_period,
        recent_tracks,
        playlist_info,
    ) = fetch_and_process_data(access_token, time_periods)

    # Aggregate user data
    user_data = {
        "top_tracks": top_tracks,
        "top_artists": top_artists,
        "all_artists_info": all_artists_info,
        "audio_features": audio_features,
        "genre_counts": genre_counts,
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
