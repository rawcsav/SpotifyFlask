import json

from flask import Blueprint, request, session
from spotipy import Spotify
from spotipy.exceptions import SpotifyException

bp = Blueprint('search', __name__)


@bp.route('/search', methods=['POST'])
def search():
    query = request.json.get('query')
    type = request.json.get('type')
    if not query:
        return json.dumps({'error': 'No search query provided'}), 400
    access_token = session['tokens'].get('access_token')
    sp = Spotify(auth=access_token)
    try:
        results = sp.search(q=query, type=type, limit=5)
        return json.dumps(results)
    except SpotifyException as e:
        return json.dumps({'error': str(e)}), 400


@bp.route('/genres', methods=['GET'])
def genres():
    # Check if genres are already in session
    if 'genre_seeds' in session:
        return json.dumps(session['genre_seeds'])

    access_token = session['tokens'].get('access_token')
    sp = Spotify(auth=access_token)
    genres = sp.recommendation_genre_seeds()

    # Store the genres in session for future use
    session['genre_seeds'] = genres

    return json.dumps(genres)
