"""
Application configuration module.

This module defines configuration classes used by the Flask application.
It supports environment-based settings, dynamic directory resolution,
secure defaults, and paths for logs and database files.

Classes:
    Config: Base configuration shared by all environments.
    DevelopmentConfig: Settings optimized for local development.
    ProductionConfig: Settings used in production deployment.
"""

import os


class Config:
    """
    Base configuration for the Flask application.

    This class defines core settings for security, database paths,
    directory structures, logging, and API tokens. Environment variables
    are used wherever applicable to support deployment flexibility.
    """

    # ---------------------------------------------------------------------
    # Core Application Settings
    # ---------------------------------------------------------------------
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    # ---------------------------------------------------------------------
    # Base Directories
    # ---------------------------------------------------------------------
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    INSTANCE_DIR = os.getenv(
        "INSTANCE_DIR",
        os.path.join(BASE_DIR, "instance")
    )

    # Ensure instance directory exists
    os.makedirs(INSTANCE_DIR, exist_ok=True)

    # ---------------------------------------------------------------------
    # Database Configuration
    # ---------------------------------------------------------------------
    DB_DIR = os.getenv(
        "DB_DIR",
        os.path.join(INSTANCE_DIR, "db")
    )
    os.makedirs(DB_DIR, exist_ok=True)

    DB_PATH = os.getenv(
        "DB_PATH",
        os.path.join(DB_DIR, "repo.db")
    )

    # ---------------------------------------------------------------------
    # Logging Configuration
    # ---------------------------------------------------------------------
    LOG_DIR = os.getenv(
        "LOG_DIR",
        os.path.join(INSTANCE_DIR, "logs")
    )
    os.makedirs(LOG_DIR, exist_ok=True)

    LOG_FILE = os.getenv(
        "LOG_FILE",
        os.path.join(LOG_DIR, "app.log")
    )


class DevelopmentConfig(Config):
    """
    Configuration for local development.

    Debug mode is enabled and paths are fully local.
    """

    DEBUG = True
    ENV = "development"


class ProductionConfig(Config):
    """
    Configuration for production deployment.

    Debug mode disabled and sensitive values must come from environment variables.
    """

    DEBUG = False
    ENV = "production"

    # Require secure secret key in production
    SECRET_KEY = os.getenv("SECRET_KEY", "prod-secret-key")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production.")
