from app.util.database_utils import get_or_fetch_artist_info, get_or_fetch_audio_features
from statistics import mean


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


#
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


def get_playlist_details(sp, playlist_id):
    tracks = get_playlist_tracks(sp, playlist_id)
    track_info_list = get_track_info_list(sp, tracks)
    genre_counts, top_artists = get_genre_artists_count(track_info_list)
    audio_feature_stats = get_audio_features_stats(track_info_list)

    return track_info_list, genre_counts, top_artists, audio_feature_stats
