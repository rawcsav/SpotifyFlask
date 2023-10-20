from random import random

from flask import session

from app.database import Songfull, PastGame, db

import subprocess


def trim_audio(input_path, output_path, clip_length):
    subprocess.run([
        "ffmpeg", "-i", input_path, "-ss", "0", "-t", str(clip_length), output_path
    ])


import requests


def download_song(url, path):
    response = requests.get(url)
    response.raise_for_status()  # Ensure we got a successful response

    with open(path, 'wb') as f:
        f.write(response.content)


class GameSession:
    @staticmethod
    def start(genre=None):
        song = GameSession.random_song_from_db(genre)
        session['current_song_id'] = song.id
        session['attempts'] = 0
        session['clip_duration'] = 0.1

    @staticmethod
    def random_song_from_db(genre=None):
        if genre:
            songs = Songfull.query.filter_by(genre=genre).all()
        else:
            songs = Songfull.query.all()

        if songs:
            return random.choice(songs)
        return None

    @staticmethod
    def increase_clip_duration():
        session['clip_duration'] = min(session['clip_duration'] * 2, 30)  # max 30 seconds

    @staticmethod
    def guess(song_name):
        session['attempts'] += 1
        current_song = Songfull.query.get(session['current_song_id'])

        if song_name == current_song.name:
            return True
        if session['attempts'] < 7:
            GameSession.increase_clip_duration()
            return False
        return None  # Game over (no more attempts)

    @staticmethod
    def archive_game(user_id, correct):
        past_game = PastGame(
            user_id=user_id,
            song_id=session['current_song_id'],
            attempts_made=session['attempts'],
            correct_guess=correct
        )
        try:
            db.session.add(past_game)
            db.session.commit()
        except:
            db.session.rollback()
            raise
