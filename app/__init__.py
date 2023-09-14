from datetime import datetime

from flask import Flask, session, current_app
from flask_session import Session

from app import config
from app.util import remove_directory, scheduled_cleanup


def create_app():
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY
    app.config['SESSION_TYPE'] = config.SESSION_TYPE
    app.config['SESSION_PERMANENT'] = config.SESSION_PERMANENT
    app.config['PERMANENT_SESSION_LIFETIME'] = config.PERMANENT_SESSION_LIFETIME
    Session(app)

    app.app_context().push()

    @app.before_request
    def before_request():
        session.modified = True  # ensure every request resets the session lifetime

        if 'last_activity' in session:
            elapsed = datetime.utcnow() - session['last_activity']
            session_lifetime = current_app.config.get('PERMANENT_SESSION_LIFETIME')
            if elapsed > session_lifetime:
                main_upload_dir = session.get('UPLOAD_DIR')
                remove_directory(main_upload_dir)
                session.clear()

        session['last_activity'] = datetime.utcnow()

    # Register blueprints
    from .routes import auth, user, stats, search, recommendations
    app.register_blueprint(auth.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(stats.bp)
    app.register_blueprint(search.bp)
    app.register_blueprint(recommendations.bp)

    # scheduler = BackgroundScheduler()
    # scheduler.add_job(scheduled_cleanup, 'interval', hours=2)
    # scheduler.start()
    return app
