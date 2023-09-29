import os
from flask import Blueprint, render_template, jsonify, session, request
import json

from app.routes.auth import require_spotify_auth
from app.util.session_utils import load_from_json, update_json
from app.util.spotify_utils import init_session_client
from app.util.playlist_utils import get_playlist_details

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
    user_directory = session["UPLOAD_DIR"]
    playlist_data_json_path = os.path.join(user_directory, 'playlist_data.json')
    user_data_json_path = os.path.join(user_directory, 'user_data.json')

    playlist_data = {}

    if os.path.exists(playlist_data_json_path):
        playlist_data = load_from_json(playlist_data_json_path)

    if playlist_id in playlist_data:
        return render_template('spec_playlist.html', playlist_data=playlist_data[playlist_id])

    user_data = load_from_json(user_data_json_path)

    for playlist in user_data["playlists"]:
        if playlist['id'] == playlist_id:
            playlist_data[playlist_id] = {
                'id': playlist['id'],
                'name': playlist['name'],
                'owner': playlist['owner'],
                'cover_art': playlist["cover_art"],
                'public': playlist['public'],
                'collaborative': playlist['collaborative'],
                'total_tracks': playlist["total_tracks"],
            }

            sp, error = init_session_client(session)
            if error:
                return json.dumps(error), 401

            pl_track_data, pl_genre_counts, pl_top_artists, pl_feature_stats = \
                get_playlist_details(sp, playlist_id)

            playlist_data[playlist_id]['tracks'] = pl_track_data
            playlist_data[playlist_id]['genre_counts'] = pl_genre_counts
            playlist_data[playlist_id]['top_artists'] = pl_top_artists
            playlist_data[playlist_id]['feature_stats'] = pl_feature_stats

            update_json(playlist_data, playlist_data_json_path)

            return render_template('spec_playlist.html', playlist_data=playlist_data[playlist_id])

    # If we reach here, the playlist was not found in either JSON files
    return jsonify({'error': 'Playlist not found'}), 404
