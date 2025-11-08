"""Custom logger for application"""

import logging
import os


def setup_logger(app):
    """Configure application-wide logging."""
    os.makedirs(app.config["LOG_DIR"], exist_ok=True)
    log_file = app.config["LOG_FILE"]

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )

    # Clear existing handlers to avoid duplicate logs
    if app.logger.hasHandlers():
        app.logger.handlers.clear()

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Stream handler (console)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)

    # Attach to app.logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.DEBUG)

    # Prevent Flask from propagating logs to root logger
    app.logger.propagate = False

    app.logger.info("Logger initialized successfully.")
