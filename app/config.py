"""Config for application"""

import os


class Config:
    """Base configuration"""
    # Core app settings
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    # Paths
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
    DB_DIR = os.path.join(INSTANCE_DIR, "db")
    DB_PATH = os.path.join(DB_DIR, "repo.db")

    LOG_DIR = os.path.join(INSTANCE_DIR, "logs")
    LOG_FILE = os.path.join(LOG_DIR, "app.log")
