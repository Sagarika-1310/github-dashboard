"""Utility module for handling database-related operations using SQLite.

This module provides a `db_connect` decorator that manages database connections,
cursor creation, commits, rollbacks, logging, and cleanup. It centralizes DB
access logic to ensure consistency and prevent resource leaks across the
application.
"""

import os
import sqlite3
from functools import wraps
from flask import current_app as app


def db_connect(path: str = None):
    """
    Decorator that provides a managed SQLite database connection to the wrapped function.

    The wrapped function will receive a `cursor` object as its first argument.
    All connection handling—including opening, committing, rolling back, and closing—
    is automatically managed.

    Args:
        path (str, optional): Custom database file path. Falls back to
                              app.config["DB_PATH"] when not provided.

    Returns:
        function: Wrapped function with database context injected.

    Raises:
        sqlite3.Error: Database-related errors.
        Exception: Any unexpected errors during DB operations.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            conn = None
            cursor = None

            try:
                # Determine correct database path
                try:
                    db_path = path or app.config["DB_PATH"]
                except KeyError:
                    raise KeyError(
                        "DB_PATH not found in app.config. Please configure it before using db_connect."
                    )

                # Ensure directory exists (unless DB is in current directory)
                db_dir = os.path.dirname(db_path)
                if db_dir:
                    os.makedirs(db_dir, exist_ok=True)
                    app.logger.debug(f"Ensured DB directory exists: {db_dir}")

                # Create SQLite connection
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row  # Return dict-like rows
                cursor = conn.cursor()

                app.logger.info(f"Opened SQLite connection at: {db_path}")

                # Execute wrapped function
                result = func(cursor, *args, **kwargs)

                # Commit changes
                conn.commit()
                app.logger.debug("Transaction committed successfully.")
                return result

            except sqlite3.Error as sql_err:
                if conn:
                    conn.rollback()
                    app.logger.warning("Transaction rolled back due to SQLite error.")
                app.logger.error(f"SQLite error: {str(sql_err)}")
                raise

            except Exception as exc:
                if conn:
                    conn.rollback()
                    app.logger.warning("Transaction rolled back due to unexpected error.")
                app.logger.error(f"Unexpected database error: {str(exc)}")
                raise

            finally:
                # Close DB resources
                if cursor:
                    cursor.close()
                    app.logger.debug("Cursor closed.")
                if conn:
                    conn.close()
                    app.logger.info("SQLite connection closed.")

        return wrapper

    return decorator
