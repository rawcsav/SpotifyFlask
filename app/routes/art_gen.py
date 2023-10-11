from datetime import datetime
from flask import Blueprint, request, send_from_directory, jsonify, session
import openai
from requests import RequestException
from app.util.art_gen_utils import generate_dalle_prompt, generate_images_dalle
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

        prompt = generate_dalle_prompt()

        # Generate the images
        images = generate_images_dalle(prompt)
        current_time = datetime.utcnow()

        for img_url in images:
            new_image_url = artgenurl_sql(
                url=img_url,
                playlist_id=playlist_id,
                timestamp=current_time,
            )
            db.session.add(new_image_url)
        db.session.commit()

        return {"images": images}, 200

    except RequestException:
        return jsonify(error="Error calling OpenAI"), 500
    except Exception as e:
        return jsonify(error="Internal server error"), 500


@bp.route('/images/<filename>')
def get_image(filename):
    directory = "images"
    return send_from_directory(directory, filename)
