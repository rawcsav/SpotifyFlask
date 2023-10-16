import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

# Spotify API details
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Spotify API endpoints
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
ME_URL = "https://api.spotify.com/v1/me"

MAIN_USER_DIR = "app/user_data_dir"

SECRET_KEY = os.getenv("SECRET_KEY")
SESSION_TYPE = "filesystem"
SESSION_PERMANENT = True
PERMANENT_SESSION_LIFETIME = timedelta(minutes=1440)

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Strict"

SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
SQL_ALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False

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

PARENT_GENRES = {
    'Rap_HipHop': ['rap', 'hip hop', 'trap', 'r&b', 'urban contemporary', 'drill', 'grime', 'underground hip hop',
                   'plugg'],
    'Country_Folk': ['country', 'folk', 'folk-pop', 'country road', 'modern country rock', 'outlaw country',
                     'americana', 'singer-songwriter', 'bluegrass'],
    'Ambient_Experimental': ['ambient', 'experimental_ambient', 'experimental', 'electronica', 'abstract', 'drone',
                             'soundtrack', 'video game music', 'noise'],
    'Classical_Opera': ['classical', 'opera', 'orchestra', 'symphony', 'neoclassicism', 'early music', 'baroque',
                        'minimalism', 'avant-garde'],
    'Dance_EDM': ['dance', 'edm', 'house', 'trance', 'electro house', 'techno', 'electronic', 'big room',
                  'deep house'],
    'Jazz_Blues': ['jazz', 'blues', 'rythym and boogie', 'swing', 'jazz fusion', 'bebop', 'big band',
                   'modern blues' 'blues rock'],
    'Rock': ['rock', 'hard rock', 'classic rock', 'metal', 'punk', 'alternative rock', 'grunge', 'indie rock',
             'post-punk'],
    'Funk': ['funk', 'disco', 'soul', 'funk rock', 'adult standards', 'deep funk', 'rare groove', 'deep motown',
             'classic soul'],
    'Reggae_World': ['reggae', 'world', 'ska', 'dancehall', 'dub', 'modern reggae', 'reggae fusion', 'reggae rock',
                     'afropop']
}

CLIPS_DIR = "app/data/clips"
