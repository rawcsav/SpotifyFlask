import os
from datetime import timedelta

from dotenv import load_dotenv

from app.util.database_utils import db

load_dotenv()

# Spotify API details
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Spotify API endpoints
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
ME_URL = "https://api.spotify.com/v1/me"

SECRET_KEY = os.getenv("SECRET_KEY")
FLASK_ENV = os.getenv("FLASK_ENV")

SESSION_TYPE = "sqlalchemy"
SESSION_PERMANENT = True
PERMANENT_SESSION_LIFETIME = timedelta(minutes=1440)

SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE")
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Strict"

SQL_ALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False
SQLALCHEMY_POOL_RECYCLE = 299

SSH_HOST = os.getenv("SSH_HOST")
SSH_USER = os.getenv("SSH_USER")
SSH_PASS = os.getenv("SSH_PASS")
SQL_HOSTNAME = os.getenv("SQL_HOSTNAME")
SQL_USERNAME = os.getenv("SQL_USERNAME")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")
SQL_DB_NAME = os.getenv("SQL_DB_NAME")

AUDIO_FEATURES = [
    "acousticness",
    "danceability",
    "energy",
    "instrumentalness",
    "liveness",
    "loudness",
    "speechiness",
    "tempo",
    "valence",
    "popularity",
]

REDIRECT_URL = "http://webstats.rawcsav.com/"

MAX_RETRIES = 3
RETRY_WAIT_SECONDS = 2
