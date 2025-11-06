"""Initialize flask app"""

from flask import Flask
import os
from app.logger import setup_logger

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'dev_secret_key_change_me'

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Setup logging
    setup_logger(app)

    # Import and register blueprints
    from app.routes.repo_routes import bp as repo_bp
    from app.routes.auth_routes import bp as auth_bp

    app.register_blueprint(repo_bp, url_prefix='/repo')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app