import logging

from flask import Blueprint, render_template, jsonify, \
    session, redirect, url_for, request
import json
import random

from time import sleep
from requests.exceptions import RequestException
from app.routes.auth import require_spotify_auth
from app.util.database_utils import db, playlist_sql, UserData
from app.util.spotify_utils import init_session_client
from app.util.playlist_utils import get_playlist_details, update_playlist_data

bp = Blueprint('playlist', __name__)


@bp.route('/playlist', methods=['GET'])
@require_spotify_auth
def playlist():
    spotify_user_id = session["USER_ID"]
    data = {
        "images": [{"url": session.get("PROFILE_PIC", "")}],
        "display_name": session.get("DISPLAY_NAME", "")
    }
    # Retrieve the user's data entry from the database
    user_data_entry = UserData.query.filter_by(spotify_user_id=spotify_user_id).first()

    if not user_data_entry:
        return jsonify(error="User data not found"), 404

    owner_name = session.get("DISPLAY_NAME")
    playlists = [playlist for playlist in user_data_entry.playlist_info
                 if playlist["owner"] is not None
                 and playlist["owner"] == owner_name]

    return render_template('playlist.html', data=data, playlists=playlists)


@bp.route('/playlist/<string:playlist_id>')
@require_spotify_auth
def show_playlist(playlist_id):
    playlist = playlist_sql.query.get(playlist_id)
    playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"
    data = {
        "images": [{"url": session.get("PROFILE_PIC", "")}],
        "display_name": session.get("DISPLAY_NAME", "")
    }
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

    return render_template('spec_playlist.html', playlist_id=playlist_id,
                           data=data,
                           playlist_url=playlist_url,
                           playlist_data=playlist_data,
                           year_count=json.dumps(year_count), owner_name=owner_name, total_tracks=total_tracks,
                           is_collaborative=is_collaborative, is_public=is_public)


@bp.route('/playlist/<string:playlist_id>/refresh', methods=['POST'])
@require_spotify_auth
def refresh_playlist(playlist_id):
    result = update_playlist_data(playlist_id)
    if "error" in result:
        return result, 401
    if "Playlist not found" in result:
        return result, 404
    return redirect(url_for('playlist.show_playlist', playlist_id=playlist_id))


@bp.route('/like_all_songs/<playlist_id>')
def like_all_songs(playlist_id):
    sp, error = init_session_client(session)
    if error:
        return json.dumps(error), 401

    playlist = playlist_sql.query.get(playlist_id)
    if not playlist:
        return "Playlist not found", 404

    # Filter out tracks without valid IDs
    track_ids = [track['id'] for track in playlist.tracks if track.get('id')]
    if not track_ids:
        return "No valid tracks in the playlist", 400

    try:
        # Batch the track_ids in groups of 50
        for i in range(0, len(track_ids), 50):
            batch = track_ids[i:i + 50]
            sp.current_user_saved_tracks_add(batch)
    except Exception as e:
        return f"Error occurred while liking songs: {str(e)}", 500

    return "All songs liked!"


@bp.route('/unlike_all_songs/<playlist_id>')
def unlike_all_songs(playlist_id):
    sp, error = init_session_client(session)
    if error:
        return json.dumps(error), 401

    playlist = playlist_sql.query.get(playlist_id)
    if not playlist:
        return "Playlist not found", 404

    # Filter out tracks without valid IDs
    track_ids = [track['id'] for track in playlist.tracks if track.get('id')]
    if not track_ids:
        return "No valid tracks in the playlist", 400

    try:
        # Batch the track_ids in groups of 50
        for i in range(0, len(track_ids), 50):
            batch = track_ids[i:i + 50]
            sp.current_user_saved_tracks_delete(batch)
    except Exception as e:
        return f"Error occurred while unliking songs: {str(e)}", 500

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
                 track['id'] is not None]
    all_track_ids = [track['id'] for track in playlist.tracks]

    track_count = {track: track_ids.count(track) for track in set(track_ids)}

    positions_to_remove = []

    for track_id, count in track_count.items():
        if count > 1:
            duplicate_positions = [i for i, x in enumerate(all_track_ids) if x == track_id][1:]
            positions_to_remove.extend(duplicate_positions)

    for i in range(0, len(positions_to_remove), 100):
        batch = [{'uri': 'spotify:track:' + all_track_ids[pos], 'positions': [pos]} for pos in
                 positions_to_remove[i:i + 100]]
        sp.playlist_remove_specific_occurrences_of_items(playlist_id, batch, snapshot_id)

    update_result = update_playlist_data(playlist_id)
    if "error" in update_result:
        return update_result, 401
    if "Playlist not found" in update_result:
        return update_result, 404

    # Redirect to the playlist page or a route that displays the updated playlist
    return redirect(url_for('playlist.show_playlist', playlist_id=playlist_id))


MAX_RETRIES = 3
RETRY_WAIT_SECONDS = 2

logging.basicConfig(level=logging.DEBUG, filename='app.log', format='%(asctime)s - %(levelname)s - %(message)s')


@bp.route('/playlist/<string:playlist_id>/reorder', methods=['POST'])
@require_spotify_auth
def reorder_playlist(playlist_id):
    sp, error = init_session_client(session)
    if error:
        return jsonify(error=error), 401

    playlist = playlist_sql.query.get(playlist_id)
    if not playlist:
        return jsonify(error="Playlist not found"), 404

    # Separate local files and other tracks
    local_files = [track for track in playlist.tracks if track['id'] is None]
    non_local_files = [track for track in playlist.tracks if track['id'] is not None]

    # Logging for debugging
    logging.debug(f"Local files count: {len(local_files)}")
    logging.debug(f"Non-local files count: {len(non_local_files)}")

    # Preprocessing steps to handle inconsistent 'release_date' values
    for track in non_local_files:
        if 'release_date' not in track or not track['release_date']:
            track['release_date'] = '0000-00-00'  # Defaulting to a very early date

    # Extract track details for non-local tracks
    added_at_dates = [track['added_at'] for track in non_local_files]
    track_ids = [track['id'] for track in non_local_files]
    release_dates = [track['release_date'] for track in non_local_files]

    combined = list(zip(track_ids, added_at_dates, release_dates))
    sorting_criterion = request.json.get('sorting_criterion')

    # Logging for debugging
    logging.debug(f"Sorting criterion: {sorting_criterion}")

    if sorting_criterion == 'Date Added - Ascending':
        sorted_tracks = sorted(combined, key=lambda x: x[1])
    elif sorting_criterion == 'Date Added - Descending':
        sorted_tracks = sorted(combined, key=lambda x: x[1], reverse=True)
    elif sorting_criterion == 'Release Date - Ascending':
        sorted_tracks = sorted(combined, key=lambda x: (x[2] is None, x[2]))  # Prioritize non-None values
    elif sorting_criterion == 'Release Date - Descending':
        sorted_tracks = sorted(combined, key=lambda x: (x[2] is None, x[2]), reverse=True)
    elif sorting_criterion == 'Random Shuffle':
        random.shuffle(combined)
        sorted_tracks = combined
    else:
        return jsonify(error="Invalid sorting criterion"), 400

    # Integrate local files back to the sorted list
    sorted_tracks.extend([(track['id'], track['added_at'], None) for track in local_files])

    sorted_track_ids = [item[0] for item in sorted_tracks]
    snapshot_id = playlist.snapshot_id

    original_positions = [track['id'] for track in playlist.tracks]

    for i, target_track_id in enumerate(sorted_track_ids):
        if target_track_id is None:  # Local track
            continue
        current_position = original_positions.index(target_track_id)
        if i != current_position:
            retries = 0
            success = False
            while retries < MAX_RETRIES and not success:
                try:
                    sp.playlist_reorder_items(playlist_id, range_start=current_position, insert_before=i,
                                              range_length=1, snapshot_id=snapshot_id)
                    original_positions.pop(current_position)
                    original_positions.insert(i, target_track_id)
                    snapshot_id = sp.playlist(playlist_id)['snapshot_id']
                    success = True
                except (RequestException, Exception) as e:
                    # Check for rate limits
                    if isinstance(e, RequestException) and e.response.status_code == 429:
                        retry_after = int(e.response.headers.get('Retry-After', RETRY_WAIT_SECONDS))
                        sleep(retry_after)
                        continue
                    retries += 1
                    if retries < MAX_RETRIES:
                        sleep(RETRY_WAIT_SECONDS)
                    else:
                        return jsonify(
                            error=f"Failed to reorder track after {MAX_RETRIES} attempts. Error: {str(e)}"), 500

    logging.debug(f"Final sorted track IDs: {sorted_track_ids}")

    return jsonify(status="Playlist reordered successfully"), 200
