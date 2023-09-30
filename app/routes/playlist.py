import os
from flask import Blueprint, render_template, jsonify, session, \
    request, send_file
import json

from app.routes.auth import require_spotify_auth
from app.util.database_utils import db, playlist_sql
from app.util.session_utils import load_from_json
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
    user_data_json_path = os.path.join(user_directory, 'user_data.json')

    # Try to retrieve the playlist from the SQL database
    playlist = playlist_sql.query.get(playlist_id)
    playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"

    if playlist:
        playlist_data = playlist.__dict__
        owner_name = playlist_data['owner']
        total_tracks = playlist_data['total_tracks']
        is_collaborative = playlist_data['collaborative']
        is_public = playlist_data['public']
        temporal_stats = playlist_data.get('temporal_stats', {})
        year_count = temporal_stats.get('year_count', {})

        return render_template('spec_playlist.html', playlist_id=playlist_id, playlist_url=playlist_url,
                               playlist_data=playlist_data,
                               year_count=json.dumps(year_count), owner_name=owner_name, total_tracks=total_tracks,
                               is_collaborative=is_collaborative, is_public=is_public)

    # If the playlist wasn't in the SQL database, get the basic details from the JSON file
    user_data = load_from_json(user_data_json_path)
    playlist_details = {}

    for playlist in user_data["playlists"]:
        if playlist['id'] == playlist_id:
            playlist_details = {
                'id': playlist['id'],
                'name': playlist['name'],
                'owner': playlist['owner'],
                'cover_art': playlist["cover_art"],
                'public': playlist['public'],
                'collaborative': playlist['collaborative'],
                'total_tracks': playlist["total_tracks"],
            }

    # Get the additional details from the Spotify API
    sp, error = init_session_client(session)
    if error:
        return json.dumps(error), 401

    pl_track_data, pl_genre_counts, pl_top_artists, \
        pl_feature_stats, pl_temporal_stats, = \
        get_playlist_details(sp, playlist_id)

    # Create a new playlist_sql object and save it to the SQL database
    new_playlist = playlist_sql(id=playlist_details['id'],
                                name=playlist_details['name'],
                                owner=playlist_details['owner'],
                                cover_art=playlist_details['cover_art'],
                                public=playlist_details['public'],
                                collaborative=playlist_details['collaborative'],
                                total_tracks=playlist_details['total_tracks'],
                                tracks=pl_track_data,
                                genre_counts=pl_genre_counts,
                                top_artists=pl_top_artists,
                                feature_stats=pl_feature_stats,
                                temporal_stats=pl_temporal_stats, )

    db.session.merge(new_playlist)
    db.session.commit()
    playlist_data = new_playlist.__dict__

    temporal_stats = playlist_data.get('temporal_stats', {})
    year_count = temporal_stats.get('year_count', {})
    owner_name = playlist_data['owner']
    total_tracks = playlist_data['total_tracks']
    is_collaborative = playlist_data['collaborative']
    is_public = playlist_data['public']

    return render_template('spec_playlist.html', playlist_id=playlist_id, playlist_url=playlist_url,
                           playlist_data=playlist_data,
                           year_count=json.dumps(year_count), owner_name=owner_name, total_tracks=total_tracks,
                           is_collaborative=is_collaborative, is_public=is_public)
