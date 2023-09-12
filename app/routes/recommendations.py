import json

from flask import Blueprint, jsonify, render_template, request, session
from spotipy import Spotify

from .auth import refresh

bp = Blueprint('recommendations', __name__)


@bp.route('/recommendations', methods=['GET'])
def recommendations():
    # This route will just render the template
    return render_template('recommendations.html')


@bp.route('/get_recommendations', methods=['GET', 'POST'])
def get_recommendations():
    access_token = session['tokens'].get('access_token')
    if not access_token:
        refresh_response = json.loads(refresh())
        if 'error' in refresh_response:
            return json.dumps({'error': 'Failed to refresh token'}), 401
        access_token = refresh_response['access_token']

    sp = Spotify(auth=access_token)
    if request.method == 'POST':
        tracks = [track.strip() for track in request.form.get('track_seeds', '').split(',') if track.strip()]
        artists = [artist.strip() for artist in request.form.get('artist_seeds', '').split(',') if artist.strip()]
        genres = [genre.strip() for genre in request.form.get('genre_seeds', '').split(',') if genre.strip()]

        seed_tracks = tracks if tracks else None
        seed_artists = artists if artists else None
        seed_genres = genres if genres else None

        limit = request.form.get('limit', 5)
        popularity_min, popularity_max = map(int, request.form.get('popularity_slider').split(','))
        energy_min, energy_max = map(float, request.form.get('energy_slider').split(','))
        instrumentalness_min, instrumentalness_max = map(float, request.form.get('instrumentalness_slider').split(','))
        tempo_min, tempo_max = map(float, request.form.get('tempo_slider').split(','))
        danceability_min, danceability_max = map(float, request.form.get('danceability_slider').split(','))
        valence_min, valence_max = map(float, request.form.get('valence_slider').split(','))
        print("Seed Tracks:", seed_tracks)
        print("Seed Artists:", seed_artists)
        print("Seed Genres:", seed_genres)

        recommendations = sp.recommendations(
            seed_tracks=seed_tracks,
            seed_artists=seed_artists,
            seed_genres=seed_genres,
            limit=limit,
            min_popularity=popularity_min,
            max_popularity=popularity_max,
            min_energy=energy_min,
            max_energy=energy_max,
            min_instrumentalness=instrumentalness_min,
            max_instrumentalness=instrumentalness_max,
            min_danceability=danceability_min,
            max_danceability=danceability_max,
            min_valence=valence_min,
            max_valence=valence_max,
            min_tempo=tempo_min,
            max_tempo=tempo_max,
            market='US',
        )

    track_info_list = []
    for track in recommendations['tracks']:
        track_info = {
            'trackid': track['id'],
            'artistid': track['artists'][0]['id'] if track['artists'] else None,
            'preview': track['preview_url'],
            'cover_art': track['album']['images'][0]['url'] if track['album']['images'] else None,
            'artist': track['artists'][0]['name'],
            'trackName': track['name'],
            'trackUrl': track['external_urls']['spotify'],
            'albumName': track['album']['name'],
        }
        track_info_list.append(track_info)

    return jsonify({'recommendations': track_info_list})
