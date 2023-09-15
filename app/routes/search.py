import json

import openai as novaai
from flask import Blueprint, request, session
from fuzzywuzzy import process
from spotipy import Spotify
from spotipy.exceptions import SpotifyException

from app import config

bp = Blueprint('search', __name__)

novaai.api_base = 'https://api.nova-oss.com/v1'
novaai.api_key = config.NOVAAI_API_KEY


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


@bp.route('/genres', methods=['POST'])
def search_genres():
    query = request.json.get("query")

    # Fetch genres from Spotify
    if 'genre_seeds' not in session:
        access_token = session['tokens'].get('access_token')
        sp = Spotify(auth=access_token)
        genres = sp.recommendation_genre_seeds()
        session['genre_seeds'] = genres
    else:
        genres = session['genre_seeds']

    genre_seeds = genres['genres']

    try:
        response = novaai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system",
                 "content": f"You are a helpful search assistant that provides the top 10-15 most related genre seeds to a given user query. These are the genres you must choose from: {genre_seeds} Answer only with the exact names of related genres from this list, nothing else. Under no circumstances can you list a genre that is not on the list."},
                {"role": "user", "content": "dance"},
                {"role": "assistant",
                 "content": "dance, edm, electro, club, techno, trance, house, electronic, disco, breakbeat, dubstep"},
                {"role": "user", "content": query}
            ],
            temperature=0,
            max_tokens=100,
        )

        related_genres = response["choices"][0]["message"]["content"].split(", ")
        best_matches = [process.extractOne(related, genre_seeds)[0] for related in related_genres]
        return json.dumps({"genres": best_matches})

    except Exception as e:
        print(e)  # Print any exceptions for debugging
        return json.dumps({'error': 'Error processing request'}), 500
