"""
Application factory for Flask app initialization.

This module creates and configures the Flask application, loads environment-
specific settings, initializes logging, registers blueprints, and prepares the
database tables at startup.
"""

from flask import Flask

from app.logger import setup_logger
from app.config import DevelopmentConfig
from app.repositories.auth_repo import init_auth_table
from app.repositories.github_repo import init_repo_table


def create_app(config_class=None):
    """
    Create and configure the Flask application.

    Args:
        config_class (class, optional):
            Custom config class for initialization.
            Defaults to DevelopmentConfig if not provided.

    Returns:
        Flask: The initialized Flask application instance.
    """

    app = Flask(__name__)

    # Choose configuration
    config_class = config_class or DevelopmentConfig
    app.config.from_object(config_class)

    setup_logger(app)
    app.logger.info(f"Using configuration: {config_class.__name__}")

    from app.routes.github_routes import bp as repo_bp
    from app.routes.auth_routes import bp as auth_bp

    app.register_blueprint(repo_bp, url_prefix="/repo")
    app.register_blueprint(auth_bp, url_prefix="/auth")

    app.logger.info("Blueprints registered successfully.")

    with app.app_context():
        try:
            init_auth_table()
            init_repo_table()
            app.logger.info("All database tables initialized successfully.")
        except Exception as e:
            app.logger.error(f"Database initialization failed: {str(e)}")
            raise

    app.logger.info("Application started successfully!")

    return app
