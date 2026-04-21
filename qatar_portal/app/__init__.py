import os
from flask import Flask, jsonify
from flask_session import Session
from flask_cors import CORS
from app.extensions import db, bcrypt
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    env = os.environ.get("FLASK_ENV", "development")
    if env == "production":
        app.config.from_object("app.config.ProductionConfig")
    else:
        app.config.from_object("app.config.DevelopmentConfig")

    # Create session folder if it doesn't exist
    os.makedirs("./flask_session", exist_ok=True)

    # Init extensions
    db.init_app(app)
    bcrypt.init_app(app)
    Session(app)
    CORS(app, supports_credentials=True)

    # Register blueprints
    from app.routes.pages import pages_bp
    from app.routes.auth import auth_bp
    from app.routes.opportunities import opps_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(opps_bp, url_prefix="/api/opportunities")

    # Global error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Resource not found."}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"success": False, "error": "Method not allowed."}), 405

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"success": False, "error": "An unexpected server error occurred."}), 500

    # Create all DB tables on startup (for dev — in prod use alembic)
    with app.app_context():
        db.create_all()

    return app
