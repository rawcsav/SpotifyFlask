import json
from flask import Blueprint, jsonify, render_template, request, session, json
from modules.auth.auth import require_spotify_auth, fetch_user_data
from modules.auth.auth_util import verify_session, init_session_client
from util.api_util import format_track_info
from app.models.playlist_models import Playlist
from app.models.user_models import User
from modules.recs.recs_util import spotify_search, get_recommendations

recs_bp = Blueprint("recs", __name__, template_folder="templates", static_folder="static")


def parse_seeds(key):
    return [item.strip() for item in request.form.get(f"{key}_seeds", "").split(",") if item.strip()] or None


@recs_bp.route("/recommendations", methods=["GET"])
@require_spotify_auth
def recommendations():
    spotify_user_id = session["USER_ID"]
    access_token = verify_session(session)
    res_data = fetch_user_data(access_token)

    playlist_data = Playlist.query.filter_by(user_id=spotify_user_id)
    user_data_entry = User.query.filter_by(id=spotify_user_id).first()
    if not playlist_data:
        return jsonify(error="User data not found"), 404

    owner_name = session.get("DISPLAY_NAME")
    playlists = [
        playlist for playlist in playlist_data if playlist["owner"] is not None and playlist["owner"] == owner_name
    ]

    return render_template(
        "templates/recommendations.html", data=res_data, playlists=playlists, user_data=user_data_entry
    )


@recs_bp.route("/get_recommendations", methods=["GET", "POST"])
def get_recommendations_route():
    sp, error = init_session_client(session)
    if error:
        return json.dumps(error), 401

    if request.method == "POST":
        seeds = {
            key: [item.strip() for item in request.form.get(f"{key}_seeds", "").split(",") if item.strip()] or None
            for key in ["track", "artist"]
        }
        limit = request.form.get("limit", 5)
        sliders = {
            key: tuple(map(type_func, request.form.get(f"{key}_slider").split(",")))
            for key, type_func in zip(
                ["popularity", "energy", "instrumentalness", "tempo", "danceability", "valence"],
                [int, float, float, float, float, float],
            )
        }

        recommendations_data = get_recommendations(sp, **seeds, limit=limit, **sliders, market="US")

        if "error" in recommendations_data:
            return json.dumps(recommendations_data), 400

        track_info_list = [format_track_info(track) for track in recommendations_data["tracks"]]
        return jsonify({"recs": track_info_list})


@recs_bp.route("/save_track", methods=["POST"])
def save_track():
    sp, error = init_session_client(session)
    if error:
        return json.dumps(error), 401

    track_id = request.json["track_id"]
    print(f"track_id: {track_id}")

    sp.current_user_saved_tracks_add([track_id])
    return jsonify({"status": "success"})


@recs_bp.route("/add_to_playlist", methods=["POST"])
def add_to_playlist():
    sp, error = init_session_client(session)
    if error:
        return json.dumps(error), 401

    track_id = request.json["track_id"]
    playlist_id = request.json["playlist_id"]
    sp.playlist_add_items(playlist_id, [track_id])
    return jsonify({"status": "success"})


@recs_bp.route("/unsave_track", methods=["POST"])
def unsave_track():
    sp, error = init_session_client(session)
    if error:
        return json.dumps(error), 401

    track_id = request.json["track_id"]
    print(f"track_id: {track_id}")

    sp.current_user_saved_tracks_delete([track_id])
    return jsonify({"status": "success"})


@recs_bp.route("/remove_from_playlist", methods=["POST"])
def remove_from_playlist():
    sp, error = init_session_client(session)
    if error:
        return json.dumps(error), 401

    track_id = request.json["track_id"]
    playlist_id = request.json["playlist_id"]

    sp.playlist_remove_all_occurrences_of_items(playlist_id, [track_id])
    return jsonify({"status": "success"})


@recs_bp.route("/search", methods=["POST"])
def search():
    query = request.json.get("query")
    type = request.json.get("type")
    if not query:
        return json.dumps({"error": "No search query provided"}), 400
    sp, error = init_session_client(session)
    if error:
        return json.dumps(error), 401
    results = spotify_search(sp, query, type)
    return json.dumps(results)
