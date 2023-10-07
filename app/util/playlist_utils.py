import json

from app.util.database_utils import get_or_fetch_artist_info, get_or_fetch_audio_features, playlist_sql, db
from datetime import datetime
from collections import defaultdict
from flask import session

from app.util.spotify_utils import init_session_client


def get_playlist_info(sp, playlist_id):
    playlist = sp.playlist(playlist_id)

    playlist_info = {
        "id": playlist["id"],
        "name": playlist["name"],
        "owner": playlist["owner"]["display_name"],
        "cover_art": playlist["images"][0]["url"] if playlist["images"] else None,
        "public": playlist["public"],
        "collaborative": playlist["collaborative"],
        "total_tracks": playlist["tracks"]["total"],
        "snapshot_id": playlist["snapshot_id"],
    }

    return playlist_info


def get_playlist_tracks(sp, playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    next_page = results['next']

    while next_page:
        results = sp.next(results)
        tracks.extend(results['items'])
        next_page = results['next']

    return tracks


def get_track_info_list(sp, tracks):
    track_ids = [track_data['track']['id'] for track_data in tracks if track_data['track']['id'] is not None]
    track_features_dict = get_or_fetch_audio_features(sp, track_ids)
    track_info_list = []

    # Pre-fetch all artist info at once to minimize API calls.
    unique_artist_ids = list(set(
        artist['id'] for track_data in tracks for artist in track_data['track']['artists'] if artist['id'] is not None))
    all_artist_info = get_or_fetch_artist_info(sp, unique_artist_ids)

    for track_data in tracks:
        track = track_data['track']

        # Remove unwanted columns
        track.pop('available_markets', None)
        track.pop('disc_number', None)
        track.pop('external_ids', None)
        track.pop('href', None)
        track.pop('linked_from', None)
        track.pop('restrictions', None)

        artists = track['artists']
        image = track['album'].get('images', [])
        cover_art = image[0].get('url') if image else None

        artist_info = []
        for artist in artists:
            artist_id = artist['id']
            if artist_id is not None and artist_id in all_artist_info:
                artist_info.append(all_artist_info[artist_id])
        audio_features = track_features_dict.get(track['id'], {})
        is_local = track.get('is_local', False)  # Extracting the is_local attribute

        track_info = {
            'id': track['id'],
            'name': track['name'],
            'is_local': is_local,
            'added_at': track_data.get('added_at', None),  # Adding the "added_at" field
            'album': track['album']['name'],
            'release_date': track['album']['release_date'],
            'explicit': track['explicit'],
            'popularity': None if is_local else track['popularity'],  # Set to None if track is local
            'cover_art': cover_art,
            'artists': artist_info,
            'audio_features': audio_features,
        }

        track_info_list.append(track_info)

    return track_info_list


def get_genre_artists_count(track_info_list, top_n=10):
    genre_info = {}  # Will store both counts and artist lists for each genre
    artist_counts = {}
    artist_images = {}
    artist_urls = {}
    artist_ids = {}  # New dictionary to store artist IDs

    for track_info in track_info_list:
        for artist_dict in track_info['artists']:
            artist_id = artist_dict.get('id')
            artist_name = artist_dict.get('name')
            artist_genres = artist_dict.get('genres', [])
            spotify_url = f"https://open.spotify.com/artist/{artist_id}"

            try:
                artist_image_url = artist_dict.get('images', [{}])[0].get('url')
            except IndexError:
                artist_image_url = None

            for genre in artist_genres:
                # Initialize genre info if it's not present
                if genre not in genre_info:
                    genre_info[genre] = {"count": 0, "artists": set()}

                # Increment genre count and add artist
                genre_info[genre]["count"] += 1
                genre_info[genre]["artists"].add(artist_name)

            artist_counts[artist_name] = artist_counts.get(artist_name, 0) + 1
            artist_ids[artist_name] = artist_id  # Store the artist ID

            if artist_image_url:
                artist_images[artist_name] = artist_image_url

            artist_urls[artist_name] = spotify_url

    sorted_artists = sorted(artist_counts.items(), key=lambda x: x[1], reverse=True)
    top_artists = [(name, count, artist_images.get(name, None), artist_urls.get(name), artist_ids.get(name)) for
                   name, count in sorted_artists[:top_n]]

    # Convert genre_info artists sets back to lists for consistency
    for genre, info in genre_info.items():
        info["artists"] = list(info["artists"])

    return genre_info, top_artists


def get_audio_features_stats(track_info_list):
    audio_feature_stats = {feature: {'min': None, 'max': None, 'total': 0} for feature in
                           track_info_list[0]['audio_features'].keys() if feature != 'id'}
    audio_feature_stats['popularity'] = {'min': None, 'max': None, 'total': 0}

    for idx, track_info in enumerate(track_info_list):
        if track_info['is_local'] or track_info['popularity'] is None:
            continue  # Skip local tracks and tracks with 'None' popularity

        for feature, value in track_info['audio_features'].items():
            if feature != 'id':
                try:
                    if audio_feature_stats[feature]['min'] is None or value < audio_feature_stats[feature]['min'][1]:
                        audio_feature_stats[feature]['min'] = (track_info['name'], value)
                    if audio_feature_stats[feature]['max'] is None or value > audio_feature_stats[feature]['max'][1]:
                        audio_feature_stats[feature]['max'] = (track_info['name'], value)
                    audio_feature_stats[feature]['total'] += value
                except KeyError:
                    print(
                        f"KeyError at track index {idx}, track name: {track_info['name']}, missing feature: {feature}")
                    continue

        # Calculate min, max, and total for popularity
        pop = track_info['popularity']
        if audio_feature_stats['popularity']['min'] is None or pop < audio_feature_stats['popularity']['min'][1]:
            audio_feature_stats['popularity']['min'] = (track_info['name'], pop)
        if audio_feature_stats['popularity']['max'] is None or pop > audio_feature_stats['popularity']['max'][1]:
            audio_feature_stats['popularity']['max'] = (track_info['name'], pop)
        audio_feature_stats['popularity']['total'] += pop

    for feature, stats in audio_feature_stats.items():
        stats['avg'] = stats['total'] / len(
            [track for track in track_info_list if not track['is_local'] and track['popularity'] is not None])

    return audio_feature_stats


def get_temporal_stats(track_info_list, playlist_id):
    if not track_info_list:
        return {}

    def parse_date_or_default(track, default):
        release_date = track['release_date']
        if release_date:
            return datetime.strptime(release_date, "%Y") if len(release_date) == 4 \
                else datetime.strptime(release_date, "%Y-%m-%d")
        return default

    valid_tracks = [track for track in track_info_list if track.get('id') and not track.get('is_local')]

    if not valid_tracks:
        return {}  # return empty dict if no valid tracks

    oldest_track = min(valid_tracks, key=lambda x: parse_date_or_default(x, datetime.min))
    newest_track = max(valid_tracks, key=lambda x: parse_date_or_default(x, datetime.max))

    year_count = defaultdict(int)

    for track in track_info_list:
        if track['release_date']:
            year = track['release_date'].split('-')[0]
            decade = year[:-1] + "0s"  # truncate the last digit and append "0s" for the decade representation
            year_count[decade] += 1

    temporal_stats = {
        'oldest_track': oldest_track['name'],
        'newest_track': newest_track['name'],
        'oldest_track_date': oldest_track['release_date'],
        'newest_track_date': newest_track['release_date'],
        'oldest_track_image': oldest_track["cover_art"],
        'newest_track_image': newest_track["cover_art"],
        'oldest_track_artist': oldest_track['artists'][0]['name'] if oldest_track['artists'] else 'Unknown',
        'newest_track_artist': newest_track['artists'][0]['name'] if newest_track['artists'] else 'Unknown',
        "year_count": year_count
    }
    return temporal_stats


def get_playlist_details(sp, playlist_id):
    playlist_info = get_playlist_info(sp, playlist_id)
    tracks = get_playlist_tracks(sp, playlist_id)
    track_info_list = get_track_info_list(sp, tracks)
    genre_counts, top_artists = get_genre_artists_count(track_info_list)
    audio_feature_stats = get_audio_features_stats(track_info_list)
    temporal_stats = get_temporal_stats(track_info_list, playlist_id)

    return playlist_info, track_info_list, genre_counts, top_artists, audio_feature_stats, temporal_stats


def update_playlist_data(playlist_id):
    sp, error = init_session_client(session)
    if error:
        return json.dumps(error), 401

    playlist = playlist_sql.query.get(playlist_id)
    if not playlist:
        return "Playlist not found", 404

    # Fetch the new data
    pl_playlist_info, pl_track_data, pl_genre_counts, pl_top_artists, \
        pl_feature_stats, pl_temporal_stats = get_playlist_details(sp, playlist_id)

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

    return "Playlist updated successfully"


def get_sp_genre_seeds(sp):
    global genre_seeds
    if 'genre_seeds' not in globals():
        genre_seeds = sp.recommendation_genre_seeds()  # Assuming sp is your Spotipy client
    return genre_seeds


def get_artists_seeds(artist_counts, artist_ids, top_n=5):
    sorted_artists = sorted(artist_counts.items(), key=lambda x: x[1], reverse=True)
    return [artist_ids[artist[0]] for artist in sorted_artists[:min(top_n, len(sorted_artists))]]


def get_genres_seeds(sp, genre_info, top_n=10):
    genre_seeds_dict = get_sp_genre_seeds(sp)
    genre_seeds = genre_seeds_dict['genres']

    valid_genres = []
    for genre, count in sorted(genre_info.items(), key=lambda x: x[1]['count'], reverse=True)[:top_n]:
        sanitized_genre = genre.strip().lower()

        # Check for direct match
        if sanitized_genre in genre_seeds:
            valid_genres.append(sanitized_genre)
            continue

        # Check for space-hyphen replacement
        hyphenated_genre = sanitized_genre.replace(" ", "-")
        if hyphenated_genre in genre_seeds:
            valid_genres.append(hyphenated_genre)
            continue

        # Check for hyphen-space replacement
        spaced_genre = sanitized_genre.replace("-", " ")
        if spaced_genre in genre_seeds:
            valid_genres.append(spaced_genre)

    print(valid_genres)
    return valid_genres[:2]  # Return top 2 valid genres
