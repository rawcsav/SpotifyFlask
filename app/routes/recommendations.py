import json

from flask import Blueprint, jsonify, render_template, request, session

from app.util.spotify_utils import init_session_client, get_recommendations, format_track_info

bp = Blueprint('recommendations', __name__)


def parse_seeds(key):
    return [item.strip() for item in request.form.get(f"{key}_seeds", '').split(',') if item.strip()] or None


@bp.route('/recommendations', methods=['GET'])
def recommendations():
    return render_template('recommendations.html')


@bp.route('/get_recommendations', methods=['GET', 'POST'])
def get_recommendations_route():
    sp, error = init_session_client(session)
    if error:
        return json.dumps(error), 401

    if request.method == 'POST':

        seeds = {key: [item.strip() for item in request.form.get(f"{key}_seeds", '').split(',') if item.strip()] or None
                 for key in ['track', 'artist', 'genre']}
        limit = request.form.get('limit', 5)
        sliders = {key: tuple(map(type_func, request.form.get(f"{key}_slider").split(','))) for key, type_func in
                   zip(['popularity', 'energy', 'instrumentalness', 'tempo', 'danceability', 'valence'],
                       [int, float, float, float, float, float])}

        recommendations_data = get_recommendations(sp, **seeds, limit=limit, **sliders, market='US')

        if 'error' in recommendations_data:
            return json.dumps(recommendations_data), 400

        track_info_list = [format_track_info(track) for track in recommendations_data['tracks']]
        return jsonify({'recommendations': track_info_list})
