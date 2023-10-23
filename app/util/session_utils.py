import os
import secrets
import string
from datetime import timezone, timedelta

import openai
import requests
import sshtunnel
from cryptography.fernet import Fernet
from flask import abort, session
from app import config


def verify_session(session):
    if "tokens" not in session:
        abort(400)
    return session["tokens"].get("access_token")


def fetch_user_data(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    res = requests.get(config.ME_URL, headers=headers)
    if res.status_code != 200:
        abort(res.status_code)
        
    spotify_user_id = res.get("id")
    spotify_user_display_name = res.get("display_name")

    session["DISPLAY_NAME"] = spotify_user_display_name
    session["USER_ID"] = spotify_user_id
    return res.json()


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


def convert_utc_to_est(utc_time):
    return utc_time.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=-4)))


def load_key_from_env():
    return os.environ["CRYPT_KEY"].encode()


def encrypt_data(data):
    CRYPT_KEY = load_key_from_env()
    cipher_suite = Fernet(CRYPT_KEY)
    encrypted_data = cipher_suite.encrypt(data.encode())
    return encrypted_data


def decrypt_data(encrypted_data):
    CRYPT_KEY = load_key_from_env()
    cipher_suite = Fernet(CRYPT_KEY)
    decrypted_data = cipher_suite.decrypt(encrypted_data)
    return decrypted_data.decode()


def is_api_key_valid(api_key):
    openai.api_key = api_key

    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt="This is a test.",
            max_tokens=5
        )
    except:
        return False
    else:
        return True


def get_tunnel():
    tunnel = sshtunnel.SSHTunnelForwarder(
        (config.SSH_HOST),
        ssh_username=config.SSH_USER,
        ssh_password=config.SSH_PASS,
        remote_bind_address=(
            config.SQL_HOSTNAME, 3306)
    )
    tunnel.start()
    return tunnel


def check_login_status():
    return 'tokens' in session
