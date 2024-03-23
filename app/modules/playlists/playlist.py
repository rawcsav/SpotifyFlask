import base64
import json
import random
from io import BytesIO

import requests
from PIL import Image
from flask import Blueprint, render_template, jsonify, session, redirect, url_for, request
from app.models.playlist_models import Playlist
from modules.auth.auth import require_spotify_auth, fetch_user_data
from modules.playlists.playlist_util import calculate_playlist_weights, fetch_playlists, aggregate_playlist_statistics
from util.api_util import get_artists_seeds, get_genres_seeds, format_track_info
from modules.auth.auth_util import verify_session, init_session_client
from modules.recs.recs_util import get_recommendations

playlist_bp = Blueprint("playlist", __name__, template_folder="templates", static_folder="static")


@playlist_bp.route("/playlist", methods=["GET"])
@require_spotify_auth
def playlist():
    sp = init_session_client(session)
    spotify_user_id = session["USER_ID"]
    access_token = verify_session(session)
    res_data = fetch_user_data(access_token)

    user_playlist = Playlist.query.filter_by(user_id=spotify_user_id).first()
    if not user_playlist:
        fetch_playlists(sp, spotify_user_id)
    page = request.args.get("page", 1, type=int)
    per_page = 10  # or any other desired value

    owner_name = session.get("DISPLAY_NAME")
    start = (page - 1) * per_page
    end = start + per_page
    playlists = [playlist for playlist in user_playlist]

    total_playlists = len(playlists)
    total_pages = -(-total_playlists // per_page)  # This calculates the ceiling of division

    return render_template(
        "templates/playlist.html", data=res_data, playlists=playlists, page=page, total_pages=total_pages
    )


@playlist_bp.route("/playlist/<string:playlist_id>")
@require_spotify_auth
def show_playlist(playlist_id):
    # Verify Spotify session and get access token
    access_token = verify_session(session)
    if not access_token:
        return json.dumps({"error": "Spotify authentication required"}), 401

    # Attempt to fetch playlist from the database
    playlist = Playlist.query.get(playlist_id)
    if playlist:
        # Use the aggregated statistics if the playlist exists in the database
        playlist_data = aggregate_playlist_statistics(playlist_id)
    else:
        # Initialize Spotify session client
        sp, error = init_session_client(session)
        if error:
            return json.dumps(error), 401

        # Fetch playlist details directly from Spotify if not found in the database
        playlist_data = get_playlist_details(sp, playlist_id)
        if not playlist_data:
            return json.dumps({"error": "Playlist not found"}), 404

    # Preprocess the genre_counts data and other statistics
    sorted_genre_data = sorted(playlist_data["genre_stats"].items(), key=lambda x: x[1], reverse=True)
    top_10_genre_data = dict(sorted_genre_data[:10])

    # Render the playlist details template with aggregated data
    return render_template(
        "templates/spec_playlist.html",
        playlist_id=playlist_id,
        playlist_url=f"https://open.spotify.com/playlist/{playlist_id}",
        playlist_data=playlist_data,
        top_10_genre_data=top_10_genre_data,
        year_count=json.dumps(playlist_data["year_count"]),
        owner_name=playlist_data.get("owner_name", "Unknown"),
        total_tracks=playlist_data.get("total_tracks", 0),
        is_collaborative=playlist_data.get("is_collaborative", False),
        is_public=playlist_data.get("is_public", True),
        artgen_ten=playlist_data.get("artgen_ten", {}),
        genre_scores=playlist_data.get("genre_scores", {}),
    )


@playlist_bp.route("/playlist/<string:playlist_id>/refresh", methods=["POST"])
@require_spotify_auth
def refresh_playlist(playlist_id):
    result = update_playlist_data(playlist_id)
    if "error" in result:
        return result, 401
    if "Playlist not found" in result:
        return result, 404
    return redirect(url_for("playlist.show_playlist", playlist_id=playlist_id))


@playlist_bp.route("/like_all_songs/<playlist_id>")
def like_all_songs(playlist_id):
    sp, error = init_session_client(session)
    if error:
        return json.dumps(error), 401

    playlist = Playlist.query.get(playlist_id)
    if not playlist:
        return "Playlist not found", 404

    # Filter out tracks without valid IDs
    track_ids = [track["id"] for track in playlist.tracks if track.get("id")]
    if not track_ids:
        return "No valid tracks in the playlist", 400

    try:
        # Batch the track_ids in groups of 50
        for i in range(0, len(track_ids), 50):
            batch = track_ids[i : i + 50]
            sp.current_user_saved_tracks_add(batch)
    except Exception as e:
        return f"Error occurred while liking songs: {str(e)}", 500

    return "All songs liked!"


@playlist_bp.route("/unlike_all_songs/<playlist_id>")
def unlike_all_songs(playlist_id):
    sp, error = init_session_client(session)
    if error:
        return json.dumps(error), 401

    playlist = Playlist.query.get(playlist_id)
    if not playlist:
        return "Playlist not found", 404

    # Filter out tracks without valid IDs
    track_ids = [track["id"] for track in playlist.tracks if track.get("id")]
    if not track_ids:
        return "No valid tracks in the playlist", 400

    try:
        # Batch the track_ids in groups of 50
        for i in range(0, len(track_ids), 50):
            batch = track_ids[i : i + 50]
            sp.current_user_saved_tracks_delete(batch)
    except Exception as e:
        return f"Error occurred while unliking songs: {str(e)}", 500

    return "All songs unliked!"


@playlist_bp.route("/remove_duplicates/<playlist_id>")
def remove_duplicates(playlist_id):
    sp, error = init_session_client(session)
    if error:
        return json.dumps(error), 401

    playlist = Playlist.query.get(playlist_id)
    if not playlist:
        return "Playlist not found", 404

    snapshot_id = playlist.snapshot_id

    track_ids = [track["id"] for track in playlist.tracks if track["id"] is not None]
    all_track_ids = [track["id"] for track in playlist.tracks]

    track_count = {track: track_ids.count(track) for track in set(track_ids)}

    positions_to_remove = []

    for track_id, count in track_count.items():
        if count > 1:
            duplicate_positions = [i for i, x in enumerate(all_track_ids) if x == track_id][1:]
            positions_to_remove.extend(duplicate_positions)

    for i in range(0, len(positions_to_remove), 100):
        batch = [
            {"uri": "spotify:track:" + all_track_ids[pos], "positions": [pos]}
            for pos in positions_to_remove[i : i + 100]
        ]
        sp.playlist_remove_specific_occurrences_of_items(playlist_id, batch, snapshot_id)

    update_result = update_playlist_data(playlist_id)
    if "error" in update_result:
        return update_result, 401
    if "Playlist not found" in update_result:
        return update_result, 404

    # Redirect to the playlist page or a route that displays the updated playlist
    return redirect(url_for("playlist.show_playlist", playlist_id=playlist_id))


MAX_RETRIES = 3
RETRY_WAIT_SECONDS = 2


@playlist_bp.route("/playlist/<string:playlist_id>/reorder", methods=["POST"])
@require_spotify_auth
def reorder_playlist(playlist_id):
    sp, error = init_session_client(session)
    if error:
        return jsonify(error=error), 401

    playlist = Playlist.query.get(playlist_id)
    if not playlist:
        return jsonify(error="Playlist not found"), 404

    non_local_files = [track for track in playlist.tracks if track["id"] is not None]

    added_at_dates = [track["added_at"] for track in non_local_files]
    track_ids = [track["id"] for track in non_local_files]
    release_dates = [track["release_date"] for track in non_local_files]

    combined = list(zip(track_ids, added_at_dates, release_dates))
    sorting_criterion = request.json.get("sorting_criterion")

    if sorting_criterion == "Date Added - Ascending":
        sorted_tracks = sorted(combined, key=lambda x: x[1])
    elif sorting_criterion == "Date Added - Descending":
        sorted_tracks = sorted(combined, key=lambda x: x[1], reverse=True)
    elif sorting_criterion == "Release Date - Ascending":
        sorted_tracks = sorted(combined, key=lambda x: (x[2] is None, x[2]))  # Prioritize non-None values
    elif sorting_criterion == "Release Date - Descending":
        sorted_tracks = sorted(combined, key=lambda x: (x[2] is None, x[2]), reverse=True)
    elif sorting_criterion == "Random Shuffle":
        random.shuffle(combined)
        sorted_tracks = combined
    else:
        return jsonify(error="Invalid sorting criterion"), 400

    sorted_track_ids = [item[0] for item in sorted_tracks]
    playlist_name = playlist.name
    user_id = session["USER_ID"]
    new_playlist_name = f"Sorted {playlist_name}"
    new_playlist = sp.user_playlist_create(user_id, new_playlist_name)
    new_playlist_id = new_playlist["id"]

    track_uris_to_add = [f"spotify:track:{track_id}" for track_id in sorted_track_ids if track_id is not None]

    for i in range(0, len(track_uris_to_add), 100):
        batch = track_uris_to_add[i : i + 100]
        try:
            sp.user_playlist_add_tracks(user_id, new_playlist_id, batch)
        except Exception as e:
            return jsonify(error=f"An error occurred while adding tracks: {str(e)}"), 500

    return jsonify(status="Playlist reordered successfully"), 200


@playlist_bp.route("/get_pl_recommendations/<string:playlist_id>/recommendations", methods=["POST"])
def get_pl_recommendations(playlist_id):
    sp, error = init_session_client(session)
    if error:
        return jsonify(error=error), 401

    playlist = Playlist.query.get(playlist_id)
    if not playlist:
        return jsonify(error="Playlist not found"), 404

    genre_info = playlist.genre_counts
    top_artists = playlist.top_artists

    artist_counts = {artist[0]: artist[1] for artist in top_artists}
    artist_ids = {artist[0]: artist[4] for artist in top_artists}

    top_artist_ids = get_artists_seeds(artist_counts, artist_ids)
    top_genres = get_genres_seeds(sp, genre_info)

    num_artist_seeds = 5 - len(top_genres)

    seeds = {"track": None, "artist": top_artist_ids[:num_artist_seeds], "genre": top_genres}

    recommendations_data = get_recommendations(sp, limit=10, market="US", **seeds)

    if "error" in recommendations_data:
        return json.dumps(recommendations_data), 400

    track_info_list = [format_track_info(track) for track in recommendations_data["tracks"]]
    return jsonify({"recs": track_info_list})


@playlist_bp.route("/playlist/<string:playlist_id>/cover-art", methods=["POST"])
@require_spotify_auth
def change_cover_art(playlist_id):
    image_url = request.json.get("image_url")

    if not image_url:
        return jsonify(error="Image URL not provided"), 400

    try:
        # Fetch the image from the provided URL
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))

        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue())

        # Initialize the Spotify client
        sp, error = init_session_client(session)
        if error:
            return jsonify(error=error), 401

        # Use the Spotify API to update the cover art
        sp.playlist_upload_cover_image(playlist_id, img_base64.decode("utf-8"))

        return jsonify(status="Cover art updated successfully"), 200

    except Exception as e:
        return jsonify(error=str(e)), 500
