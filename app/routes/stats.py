from collections import defaultdict

from flask import Blueprint, session, render_template
from spotipy import Spotify

bp = Blueprint('stats', __name__)


@bp.route('/stats')
def stats():
    access_token = session['tokens'].get('access_token')
    sp = Spotify(auth=access_token)

    time_periods = ['short_term', 'medium_term', 'long_term']

    top_tracks = {period: sp.current_user_top_tracks(time_range=period, limit=50) for period in time_periods}
    top_artists = {period: sp.current_user_top_artists(time_range=period, limit=50) for period in time_periods}

    # Collect artist IDs from the top tracks and account for their frequency
    artist_id_freq = defaultdict(int)
    for period, tracks in top_tracks.items():
        for track in tracks['items']:
            for artist in track['artists']:
                artist_id_freq[artist['id']] += 1

    # Fetch detailed artist information using sp.artists() in batches
    all_artists_info = {}
    artist_ids = list(artist_id_freq.keys())

    for i in range(0, len(artist_ids), 50):
        batch = artist_ids[i:i + 50]
        artists_info = sp.artists(batch)
        for artist in artists_info['artists']:
            all_artists_info[artist['id']] = artist

    # Differentiate genres by period and sort them
    sorted_genres_by_period = {period: {} for period in time_periods}

    for period in time_periods:
        genre_counts = defaultdict(int)

        # Initialize artist frequencies. Every artist in top artists gets a frequency of 1.
        artist_freq = {artist['id']: 1 for artist in top_artists[period]['items']}

        # For each song in top tracks, increase the artist's frequency by 1.
        for track in top_tracks[period]['items']:
            for artist in track['artists']:
                artist_freq[artist['id']] = artist_freq.get(artist['id'], 0) + 1

        # Weight genres. If the artist is in top artists, multiply frequency by the weight.
        for artist_id, freq in artist_freq.items():
            if artist_id in all_artists_info:
                artist_info = all_artists_info[artist_id]
                for genre in artist_info.get('genres', []):
                    if artist_id in [a['id'] for a in top_artists[period]['items']]:
                        freq *= 1.5
                    genre_counts[genre] += int(round(freq))

        # Sort the genres by their frequency for the current period
        sorted_genres_by_period[period] = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:20]

    return render_template('stats.html',
                           top_tracks=top_tracks,
                           top_artists=top_artists,
                           sorted_genres=sorted_genres_by_period)
