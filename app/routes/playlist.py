import os
from flask import Blueprint, render_template, jsonify, \
    session, redirect, url_for
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

    sp, error = init_session_client(session)
    if error:
        return json.dumps(error), 401

    pl_playlist_info, pl_track_data, pl_genre_counts, pl_top_artists, \
        pl_feature_stats, pl_temporal_stats, = \
        get_playlist_details(sp, playlist_id)

    # Create a new playlist_sql object and save it to the SQL database
    new_playlist = playlist_sql(id=pl_playlist_info['id'],
                                name=pl_playlist_info['name'],
                                owner=pl_playlist_info['owner'],
                                cover_art=pl_playlist_info['cover_art'],
                                public=pl_playlist_info['public'],
                                collaborative=pl_playlist_info['collaborative'],
                                total_tracks=pl_playlist_info['total_tracks'],
                                snapshot_id=pl_playlist_info['snapshot_id'],
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


@bp.route('/playlist/<string:playlist_id>/refresh', methods=['POST'])
@require_spotify_auth
def refresh_playlist(playlist_id):
    sp, error = init_session_client(session)
    if error:
        return json.dumps(error), 401

    playlist = playlist_sql.query.get(playlist_id)
    if not playlist:
        return "Playlist not found", 404

    # Fetch the new data
    pl_playlist_info, pl_track_data, pl_genre_counts, pl_top_artists, \
        pl_feature_stats, pl_temporal_stats, = \
        get_playlist_details(sp, playlist_id)

    # Update the playlist object
    playlist.name = pl_playlist_info['name']
    playlist.owner = pl_playlist_info['owner']
    playlist.cover_art = pl_playlist_info['cover_art']
    playlist.public = pl_playlist_info['public']
    playlist.collaborative = pl_playlist_info['collaborative']
    playlist.total_tracks = pl_playlist_info['total_tracks']
    playlist.snapshot_id = pl_playlist_info['snapshot_id']
    playlist.tracks = pl_track_data
    playlist.genre_counts = pl_genre_counts
    playlist.top_artists = pl_top_artists
    playlist.feature_stats = pl_feature_stats
    playlist.temporal_stats = pl_temporal_stats

    db.session.merge(playlist)
    db.session.commit()

    return redirect(url_for('playlist.show_playlist', playlist_id=playlist_id))


@bp.route('/like_all_songs/<playlist_id>')
def like_all_songs(playlist_id):
    sp, error = init_session_client(session)
    if error:
        return json.dumps(error), 401

    playlist = playlist_sql.query.get(playlist_id)
    if not playlist:
        return "Playlist not found", 404

    track_ids = [track['id'] for track in playlist.tracks]

    # Batch the track_ids in groups of 50
    for i in range(0, len(track_ids), 50):
        batch = track_ids[i:i + 50]
        sp.current_user_saved_tracks_add(batch)

    return "All songs liked!"


@bp.route('/unlike_all_songs/<playlist_id>')
def unlike_all_songs(playlist_id):
    sp, error = init_session_client(session)
    if error:
        return json.dumps(error), 401

    playlist = playlist_sql.query.get(playlist_id)
    if not playlist:
        return "Playlist not found", 404

    track_ids = [track['id'] for track in playlist.tracks]

    # Batch the track_ids in groups of 50
    for i in range(0, len(track_ids), 50):
        batch = track_ids[i:i + 50]
        sp.current_user_saved_tracks_delete(batch)

    return "All songs unliked!"


@bp.route('/remove_duplicates/<playlist_id>')
def remove_duplicates(playlist_id):
    sp, error = init_session_client(session)
    if error:
        return json.dumps(error), 401

    playlist = playlist_sql.query.get(playlist_id)
    if not playlist:
        return "Playlist not found", 404

    snapshot_id = playlist.snapshot_id

    track_ids = [track['id'] for track in playlist.tracks if
                 track['id'] is not None]  # Exclude local files for duplicate check
    all_track_ids = [track['id'] for track in playlist.tracks]  # Includes local files for positioning

    track_count = {track: track_ids.count(track) for track in set(track_ids)}

    positions_to_remove = []

    for track_id, count in track_count.items():
        if count > 1:
            # Get all positions except the first one (to keep one instance)
            duplicate_positions = [i for i, x in enumerate(all_track_ids) if x == track_id][1:]
            positions_to_remove.extend(duplicate_positions)

    for i in range(0, len(positions_to_remove), 100):
        batch = [{'uri': 'spotify:track:' + all_track_ids[pos], 'positions': [pos]} for pos in
                 positions_to_remove[i:i + 100]]
        sp.playlist_remove_specific_occurrences_of_items(playlist_id, batch, snapshot_id)

    return "Duplicates removed from Spotify and the database updated!"
