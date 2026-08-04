from __future__ import annotations

import os

from flask import Flask
from flask_cors import CORS

from config import Config
from database.mongo import ensure_indexes
from extensions import bcrypt, csrf, limiter, login_manager
from services.auth_service import User


@login_manager.user_loader
def load_user(user_id: str):
    return User.from_id(user_id)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    CORS(app, supports_credentials=True)

    login_manager.login_view = "auth.login"
    login_manager.session_protection = "strong"

    try:
        ensure_indexes()
        app.config["MONGO_READY"] = True
    except RuntimeError as exc:
        app.config["MONGO_READY"] = False
        app.logger.warning("MongoDB initialization skipped at startup: %s", exc)

    from routes.auth import auth_bp
    from routes.chat import chat_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.context_processor
    def inject_globals():
        return {"available_models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"]}

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "0") == "1")
