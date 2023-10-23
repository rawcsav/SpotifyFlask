from flask import Blueprint, request, session, json, jsonify
from app import config
from app.util.spotify_utils import init_session_client, spotify_search

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

bp = Blueprint('search', __name__)


@bp.route('/search', methods=['POST'])
def search():
    query = request.json.get('query')
    type = request.json.get('type')
    if not query:
        return json.dumps({'error': 'No search query provided'}), 400
    sp, error = init_session_client(session)
    if error:
        return json.dumps(error), 401
    results = spotify_search(sp, query, type)
    return json.dumps(results)


@bp.route('/songfull_search', methods=['GET'])
def songfull_search():
    client_id = config.SEARCH_ID
    client_secret = config.SEARCH_SECRET
    query = request.args.get('query', '')
    if not query:
        return jsonify([])

    sp = spotipy.Spotify(
        client_credentials_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

    results = sp.search(q=query, type='track', limit=10)
    tracks = results['tracks']['items']

    songs = []
    for track in tracks:
        song_data = {
            "title": track['name'],
            "artist": track['artists'][0]['name'],
            "track_id": track['id'],
        }
        songs.append(song_data)

    return jsonify(songs)
