from __future__ import annotations

import os
from pathlib import Path

from flask import Flask
from flask_cors import CORS

from .models import db
from .routes.files import files_bp
from .routes.search import search_bp
from .routes.upload import upload_bp


def create_app() -> Flask:
    app = Flask(__name__)

    base_dir = Path(__file__).resolve().parent.parent
    app.config.update(
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", f"sqlite:///{base_dir / 'vault.db'}"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.getenv("UPLOAD_FOLDER", str(base_dir / "uploads")),
        PREVIEW_FOLDER=os.getenv("PREVIEW_FOLDER", str(base_dir / "previews")),
        MAX_CONTENT_LENGTH=int(os.getenv("MAX_CONTENT_LENGTH", str(1024 * 1024 * 1024))),
        REDIS_URL=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    )

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    Path(app.config["PREVIEW_FOLDER"]).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.register_blueprint(upload_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(files_bp)

    with app.app_context():
        db.create_all()

    return app
