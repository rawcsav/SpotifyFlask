from datetime import datetime
from flask import Blueprint, request, send_from_directory, jsonify, session
import openai
from requests import RequestException
from app.util.art_gen_utils import generate_and_save_images
from app.util.database_utils import artgenurl_sql, db, UserData, playlist_sql
from app.util.session_utils import verify_session, fetch_user_data, decrypt_data

bp = Blueprint('art_gen', __name__)


@bp.route('/generate_images/<string:playlist_id>', methods=['POST'])
def generate_images(playlist_id):
    try:
        access_token = verify_session(session)
        res_data = fetch_user_data(access_token)
        spotify_user_id = res_data.get("id")

        user_data = UserData.query.filter_by(spotify_user_id=spotify_user_id).first()
        encrypted_api_key = user_data.api_key_encrypted

        api_key = decrypt_data(encrypted_api_key)

        openai.api_key = api_key

        # Check if genre is provided in the request data
        genre_name = request.json.get('genre_name', None)

        images, prompt = generate_and_save_images(playlist_id, genre_name)

        return {"images": images, "prompt": prompt}, 200
    except Exception as e:
        print(e)
        return jsonify(error="Internal server error"), 500


@bp.route('/images/<filename>')
def get_image(filename):
    directory = "images"
    return send_from_directory(directory, filename)
