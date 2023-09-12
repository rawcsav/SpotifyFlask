import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

# Application Secret Key
SECRET_KEY = os.getenv('SECRET_KEY')

# Spotify API details
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

# Spotify API endpoints
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
ME_URL = 'https://api.spotify.com/v1/me'
MAIN_USER_DIR = 'app/user_data_dir'

SECRET_KEY = os.urandom(24)
SESSION_TYPE = "filesystem"
SESSION_PERMANENT = True
PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
