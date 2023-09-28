import os
from flask import Blueprint, render_template, jsonify, session, request
import json

from app.routes.auth import require_spotify_auth
from app.util.session_utils import load_from_json, store_to_json

bp = Blueprint('playlist', __name__)


@bp.route('/playlist', methods=['GET'])
@require_spotify_auth
def playlist():
    user_directory = session["UPLOAD_DIR"]
    json_path = os.path.join(user_directory, 'user_data.json')
    user_data = load_from_json(json_path)

    if not user_data:
        return jsonify(error="User data not found"), 404

    owner_name = session.get("DISPLAY_NAME")
    playlists = [playlist for playlist in user_data["playlists"]
                 if playlist["owner"] is not None
                 and playlist["owner"] is not None
                 and playlist["owner"] == owner_name]

    return render_template('playlist.html', playlists=playlists)


@bp.route('/playlist/<string:playlist_id>')
@require_spotify_auth
def show_playlist(playlist_id):
    playlist_name = request.args.get('playlist_name', 'Default Name')
    user_directory = session.get('UPLOAD_DIR')
    json_path = os.path.join(user_directory, 'playlist_data.json')

    # Step 1 and Step 2
    if os.path.exists(json_path):
        playlist_data = load_from_json(json_path)
    else:
        playlist_data = {}

    # Step 3 and Step 4
    if playlist_id in playlist_data:
        existing_data = playlist_data[playlist_id]
    else:
        existing_data = {
            "playlist_id": playlist_id,
            "playlist_name": playlist_name,
        }
        playlist_data[playlist_id] = existing_data
        store_to_json(playlist_data, json_path)

    # Step 5
    return render_template('spec_playlist.html', playlist_data=existing_data)
