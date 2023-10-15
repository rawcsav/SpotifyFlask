from flask import Blueprint, render_template, jsonify, \
    session, redirect, url_for, request
import json
import random
import base64
import requests
from io import BytesIO
from PIL import Image
from app.routes.auth import require_spotify_auth
from app.util.database_utils import db, playlist_sql, UserData, delete_expired_images_for_playlist, genre_sql
from app.util.playlist_utils import get_playlist_details, update_playlist_data, get_artists_seeds, get_genres_seeds, \
    find_parent_genres
from app.util.session_utils import verify_session, fetch_user_data
from app.util.spotify_utils import init_session_client, format_track_info, get_recommendations

bp = Blueprint('playlist', __name__)


@bp.route('/playlist', methods=['GET'])
@require_spotify_auth
def playlist():
    spotify_user_id = session["USER_ID"]
    access_token = verify_session(session)
    res_data = fetch_user_data(access_token)

    # Retrieve the user's data entry from the database
    user_data_entry = UserData.query.filter_by(spotify_user_id=spotify_user_id).first()

    if not user_data_entry:
        return jsonify(error="User data not found"), 404

    page = request.args.get('page', 1, type=int)
    per_page = 10  # or any other desired value

    owner_name = session.get("DISPLAY_NAME")
    start = (page - 1) * per_page
    end = start + per_page
    playlists = [playlist for playlist in user_data_entry.playlist_info[start:end]
                 if playlist["owner"] is not None
                 and playlist["owner"] == owner_name]

    total_playlists = len(user_data_entry.playlist_info)
    total_pages = -(-total_playlists // per_page)  # This calculates the ceiling of division

    return render_template('playlist.html', data=res_data, playlists=playlists, page=page, total_pages=total_pages)


@bp.route('/playlist/<string:playlist_id>')
@require_spotify_auth
def show_playlist(playlist_id):
    delete_expired_images_for_playlist(playlist_id)

    playlist = playlist_sql.query.get(playlist_id)
    playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"
    access_token = verify_session(session)

    res_data = fetch_user_data(access_token)
    if playlist:
        playlist_data = playlist.__dict__
        owner_name = playlist_data['owner']
        total_tracks = playlist_data['total_tracks']
        is_collaborative = playlist_data['collaborative']
        is_public = playlist_data['public']
        temporal_stats = playlist_data.get('temporal_stats', {})
        year_count = temporal_stats.get('year_count', {})
        sorted_genre_data = sorted(playlist_data['genre_counts'].items(), key=lambda x: x[1]['count'], reverse=True)
        top_10_genre_data = dict(sorted_genre_data[:10])
        genre_info = {genre: data['count'] for genre, data in playlist_data['genre_counts'].items()}
        top_genre_stat = find_parent_genres(genre_info, genre_sql)
        top_genre_name = [genre for genre, distance in top_genre_stat]
        parent_genres = json.dumps(top_genre_name)

        return render_template('spec_playlist.html', playlist_id=playlist_id,
                               data=res_data,
                               playlist_url=playlist_url,
                               playlist_data=playlist_data,
                               top_10_genre_data=top_10_genre_data,
                               year_count=json.dumps(year_count), owner_name=owner_name, total_tracks=total_tracks,
                               is_collaborative=is_collaborative, is_public=is_public,
                               parent_genres=parent_genres)

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

    # Preprocess the genre_counts data in the Python route function
    sorted_genre_data = sorted(playlist_data['genre_counts'].items(), key=lambda x: x[1]['count'], reverse=True)
    top_10_genre_data = dict(sorted_genre_data[:10])
    genre_info = {genre: data['count'] for genre, data in playlist_data['genre_counts'].items()}
    top_genre_stat = find_parent_genres(genre_info, genre_sql)
    top_genre_name = [genre for genre, distance in top_genre_stat]
    parent_genres = json.dumps(top_genre_name)

    return render_template('spec_playlist.html', playlist_id=playlist_id,
                           data=res_data,
                           playlist_url=playlist_url,
                           playlist_data=playlist_data,
                           top_10_genre_data=top_10_genre_data,
                           year_count=json.dumps(year_count), owner_name=owner_name, total_tracks=total_tracks,
                           is_collaborative=is_collaborative, is_public=is_public,
                           parent_genres=parent_genres)


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


@bp.route('/playlist/<string:playlist_id>/reorder', methods=['POST'])
@require_spotify_auth
def reorder_playlist(playlist_id):
    sp, error = init_session_client(session)
    if error:
        return jsonify(error=error), 401

    playlist = playlist_sql.query.get(playlist_id)
    if not playlist:
        return jsonify(error="Playlist not found"), 404

    non_local_files = [track for track in playlist.tracks if track['id'] is not None]

    added_at_dates = [track['added_at'] for track in non_local_files]
    track_ids = [track['id'] for track in non_local_files]
    release_dates = [track['release_date'] for track in non_local_files]

    combined = list(zip(track_ids, added_at_dates, release_dates))
    sorting_criterion = request.json.get('sorting_criterion')

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

    sorted_track_ids = [item[0] for item in sorted_tracks]
    playlist_name = playlist.name
    user_id = session['USER_ID']
    new_playlist_name = f"Sorted {playlist_name}"
    new_playlist = sp.user_playlist_create(user_id, new_playlist_name)
    new_playlist_id = new_playlist['id']

    track_uris_to_add = [f"spotify:track:{track_id}" for track_id in sorted_track_ids if track_id is not None]

    for i in range(0, len(track_uris_to_add), 100):
        batch = track_uris_to_add[i:i + 100]
        try:
            sp.user_playlist_add_tracks(user_id, new_playlist_id, batch)
        except Exception as e:
            return jsonify(error=f"An error occurred while adding tracks: {str(e)}"), 500

    return jsonify(status="Playlist reordered successfully"), 200


@bp.route('/get_pl_recommendations/<string:playlist_id>/recommendations', methods=['POST'])
def get_pl_recommendations(playlist_id):
    print(f"playlist_id: {playlist_id}")  # Print the playlist_id

    sp, error = init_session_client(session)
    if error:
        print(f"error: {error}")  # Print the error
        return jsonify(error=error), 401

    playlist = playlist_sql.query.get(playlist_id)
    if not playlist:
        return jsonify(error="Playlist not found"), 404

    genre_info = playlist.genre_counts
    top_artists = playlist.top_artists

    artist_counts = {artist[0]: artist[1] for artist in top_artists}
    artist_ids = {artist[0]: artist[4] for artist in top_artists}
    print(f"artist_counts: {artist_counts}, artist_ids: {artist_ids}")  # Print the artist_counts and artist_ids

    top_artist_ids = get_artists_seeds(artist_counts, artist_ids)
    top_genres = get_genres_seeds(sp, genre_info)
    print(f"top_artist_ids: {top_artist_ids}, top_genres: {top_genres}")  # Print the top_artist_ids and top_genres

    num_artist_seeds = 5 - len(top_genres)
    print(f"num_artist_seeds: {num_artist_seeds}")  # Print the num_artist_seeds

    seeds = {
        'track': None,
        'artist': top_artist_ids[:num_artist_seeds],
        'genre': top_genres
    }

    recommendations_data = get_recommendations(
        sp, limit=10, market="US", **seeds
    )

    if "error" in recommendations_data:
        return json.dumps(recommendations_data), 400

    track_info_list = [
        format_track_info(track) for track in recommendations_data["tracks"]
    ]
    return jsonify({"recommendations": track_info_list})


@bp.route('/playlist/<string:playlist_id>/cover-art', methods=['POST'])
@require_spotify_auth
def change_cover_art(playlist_id):
    image_url = request.json.get('image_url')

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
        sp.playlist_upload_cover_image(playlist_id, img_base64.decode('utf-8'))

        return jsonify(status="Cover art updated successfully"), 200

    except Exception as e:
        return jsonify(error=str(e)), 500
