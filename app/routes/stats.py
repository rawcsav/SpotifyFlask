from collections import defaultdict

from flask import Blueprint, session, render_template, jsonify
from spotipy import Spotify

from app import cache

bp = Blueprint('stats', __name__)


@cache.memoize(timeout=3600)  # Cache the results for 1 hour
def get_top_tracks(access_token, period):
    sp = Spotify(auth=access_token)
    return sp.current_user_top_tracks(time_range=period, limit=50)


@cache.memoize(timeout=3600)  # Cache the results for 1 hour
def get_top_artists(access_token, period):
    sp = Spotify(auth=access_token)
    return sp.current_user_top_artists(time_range=period, limit=50)


@cache.memoize(timeout=3600)
def get_artists_info(access_token, batch):
    sp = Spotify(auth=access_token)
    return sp.artists(batch)


@bp.route('/stats')
def stats():
    access_token = session['tokens'].get('access_token')

    time_periods = ['short_term', 'medium_term', 'long_term']

    try:
        top_tracks = {period: get_top_tracks(access_token, period) for period in time_periods}
        top_artists = {period: get_top_artists(access_token, period) for period in time_periods}
    except Exception as e:
        # Handle the cache miss or any other exception
        return jsonify(error=str(e)), 500

    artist_id_freq = defaultdict(int)
    for period, tracks in top_tracks.items():
        for track in tracks['items']:
            for artist in track['artists']:
                artist_id_freq[artist['id']] += 1

    all_artists_info = {}
    artist_ids = list(artist_id_freq.keys())
    for i in range(0, len(artist_ids), 50):
        batch = artist_ids[i:i + 50]
        try:
            artists_info = get_artists_info(access_token, batch)
            for artist in artists_info['artists']:
                all_artists_info[artist['id']] = artist
        except Exception as e:
            # Handle the cache miss or any other exception
            return jsonify(error=str(e)), 500

    # Create a dictionary to store artist frequencies for each genre
    genre_artist_freq = defaultdict(lambda: defaultdict(int))

    # Populate the dictionary
    for artist_id, artist_info in all_artists_info.items():
        for genre in artist_info.get('genres', []):
            genre_artist_freq[genre][artist_id] += artist_id_freq[artist_id]

    # Determine the top 3 artists for each genre
    top_artists_for_genre = {}
    for genre, artists in genre_artist_freq.items():
        top_artists_for_genre[genre] = sorted(artists.keys(), key=lambda x: artists[x], reverse=True)[:3]

    # Convert artist IDs to artist info for rendering in the template
    for genre, artist_ids in top_artists_for_genre.items():
        top_artists_for_genre[genre] = [all_artists_info[artist_id] for artist_id in artist_ids]

    sorted_genres_by_period = {period: {} for period in time_periods}
    for period in time_periods:
        genre_counts = defaultdict(int)
        artist_freq = {artist['id']: 1 for artist in top_artists[period]['items']}
        for track in top_tracks[period]['items']:
            for artist in track['artists']:
                artist_freq[artist['id']] = artist_freq.get(artist['id'], 0) + 1
        for artist_id, freq in artist_freq.items():
            if artist_id in all_artists_info:
                artist_info = all_artists_info[artist_id]
                for genre in artist_info.get('genres', []):
                    if artist_id in [a['id'] for a in top_artists[period]['items']]:
                        freq *= 1.5
                    genre_counts[genre] += int(round(freq))
        sorted_genres_by_period[period] = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:20]

    return render_template('stats.html',
                           top_tracks=top_tracks,
                           top_artists=top_artists,
                           sorted_genres=sorted_genres_by_period,
                           top_artists_for_genre=top_artists_for_genre)
