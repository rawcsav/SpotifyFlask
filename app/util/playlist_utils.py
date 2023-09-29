from app.util.database_utils import get_or_fetch_artist_info, get_or_fetch_audio_features


def get_playlist_details(sp, playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    next_page = results['next']

    while next_page:
        results = sp.next(results)
        tracks.extend(results['items'])
        next_page = results['next']

    track_ids = [track_data['track']['id'] for track_data in tracks]
    track_features_dict = get_or_fetch_audio_features(sp, track_ids)

    track_info_list = []
    artist_ids = []

    for track_data in tracks:
        track = track_data['track']
        track_id = track['id']
        artists = track['artists']

        artist_info = []
        for artist in artists:
            artist_ids.append(artist['id'])
            artist_info.append(get_or_fetch_artist_info(sp, artist['id']))

        audio_features = track_features_dict.get(track_id, {})

        track_info = {
            'id': track_id,
            'name': track['name'],
            'popularity': track['popularity'],
            'album': track['album']['name'],
            'release_date': track['album']['release_date'],
            'explicit': track['explicit'],
            'artists': artist_info,
            'audio_features': audio_features  # Incorporating audio features
        }

        track_info_list.append(track_info)

    return track_info_list
