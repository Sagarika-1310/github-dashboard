import sqlite3
from functools import wraps
from flask import current_app as app


def db_connect(db_path=None):
    """
    Decorator for functions that need a SQLite connection.
    Automatically handles connection, cursor, commit, rollback, and close.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            conn = None
            cursor = None

            try:
                # Check for new DB path
                path = app.config["DB_PATH"]
                if db_path:
                    path = db_path

                # Connect to database
                conn = sqlite3.connect(path)
                cursor = conn.cursor()
                app.logger.info(f"Opened SQLite connection to {path}")

                # Call wrapped function
                result = func(cursor, *args, **kwargs)

                # Commit if successful
                conn.commit()
                app.logger.info("Transaction committed successfully")
                return result

            except sqlite3.Error as e:
                if conn: conn.rollback()
                app.logger.error(f"DB error. ERROR : {str(e)}")
                raise

            except Exception as e:
                if conn: conn.rollback()
                app.logger.error(f"Unexpected error in DB. ERROR: {str(e)}")
                raise

            finally:
                # Cleanup
                if cursor:
                    cursor.close()
                    app.logger.info("Cursor closed")
                if conn:
                    conn.close()
                    app.logger.info("SQLite connection closed")

        return wrapper

    return decorator
