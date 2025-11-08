"""Initialize flask app"""

from flask import Flask

from app.logger import setup_logger
from app.config import Config

def create_app():
    app = Flask(__name__)

    # Load config
    app.config.from_object(Config)

    # Setup logging
    setup_logger(app)

    # Import and register blueprints
    from app.routes.repo_routes import bp as repo_bp
    from app.routes.auth_routes import bp as auth_bp

    app.register_blueprint(repo_bp, url_prefix='/repo')
    app.register_blueprint(auth_bp, url_prefix='/repo')

    app.logger.info("Application started successfully!")

    return app
