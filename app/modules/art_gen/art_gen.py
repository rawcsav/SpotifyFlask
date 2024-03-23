from flask import Blueprint, request, send_from_directory, jsonify, session

from modules.art_gen.art_gen_util import generate_and_save_images
from modules.auth.auth import fetch_user_data
from modules.auth.auth_util import verify_session, create_openai_client

art_gen_bp = Blueprint("art_gen", __name__, template_folder="templates", static_folder="static")


@art_gen_bp.route("/generate_images/<string:playlist_id>", methods=["POST"])
def generate_images(playlist_id):
    max_retries = 3
    retries = 0
    refresh = request.json.get("refresh", False)
    quality = request.json.get("quality", "standard")  # Default to 'standard' if not provided
    genres_list = request.json.get("genres_list", [])  # Default to empty list if not provided

    while retries < max_retries:
        try:
            access_token = verify_session(session)
            res_data = fetch_user_data(access_token)
            spotify_user_id = res_data.get("id")
            client = create_openai_client(spotify_user_id)
            image_urls, revised_prompts = generate_and_save_images(
                playlist_id, spotify_user_id, client, refresh=refresh, quality=quality, genre_list=genres_list
            )
            image_and_prompts = [{"image": url, "prompt": prompt} for url, prompt in zip(image_urls, revised_prompts)]

            return jsonify({"images_and_prompts": image_and_prompts}), 200

        except Exception as e:
            print(e)
            if "content_policy_violation" in str(e).lower():
                retries += 1
                print(f"Retry {retries}/{max_retries} due to content policy violation.")
            else:
                return jsonify(error="Internal server error"), 500

    return jsonify(error="Failed to generate images after retries due to content policy violation."), 500


@art_gen_bp.route("/images/<filename>")
def get_image(filename):
    directory = "images"
    return send_from_directory(directory, filename)
