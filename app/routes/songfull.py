import os
from datetime import datetime

from flask import Blueprint, render_template, session, request, jsonify, send_from_directory

from app.database import Songfull, PastGame, db, CurrentGame, Archive
from app.util.session_utils import check_login_status, verify_session, fetch_user_data

bp = Blueprint('songfull', __name__)

CLIPS_DIR = os.getenv('CLIPS_DIR')

guess_duration_map = {6: 0.5, 5: 1, 4: 3, 3: 5, 2: 10, 1: 30};
genre_sequence = {1: 'General', 2: 'Rock', 3: 'Hip Hop'}


@bp.route('/songfull')
def game():
    logged_in = check_login_status()
    user_id_or_session = session['id']  # default to session ID
    today = datetime.utcnow().date()

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
        current_game = CurrentGame(user_id_or_session=user_id_or_session, date=today, archive_date=today)
        db.session.add(current_game)
        db.session.commit()

    # Load or create PastGame
    past_game = PastGame.query.filter_by(user_id_or_session=user_id_or_session, date=today).first()
    if not past_game:
        past_game = PastGame(user_id_or_session=user_id_or_session, date=today, archive_date=today)
        db.session.add(past_game)
        db.session.commit()

    return render_template('songfull.html', songfull_menu=songfull_menu, data=res_data)


@bp.route('/start', methods=['POST'])
def start_game():
    logged_in = check_login_status()
    user_id_or_session = session['id'] if not logged_in else fetch_user_data(verify_session(session)).get("id")
    today = datetime.utcnow().date()

    current_game = CurrentGame.query.get(user_id_or_session)
    if not current_game:
        current_game = CurrentGame(user_id_or_session=user_id_or_session, date=today, archive_date=today)
        db.session.add(current_game)
        db.session.commit()

    try:
        archive = Archive.query.get(today)

        # Get the song ID based on the current genre
        if current_game.current_genre == 'General':
            song_id = archive.general_track
        elif current_game.current_genre == 'Rock':
            song_id = archive.rock_track
        elif current_game.current_genre == 'Hip Hop':
            song_id = archive.hiphop_track
        else:
            # If it's the last song for the day (Hiphop), then just return a message for now
            return jsonify({
                'message': "You've finished all songs for today. Come back tomorrow for more!"
            })

        clip_length = guess_duration_map[current_game.guesses_left]

        return jsonify({
            'song_id': song_id,
            'clip_length': clip_length,
            'current_genre': current_game.current_genre
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/clip/<string:song_id>', methods=['GET'])
def get_clip(song_id):
    try:
        file_name = f"{song_id}.mp3"

        if not os.path.exists(os.path.join(CLIPS_DIR, file_name)):
            return jsonify({'error': 'Clip not found'}), 404

        return send_from_directory(CLIPS_DIR, file_name)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/guess', methods=['POST'])
def submit_guess():
    try:
        user_guess = request.form['song_guess']

        logged_in = check_login_status()
        user_id_or_session = session['id'] if not logged_in else fetch_user_data(verify_session(session)).get("id")
        current_game = CurrentGame.query.get(user_id_or_session)

        song_id = {
            'General': current_game.archive.general_track,
            'Rock': current_game.archive.rock_track,
            'Hip Hop': current_game.archive.hiphop_track
        }[current_game.current_genre]
        current_song = Songfull.query.get(song_id)

        past_game = PastGame.query.filter_by(user_id_or_session=user_id_or_session).first()

        if (user_guess.lower() == current_song.name.lower() or
                user_guess.lower() == f"{current_song.name} - {current_song.artist}".lower() or
                user_guess.lower() == current_song.id.lower()):

            if current_game.current_genre == 'General':
                past_game.attempts_made_general += 1
                past_game.correct_guess_general = True
            elif current_game.current_genre == 'Rock':
                past_game.attempts_made_rock += 1
                past_game.correct_guess_rock = True
            elif current_game.current_genre == 'Hip Hop':
                past_game.attempts_made_hiphop += 1
                past_game.correct_guess_hiphop = True

            db.session.commit()
            return jsonify({'status': 'correct'})
        else:
            if current_game.guesses_left > 0:
                current_game.guesses_left -= 1

            if current_game.current_genre == 'General':
                past_game.attempts_made_general += 1
            elif current_game.current_genre == 'Rock':
                past_game.attempts_made_rock += 1
            elif current_game.current_genre == 'Hip Hop':
                past_game.attempts_made_hiphop += 1

            db.session.commit()

            if current_game.guesses_left == 0:
                if current_game.current_genre != 'Hip Hop':
                    if current_game.current_genre == 'General':
                        current_game.current_genre = 'Rock'
                    elif current_game.current_genre == 'Rock':
                        current_game.current_genre = 'Hip Hop'

                    current_game.guesses_left = 6

                    db.session.commit()

                    next_song_id = {
                        'General': current_game.archive.general_track,
                        'Rock': current_game.archive.rock_track,
                        'Hip Hop': current_game.archive.hiphop_track
                    }[current_game.current_genre]

                    return jsonify({
                        'status': 'wrong',
                        'clip_length': guess_duration_map[current_game.guesses_left],
                        'song_id': next_song_id,
                        'guesses_left': current_game.guesses_left,
                        'current_genre': current_game.current_genre
                    })

                return jsonify({'status': 'lose'})

            return jsonify({
                'status': 'wrong',
                'clip_length': guess_duration_map[current_game.guesses_left],
                'song_id': song_id,
                'guesses_left': current_game.guesses_left,
                'current_genre': current_game.current_genre
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/bonus', methods=['POST'])
def submit_bonus():
    try:
        album_guess = request.form['album_guess']
        release_year_guess = request.form['release_year_guess']

        logged_in = check_login_status()
        user_id_or_session = session['id'] if not logged_in else fetch_user_data(verify_session(session)).get("id")
        current_game = CurrentGame.query.get(user_id_or_session)

        song_id = {
            'General': current_game.archive.general_track,
            'Rock': current_game.archive.rock_track,
            'Hip Hop': current_game.archive.hiphop_track
        }[current_game.current_genre]
        current_song = Songfull.query.get(song_id)

        correct_album = current_song.album.lower() == album_guess.lower()
        correct_release_year = current_song.release.lower() == release_year_guess.lower()

        if current_game.current_genre == 'General':
            current_game.current_genre = 'Rock'
        elif current_game.current_genre == 'Rock':
            current_game.current_genre = 'Hip Hop'
        elif current_game.current_genre == 'Hip Hop':
            return jsonify({'status': 'win'})

        db.session.commit()

        next_song_id = {
            'General': current_game.archive.general_track,
            'Rock': current_game.archive.rock_track,
            'Hip Hop': current_game.archive.hiphop_track
        }[current_game.current_genre]

        current_game.guesses_left = 6

        db.session.commit()

        return jsonify({
            'status': 'correct',
            'next_song_id': next_song_id,
            'correct_album': correct_album,
            'correct_release_year': correct_release_year,
            'current_genre': current_game.current_genre,
            'guesses_left': current_game.guesses_left
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
