import json
from flask import Blueprint, jsonify, render_template, request, session

from app.routes.auth import require_spotify_auth
from app.util.database_utils import UserData
from app.util.spotify_utils import (
    init_session_client,
    get_recommendations,
    format_track_info,
)

bp = Blueprint("recommendations", __name__)


def parse_seeds(key):
    return [
        item.strip()
        for item in request.form.get(f"{key}_seeds", "").split(",")
        if item.strip()
    ] or None


@bp.route("/recommendations", methods=["GET"])
@require_spotify_auth
def recommendations():
    spotify_user_id = session["USER_ID"]

    # Retrieve the user's data entry from the database
    user_data_entry = UserData.query.filter_by(spotify_user_id=spotify_user_id).first()

    if not user_data_entry:
        return jsonify(error="User data not found"), 404

    owner_name = session.get("DISPLAY_NAME")
    playlists = [playlist for playlist in user_data_entry.playlist_info
                 if playlist["owner"] is not None
                 and playlist["owner"] == owner_name]

    return render_template(
        "recommendations.html",
        playlists=playlists,
        user_data=user_data_entry,
    )


@bp.route("/get_recommendations", methods=["GET", "POST"])
def get_recommendations_route():
    sp, error = init_session_client(session)
    if error:
        return json.dumps(error), 401

    if request.method == "POST":
        seeds = {
            key: [
                     item.strip()
                     for item in request.form.get(f"{key}_seeds", "").split(",")
                     if item.strip()
                 ]
                 or None
            for key in ["track", "artist"]
        }
        limit = request.form.get("limit", 5)
        sliders = {
            key: tuple(map(type_func, request.form.get(f"{key}_slider").split(",")))
            for key, type_func in zip(
                [
                    "popularity",
                    "energy",
                    "instrumentalness",
                    "tempo",
                    "danceability",
                    "valence",
                ],
                [int, float, float, float, float, float],
            )
        }

        recommendations_data = get_recommendations(
            sp, **seeds, limit=limit, **sliders, market="US"
        )

        if "error" in recommendations_data:
            return json.dumps(recommendations_data), 400

        track_info_list = [
            format_track_info(track) for track in recommendations_data["tracks"]
        ]
        return jsonify({"recommendations": track_info_list})


@bp.route("/save_track", methods=["POST"])
def save_track():
    sp, error = init_session_client(session)
    if error:
        return json.dumps(error), 401

    track_id = request.json["track_id"]
    print(f"track_id: {track_id}")

    sp.current_user_saved_tracks_add([track_id])
    return jsonify({"status": "success"})


@bp.route("/add_to_playlist", methods=["POST"])
def add_to_playlist():
    sp, error = init_session_client(session)
    if error:
        return json.dumps(error), 401

    track_id = request.json["track_id"]
    playlist_id = request.json["playlist_id"]
    sp.playlist_add_items(playlist_id, [track_id])
    return jsonify({"status": "success"})
