from flask import Blueprint, request, jsonify
import json
from app.util.database_utils import validate_artist_data, validate_audio_data, \
    db, artist_sql, features_sql

bp = Blueprint('database', __name__)


@bp.route('/add_artist', methods=['POST'])
def add_artist():
    try:
        artist_data = request.json
        if not validate_artist_data(artist_data):
            return jsonify({'message': 'Missing required fields'}), 400

        new_artist = artist_sql(
            id=artist_data['id'],
            name=artist_data['name'],
            external_url=json.dumps(artist_data['external_urls']),
            followers=artist_data['followers']['total'],
            genres=json.dumps(artist_data['genres']),
            href=artist_data['href'],
            images=json.dumps(artist_data['images']),
            popularity=artist_data['popularity'],
        )
        db.session.add(new_artist)
        db.session.commit()
        return jsonify({'message': 'Artist added successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred: {}'.format(e)}), 500


@bp.route('/add_audio_features', methods=['POST'])
def add_audio_features():
    try:
        audio_data = request.json
        if not validate_audio_data(audio_data):
            return jsonify({'message': 'Missing required fields'}), 400

        new_audio_features = features_sql(**audio_data)
        db.session.add(new_audio_features)
        db.session.commit()
        return jsonify({'message': 'Audio features added successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred: {}'.format(e)}), 500
