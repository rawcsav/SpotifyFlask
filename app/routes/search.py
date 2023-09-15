from flask import Blueprint, request, session, json
from fuzzywuzzy import process

from app.util.session_utils import init_novaai_client, novaai_chat_completion
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


@bp.route('/genres', methods=['POST'])
def search_genres():
    query = request.json.get("query")
    if 'genre_seeds' not in session:
        access_token = session['tokens'].get('access_token')
        sp = init_spotify_client(access_token)
        genres = sp.recommendation_genre_seeds()
        session['genre_seeds'] = genres
    else:
        genres = session['genre_seeds']

    genre_seeds = genres['genres']
    init_novaai_client()
    response = novaai_chat_completion(genre_seeds, query)

    if 'error' in response:
        return json.dumps({'error': 'Error processing request'}), 500

    related_genres = response["choices"][0]["message"]["content"].split(", ")
    best_matches = [process.extractOne(related, genre_seeds)[0] for related in related_genres]
    return json.dumps({"genres": best_matches})
