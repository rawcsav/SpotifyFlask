import os
from datetime import datetime

from flask import Blueprint, render_template, session, request, jsonify, send_from_directory

from app.database import Songfull, PastGame, db, CurrentGame
from app.util.session_utils import check_login_status, verify_session, fetch_user_data

bp = Blueprint('songfull', __name__)

CLIPS_DIR = os.getenv('CLIPS_DIR')


@bp.route('/songfull')
def game():
    logged_in = check_login_status()
    user_id_or_session = session['id']  # default to session ID

    if logged_in:
        access_token = verify_session(session)
        res_data = fetch_user_data(access_token)
        songfull_menu = False
        user_id_or_session = res_data.get("id")
    else:
        songfull_menu = True
        res_data = None

    current_game = CurrentGame.query.get(user_id_or_session)
    if not current_game:
        current_game = CurrentGame(user_id_or_session=user_id_or_session)
        db.session.add(current_game)
        db.session.commit()

    # Load or create PastGame
    past_game = PastGame.query.get(user_id_or_session)
    if not past_game:
        past_game = PastGame(user_id_or_session=user_id_or_session)
        db.session.add(past_game)
        db.session.commit()

    return render_template('songfull.html', songfull_menu=songfull_menu, data=res_data)


genre_sequence = {1: 'General', 2: 'Rock', 3: 'Hip Hop'}


@bp.route('/start', methods=['POST'])
def start_game():
    if not session.get('selected_songs'):  # if there are no songs selected yet
        try:
            current_songs = Songfull.query.filter(Songfull.current > 0).order_by(Songfull.current).all()

            session['selected_songs'] = [song.id for song in current_songs]
            session['guesses_left'] = 6
            session['current_clip_length'] = 0.5

            first_song = Songfull.query.get(session['selected_songs'][0])
            session['current_genre'] = genre_sequence[first_song.current]

            return jsonify({
                'song_id': session['selected_songs'][0],
                'clip_length': session['current_clip_length'],
                'current_genre': session['current_genre']  # make sure to include this
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        try:
            next_song_id = session['selected_songs'][0]
            next_song = Songfull.query.get(next_song_id)

            session['current_genre'] = genre_sequence[next_song.current]

            return jsonify({
                'song_id': next_song_id,
                'clip_length': session['current_clip_length'],
                'current_genre': session['current_genre'],
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@bp.route('/clip/<string:song_id>', methods=['GET'])
def get_clip(song_id):
    try:
        file_name = f"{song_id}.mp3"
        print(f"CLIPS_DIR: {CLIPS_DIR}")
        print(f"File path: {os.path.join(CLIPS_DIR, file_name)}")

        if not os.path.exists(os.path.join(CLIPS_DIR, file_name)):
            return jsonify({'error': 'Clip not found'}), 404

        return send_from_directory(CLIPS_DIR, file_name)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/guess', methods=['POST'])
def submit_guess():
    try:
        user_guess = request.form['song_guess']
        current_song = Songfull.query.get(session['selected_songs'][0])

        # Fetch the PastGame record
        past_game = PastGame.query.filter_by(user_id_or_session=session['id']).first()

        if (user_guess.lower() == current_song.name.lower() or
                user_guess.lower() == f"{current_song.name} - {current_song.artist}".lower() or
                user_guess.lower() == current_song.id.lower()):

            # Update the correct guess stats
            if session['current_genre'] == 'General':
                past_game.correct_guess_general = True
            elif session['current_genre'] == 'Rock':
                past_game.correct_guess_rock = True
            elif session['current_genre'] == 'Hip Hop':
                past_game.correct_guess_hiphop = True

            return jsonify({'status': 'correct', 'next_song_id': session['selected_songs'][0]})
        else:
            session['guesses_left'] -= 1

            # Update the attempts made stats
            if session['current_genre'] == 'General':
                past_game.attempts_made_general += 1
            elif session['current_genre'] == 'Rock':
                past_game.attempts_made_rock += 1
            elif session['current_genre'] == 'Hip Hop':
                past_game.attempts_made_hiphop += 1

            db.session.commit()
            if session['guesses_left'] == 0:
                session['selected_songs'].pop(0)

                if not session['selected_songs']:
                    return jsonify({'status': 'lose'})

                next_song = Songfull.query.get(session['selected_songs'][0])
                session['guesses_left'] = 6
                session['current_genre'] = genre_sequence[next_song.current]

                session['current_clip_length'] += 5
                return jsonify({
                    'status': 'wrong',
                    'clip_length': session['current_clip_length'],
                    'song_id': next_song.id,
                    'guesses_left': session['guesses_left'],
                    'current_genre': session['current_genre']  # make sure to include this

                })

            session['current_clip_length'] += 5
            return jsonify({
                'status': 'wrong',
                'clip_length': session['current_clip_length'],
                'song_id': session['selected_songs'][0],
                'guesses_left': session['guesses_left'],
                'current_genre': session['current_genre']
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/archive', methods=['GET'])
def get_archive():
    past_games = PastGame.query.all()
    return jsonify({'archive': [game.to_dict() for game in past_games]})


@bp.route('/bonus', methods=['POST'])
def submit_bonus():
    try:
        album_guess = request.form['album_guess']
        release_year_guess = request.form['release_year_guess']

        current_song = Songfull.query.get(session['selected_songs'][0])

        correct_album = current_song.album.lower() == album_guess.lower()
        correct_release_year = current_song.release.lower() == release_year_guess.lower()

        session['selected_songs'].pop(0)

        if not session['selected_songs']:
            return jsonify({'status': 'win'})

        next_song = Songfull.query.get(session['selected_songs'][0])
        session['guesses_left'] = 6
        session['current_genre'] = genre_sequence[next_song.current]

        return jsonify({
            'status': 'correct',
            'next_song_id': next_song.id,
            'correct_album': correct_album,
            'correct_release_year': correct_release_year,
            'current_genre': session['current_genre'],
            'guesses_left': session['guesses_left']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
