import json
import os
import secrets
import shutil
import string
from flask import abort

import openai as novaai
import requests

from app import config


def remove_directory(directory_path):
    if not os.path.exists(directory_path):
        print(f"The directory {directory_path} does not exist.")
        return
    shutil.rmtree(directory_path)
    print(f"The directory {directory_path} has been removed.")


def verify_session(session):
    if "tokens" not in session:
        abort(400)
    return session["tokens"].get("access_token")


def fetch_user_data(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    res = requests.get(config.ME_URL, headers=headers)
    if res.status_code != 200:
        abort(res.status_code)
    return res.json()


def manage_user_directory(spotify_user_id, session):
    session_dir = os.path.join(config.MAIN_USER_DIR, spotify_user_id)
    os.makedirs(session_dir, exist_ok=True)
    session["UPLOAD_DIR"] = session_dir
    return session_dir


# Store User Data to JSON
def replace_none_with_empty_str(obj):
    if isinstance(obj, dict):
        return {k: replace_none_with_empty_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_none_with_empty_str(x) for x in obj]
    elif obj is None:
        return ""
    else:
        return obj


def store_to_json(user_data, json_path):
    sanitized_data = replace_none_with_empty_str(user_data)
    with open(json_path, "w") as f:
        json.dump(sanitized_data, f, ensure_ascii=False, indent=4)


# Load User Data from JSON
def load_from_json(json_path):
    with open(json_path, "r") as f:
        return json.load(f)


def load_user_data(json_path):
    if not os.path.exists(json_path):
        return None
    with open(json_path, "r") as f:
        return json.load(f)


def init_novaai_client():
    novaai.api_base = config.NOVAAI_API_BASE
    novaai.api_key = config.NOVAAI_API_KEY


# NovaAI Chat Completion
def novaai_chat_completion(genre_seeds, query):
    try:
        return novaai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a helpful search assistant that provides the top 10-15 most related genre seeds to a given user query. These are the genres you must choose from: {genre_seeds} Answer only with the exact names of related genres from this list, nothing else. Under no circumstances can you list a genre that is not on the list.",
                },
                {"role": "user", "content": "dance"},
                {
                    "role": "assistant",
                    "content": "dance, edm, electro, club, techno, trance, house, electronic, disco, breakbeat, dubstep",
                },
                {"role": "user", "content": query},
            ],
            temperature=0,
            max_tokens=100,
        )
    except Exception as e:
        print(e)
        return {"error": "Error processing request"}


def generate_state():
    return "".join(
        secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16)
    )


def prepare_auth_payload(state, scope, show_dialog=False):
    payload = {
        "client_id": config.CLIENT_ID,
        "response_type": "code",
        "redirect_uri": config.REDIRECT_URI,
        "state": state,
        "scope": scope,
    }
    if show_dialog:
        payload["show_dialog"] = True
    return payload


def request_tokens(payload, client_id, client_secret):
    res = requests.post(config.TOKEN_URL, auth=(client_id, client_secret), data=payload)
    res_data = res.json()
    if res_data.get("error") or res.status_code != 200:
        return None, res.status_code
    return res_data, None
