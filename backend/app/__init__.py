from flask import Flask, jsonify
from flask_cors import CORS

from app.config import Config
from app.extensions import db, jwt
from app.routes import register_routes
from app.migrate import run_migrations


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    raw_origins = app.config.get("FRONTEND_ORIGIN", "http://localhost:5173")
    if isinstance(raw_origins, str):
        origins = [o.strip() for o in raw_origins.split(",") if o.strip()]
    elif isinstance(raw_origins, (list, tuple)):
        origins = list(raw_origins)
    else:
        origins = ["http://localhost:5173"]

    CORS(
        app,
        resources={r"/api/*": {"origins": origins}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )

    register_routes(app)
    run_migrations(app)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "not found"}), 404

    return app
