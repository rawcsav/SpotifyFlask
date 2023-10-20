import os
from datetime import datetime

from flask import Blueprint, render_template, session, request, jsonify, send_from_directory

from app.database import Songfull, PastGame, db

bp = Blueprint('songfull', __name__)

CLIPS_DIR = os.getenv('CLIPS_DIR')


@bp.route('/songfull')
def game():
    return render_template('songfull.html')


@bp.route('/start', methods=['POST'])
def start_game():
    try:
        current_songs = Songfull.query.filter_by(current=True).all()

        session['selected_songs'] = [song.id for song in current_songs]
        session['guesses_left'] = 7
        session['current_clip_length'] = 0.1

        return jsonify({'song_id': session['selected_songs'][0], 'clip_length': session['current_clip_length']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/clip/<string:song_id>', methods=['GET'])
def get_clip(song_id):
    try:
        clip_length = session.get('current_clip_length', 0.1)
        if clip_length == 0.1:
            clip_length_str = '01'
        else:
            clip_length_str = str(int(clip_length))  # convert to string after truncating to integer
        file_name = f"{song_id}_{clip_length_str}.mp3"

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

        # Initialize 'guesses' in session if not already present
        if 'guesses' not in session:
            session['guesses'] = []

        # Add the current guess to the session
        session['guesses'].append(user_guess)

        if user_guess.lower() == current_song.name.lower():
            # Get the genre of the next song
            if session['selected_songs'][1:]:
                next_song = Songfull.query.get(session['selected_songs'][1])
                next_genre = next_song.genre
            else:
                next_genre = None

            # Reset guesses_left if the genre changes
            if session.get('current_genre') != next_genre:
                session['guesses_left'] = 7
                session['current_genre'] = next_genre

            session['selected_songs'].pop(0)
            if not session['selected_songs']:
                # Save to database before returning the result
                game_result = PastGame(user_id=session['user_id'], result="win", date=datetime.utcnow())
                try:
                    db.session.add(game_result)
                    db.session.commit()
                except:
                    db.session.rollback()
                    raise

                return jsonify({'status': 'win'})
            next_song = Songfull.query.get(session['selected_songs'][0])
            return jsonify({'status': 'correct', 'next_song_id': next_song.id})
        else:
            session['guesses_left'] -= 1
            if session['guesses_left'] == 0:
                # Save to database before returning the result
                game_result = PastGame(user_id=session['user_id'], result="loss", date=datetime.utcnow())
                try:
                    db.session.add(game_result)
                    db.session.commit()
                except:
                    db.session.rollback()
                    raise

                return jsonify({'status': 'lose'})

            session['current_clip_length'] += 5
            return jsonify({
                'status': 'wrong',
                'clip_length': session['current_clip_length'],
                'song_id': session['selected_songs'][0],
                'guesses': session['guesses'],  # Return the guesses
                'guesses_left': session['guesses_left']  # Return the remaining guesses
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/archive', methods=['GET'])
def get_archive():
    # Retrieve and return archived game results from the database.
    # This is where you would query the database for past game records and return them.
    past_games = PastGame.query.all()
    return jsonify({'archive': [game.to_dict() for game in past_games]})
