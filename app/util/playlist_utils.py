from app.util.database_utils import get_or_fetch_artist_info, get_or_fetch_audio_features
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict
from flask import session
import os


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
        track_id = track['id']
        artists = track['artists']
        image = track['album'].get('images', [])
        cover_art = None

        if image:
            cover_art = image[0].get('url')

        artist_info = []
        for artist in artists:
            artist_id = artist['id']
            if artist_id is not None and artist_id in all_artist_info:
                artist_info.append(all_artist_info[artist_id])
        audio_features = track_features_dict.get(track_id, {})

        track_info = {
            'id': track_id,
            'name': track['name'],
            'popularity': track['popularity'],
            'album': track['album']['name'],
            'release_date': track['album']['release_date'],
            'explicit': track['explicit'],
            'cover_art': cover_art,
            'artists': artist_info,
            'audio_features': audio_features
        }

        track_info_list.append(track_info)

    return track_info_list


def get_genre_artists_count(track_info_list, top_n=10):
    genre_counts = {}
    artist_counts = {}
    artist_images = {}

    for track_info in track_info_list:
        for artist_dict in track_info['artists']:
            artist_id = artist_dict.get('id')
            artist_name = artist_dict.get('name')
            artist_genres = artist_dict.get('genres', [])
            try:
                artist_image_url = artist_dict.get('images', [{}])[0].get('url')
            except IndexError:
                artist_image_url = None

            for genre in artist_genres:
                genre_counts[genre] = genre_counts.get(genre, 0) + 1

            artist_counts[artist_name] = artist_counts.get(artist_name, 0) + 1

            if artist_image_url:
                artist_images[artist_name] = artist_image_url

    sorted_artists = sorted(artist_counts.items(), key=lambda x: x[1], reverse=True)
    top_artists = [(name, count, artist_images.get(name, None)) for name, count in sorted_artists[:top_n]]

    return genre_counts, top_artists


def get_audio_features_stats(track_info_list):
    audio_feature_stats = {feature: {'min': None, 'max': None, 'total': 0} for feature in
                           track_info_list[0]['audio_features'].keys() if feature != 'id'}

    for track_info in track_info_list:
        for feature, value in track_info['audio_features'].items():
            if feature != 'id':
                if audio_feature_stats[feature]['min'] is None or value < audio_feature_stats[feature]['min'][1]:
                    audio_feature_stats[feature]['min'] = (track_info['name'], value)
                if audio_feature_stats[feature]['max'] is None or value > audio_feature_stats[feature]['max'][1]:
                    audio_feature_stats[feature]['max'] = (track_info['name'], value)
                audio_feature_stats[feature]['total'] += value

    for feature, stats in audio_feature_stats.items():
        stats['avg'] = stats['total'] / len(track_info_list)

    return audio_feature_stats


def get_temporal_stats(track_info_list, playlist_id):
    if not track_info_list:
        return {}  # return empty dict if track_info_list is empty

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
    print(oldest_track)
    print(newest_track)

    year_count = defaultdict(int)

    for track in track_info_list:
        if track['release_date']:
            year = track['release_date'].split('-')[0]
            year_count[year] += 1

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
    tracks = get_playlist_tracks(sp, playlist_id)
    track_info_list = get_track_info_list(sp, tracks)
    genre_counts, top_artists = get_genre_artists_count(track_info_list)
    audio_feature_stats = get_audio_features_stats(track_info_list)
    temporal_stats = get_temporal_stats(track_info_list, playlist_id)

    return track_info_list, genre_counts, top_artists, audio_feature_stats, temporal_stats
