"""
Custom logging configuration for the application.

This module defines utilities for setting up application-wide logging using a
consistent format, file rotation, and dual output (file + console). Logging
is initialized during Flask app creation and uses configuration defined in
config.py.
"""

import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(app):
    """
    Configure logging for the Flask application.

    This function:
        - Ensures the log directory exists.
        - Creates a rotating file handler for persistent logs.
        - Adds a stream handler for console output.
        - Prevents duplicate log entries.
        - Applies consistent formatting across handlers.

    Args:
        app (Flask): The Flask application instance.

    Raises:
        KeyError: If mandatory logging configuration keys are missing.
        OSError: If log directory or log file cannot be created.
    """

    # ------------------------------------------------------------------
    # Validate configuration
    # ------------------------------------------------------------------
    required_keys = ["LOG_DIR", "LOG_FILE"]
    for key in required_keys:
        if key not in app.config:
            raise KeyError(f"Missing required logging config key: {key}")

    log_dir = app.config["LOG_DIR"]
    log_file = app.config["LOG_FILE"]

    # ------------------------------------------------------------------
    # Ensure logging directory exists
    # ------------------------------------------------------------------
    try:
        os.makedirs(log_dir, exist_ok=True)
    except OSError as e:
        raise OSError(f"Failed to create log directory '{log_dir}': {str(e)}")

    # ------------------------------------------------------------------
    # Log formatting
    # ------------------------------------------------------------------
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # ------------------------------------------------------------------
    # Clean up any existing handlers to prevent duplicate logs
    # ------------------------------------------------------------------
    if app.logger.handlers:
        app.logger.handlers.clear()

    # ------------------------------------------------------------------
    # Rotating File Handler
    # ------------------------------------------------------------------
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=50 * 1024 * 1024,  # 50MB per file
        backupCount=2,  # keep 2 backups
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # ------------------------------------------------------------------
    # Stream Handler (console logs)
    # ------------------------------------------------------------------
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)

    # ------------------------------------------------------------------
    # Attach handlers to Flask logger
    # ------------------------------------------------------------------
    app.logger.addHandler(file_handler)
    app.logger.addHandler(stream_handler)

    # The Flask logger's base level is DEBUG so all handler levels apply.
    app.logger.setLevel(logging.DEBUG)

    # Prevent Flask from duplicating logs to the root logger
    app.logger.propagate = False

    app.logger.info("Application logger initialized successfully.")
