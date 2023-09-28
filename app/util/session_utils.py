import json
import os
import secrets
import shutil
import string
from flask import abort

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
def store_to_json(user_data, json_path):
    with open(json_path, "w") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=4)


# Load User Data from JSON


def load_from_json(json_path):
    if not os.path.exists(json_path):
        return None
    with open(json_path, "r") as f:
        return json.load(f)


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
