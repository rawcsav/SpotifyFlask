import json
import os

from flask import Blueprint, session, render_template, jsonify

bp = Blueprint('stats', __name__)


@bp.route('/stats')
def stats():
    user_directory = session["UPLOAD_DIR"]
    json_path = os.path.join(user_directory, 'user_data.json')

    if not os.path.exists(json_path):
        return jsonify(error="User data not found"), 404

    with open(json_path, 'r') as f:
        user_data = json.load(f)

    top_tracks = user_data['top_tracks']
    top_artists = user_data['top_artists']
    sorted_genres_by_period = user_data['sorted_genres']
    genre_specific_data = user_data['genre_specific_data']

    return render_template('stats.html',
                           top_tracks=top_tracks,
                           top_artists=top_artists,
                           sorted_genres=sorted_genres_by_period,
                           genre_specific_data=genre_specific_data,
                           user_data=user_data)
