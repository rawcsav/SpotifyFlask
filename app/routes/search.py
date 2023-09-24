from flask import Blueprint, request, session, json
from app.util.spotify_utils import init_spotify_client, spotify_search

bp = Blueprint('search', __name__)


@bp.route('/search', methods=['POST'])
def search():
    query = request.json.get('query')
    type = request.json.get('type')
    if not query:
        return json.dumps({'error': 'No search query provided'}), 400
    access_token = session['tokens'].get('access_token')
    sp = init_spotify_client(access_token)
    results = spotify_search(sp, query, type)
    return json.dumps(results)
