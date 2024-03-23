import json
from flask import Blueprint, jsonify, render_template, request, session, json

from models.user_models import UserData
from modules.auth.auth import require_spotify_auth, fetch_user_data
from modules.auth.auth_util import verify_session
from modules.recs.recs_util import spotify_search, get_recommendations
from modules.user.user_util import init_session_client, format_track_info
from util.form_util import RecommendationsForm

recs_bp = Blueprint("recs", __name__, template_folder="templates", static_folder="static", url_prefix="/recs")


def parse_seeds(key):
    return [item.strip() for item in request.form.get(f"{key}_seeds", "").split(",") if item.strip()] or None


@recs_bp.route("/recommendations", methods=["GET"])
@require_spotify_auth
def recommendations():
    spotify_user_id = session["USER_ID"]
    access_token = verify_session(session)
    res_data = fetch_user_data(access_token)

    user_data_entry = UserData.query.filter_by(spotify_user_id=spotify_user_id).first()

    if not user_data_entry:
        return jsonify(error="User data not found"), 404

    owner_name = session.get("DISPLAY_NAME")
    playlists = [
        playlist
        for playlist in user_data_entry.playlist_info
        if playlist["owner"] is not None and playlist["owner"] == owner_name
    ]

    return render_template("recommendations.html", data=res_data, playlists=playlists, user_data=user_data_entry)


@recs_bp.route("/get_recommendations", methods=["GET", "POST"])
def get_recommendations_route():
    sp, error = init_session_client(session)
    if error:
        return json.dumps(error), 401

    form = RecommendationsForm()

    if form.validate_on_submit():
        seeds = {
            key: [item.strip() for item in form.data.get(f"{key}_seeds", "").split(",") if item.strip()] or None
            for key in ["track", "artist"]
        }
        limit = form.limit.data
        sliders = {
            key: tuple(map(type_func, form.data[f"{key}_slider"].split(",")))
            for key, type_func in zip(
                ["popularity", "energy", "instrumentalness", "tempo", "danceability", "valence"],
                [int, float, float, float, float, float],
            )
        }

        recommendations_data = get_recommendations(sp, **seeds, limit=limit, **sliders, market="US")

        if "error" in recommendations_data:
            return json.dumps(recommendations_data), 400

        track_info_list = [format_track_info(track) for track in recommendations_data["tracks"]]
        return jsonify({"recommendations": track_info_list}, form=form)


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
