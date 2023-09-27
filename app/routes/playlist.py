import os
from flask import Blueprint, render_template, jsonify, session, request
import json

from app.util.session_utils import load_user_data
from app.util.spotify_utils import init_spotify_client

bp = Blueprint('playlist', __name__)


@bp.route('/playlist', methods=['GET'])
def playlist():
    user_directory = session["UPLOAD_DIR"]
    json_path = os.path.join(user_directory, 'user_data.json')
    user_data = load_user_data(json_path)

    if not user_data:
        return jsonify(error="User data not found"), 404

    access_token = session["tokens"].get("access_token")
    sp = init_spotify_client(access_token)

    playlists = [playlist for playlist in user_data["playlists"]]

    return render_template('playlist.html', playlists=playlists)


@bp.route('/playlist/<string:playlist_id>')
def show_playlist(playlist_id):
    playlist_name = request.args.get('playlist_name', 'Default Name')

    return render_template('spec_playlist.html', playlist_id=playlist_id, playlist_name=playlist_name)
