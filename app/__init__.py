from datetime import datetime

from flask import Flask, session, current_app
from flask_session import Session

from app import config
from app.util.session_utils import remove_directory


def create_app():
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY
    app.config["SESSION_TYPE"] = config.SESSION_TYPE
    app.config["SESSION_PERMANENT"] = config.SESSION_PERMANENT
    app.config["PERMANENT_SESSION_LIFETIME"] = config.PERMANENT_SESSION_LIFETIME

    app.config["SESSION_COOKIE_SECURE"] = config.SESSION_COOKIE_SECURE
    app.config["SESSION_COOKIE_HTTPONLY"] = config.SESSION_COOKIE_HTTPONLY
    # app.config["SESSION_COOKIE_SAMESITE"] = config.SESSION_COOKIE_SAMESITE

    # app.config["WTF_CSRF_ENABLED"] = config.WTF_CSRF_ENABLED

    Session(app)

    app.app_context().push()

    @app.before_request
    def before_request():
        session.modified = True  # ensure every request resets the session lifetime

        if "last_activity" in session:
            elapsed = datetime.utcnow() - session["last_activity"]
            session_lifetime = current_app.config.get("PERMANENT_SESSION_LIFETIME")
            if elapsed > session_lifetime:
                main_upload_dir = session.get("UPLOAD_DIR")
                remove_directory(main_upload_dir)
                session.clear()

        session["last_activity"] = datetime.utcnow()

    # Register blueprints
    from .routes import auth, user, stats, search, recommendations

    app.register_blueprint(auth.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(stats.bp)
    app.register_blueprint(search.bp)
    app.register_blueprint(recommendations.bp)

    return app
