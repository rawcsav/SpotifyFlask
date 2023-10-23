import openai
from flask import Blueprint, request, send_from_directory, jsonify, session

from app.database import UserData
from app.util.art_gen_utils import generate_and_save_images
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

        genres_list = request.json.get('genres_list', None)
        print(genres_list)
        prompt_text = request.json.get('prompt', None)

        images, prompt = generate_and_save_images(playlist_id, genres_list, prompt_text)

        return {"images": images, "prompt": prompt}, 200

    except Exception as e:
        print(e)
        return jsonify(error="Internal server error"), 500


@bp.route('/images/<filename>')
def get_image(filename):
    directory = "images"
    return send_from_directory(directory, filename)
