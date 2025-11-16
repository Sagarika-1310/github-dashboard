"""
Repository layer for authentication-related database operations.

This module handles all SQL queries related to the `auth` user table including:
table initialization, user creation, credential verification, refresh token
management, and existence checks.

By centralizing authentication data logic here, the application maintains a clean
separation of concerns between routes, services, and database operations.
"""

from flask import current_app as app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from app.utils.db_utils import db_connect


@db_connect()
def init_auth_table(cursor):
    """
    Create the 'auth' table if it does not exist.

    Args:
        cursor (sqlite3.Cursor): The database cursor.

    Returns:
        None

    Raises:
        Exception: When table creation fails.
    """
    try:
        app.logger.info("Ensuring 'auth' table exists...")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS auth (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                first_name TEXT,
                last_name TEXT,
                password TEXT NOT NULL,
                created_at TEXT NOT NULL,
                refresh_token TEXT
            );
            """
        )

        app.logger.info("'auth' table is ready.")
    except Exception as e:
        app.logger.error(f"Failed to create 'auth' table: {str(e)}")
        raise


@db_connect()
def username_exists(cursor, username):
    """
    Check if a username exists in the database.

    Args:
        cursor (sqlite3.Cursor): Database cursor.
        username (str): Username to check.

    Returns:
        bool: True if username exists, else False.

    Raises:
        Exception: Query failure.
    """
    try:
        app.logger.debug(f"Checking if username exists: '{username}'")

        cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM auth WHERE username = ?)",
            (username,)
        )
        exists = cursor.fetchone()[0] == 1

        app.logger.debug(f"Username '{username}' exists: {exists}")
        return exists

    except Exception as e:
        app.logger.error(f"Error checking username '{username}': {str(e)}")
        raise


@db_connect()
def create_user(cursor, user):
    """
    Create a new user record.

    Args:
        cursor (sqlite3.Cursor): Database cursor.
        user (dict): Must contain 'first_name', 'last_name', 'username', 'password'.

    Returns:
        None

    Raises:
        KeyError: Missing required fields.
        Exception: Insert operation fails.
    """
    try:
        required = ["first_name", "last_name", "username", "password"]
        missing = [k for k in required if k not in user]

        if missing:
            raise KeyError(f"Missing required user fields: {missing}")

        username = user["username"]
        hashed_password = generate_password_hash(user["password"])
        created_time = datetime.utcnow().isoformat()

        app.logger.info(f"Creating user: '{username}'")

        cursor.execute(
            """
            INSERT INTO auth (first_name, last_name, username, password, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user["first_name"],
                user["last_name"],
                username,
                hashed_password,
                created_time,
            )
        )

        app.logger.info(f"User '{username}' created successfully.")

    except KeyError as ke:
        app.logger.error(f"User creation failed (invalid input): {str(ke)}")
        raise

    except Exception as e:
        app.logger.error(f"Database error while creating user '{username}': {str(e)}")
        raise


@db_connect()
def authenticate_user(cursor, user):
    """
    Validate credentials for authentication.

    Args:
        cursor (sqlite3.Cursor): Database cursor.
        user (dict): Must contain 'username' and 'password'.

    Returns:
        bool: True if authentication succeeds, else False.

    Raises:
        KeyError: Missing required fields.
        Exception: Query failure.
    """
    try:
        if "username" not in user or "password" not in user:
            raise KeyError("Both 'username' and 'password' are required.")

        username = user["username"]
        password = user["password"]

        app.logger.debug(f"Authenticating user: '{username}'")

        cursor.execute(
            "SELECT password FROM auth WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()

        if row and check_password_hash(row["password"], password):
            app.logger.info(f"User '{username}' authenticated successfully.")
            return True

        app.logger.warning(f"Authentication failed for user '{username}'.")
        return False

    except KeyError as ke:
        app.logger.error(f"Authentication failed: {str(ke)}")
        raise

    except Exception as e:
        app.logger.error(f"Error authenticating user '{username}': {str(e)}")
        raise


@db_connect()
def store_refresh_token(cursor, username, token):
    """
    Store or update a refresh token for a user.

    Args:
        cursor (sqlite3.Cursor): Database cursor.
        username (str): The username to update.
        token (str): The refresh token to store.

    Returns:
        None
    """
    try:
        app.logger.info(f"Updating refresh token for user '{username}'")

        cursor.execute(
            "UPDATE auth SET refresh_token = ? WHERE username = ?",
            (token, username)
        )

        app.logger.info(f"Refresh token updated for user '{username}'")

    except Exception as e:
        app.logger.error(f"Failed to update refresh token for '{username}': {str(e)}")
        raise


@db_connect()
def get_refresh_token(cursor, username):
    """
    Retrieve the refresh token for a user.

    Args:
        cursor (sqlite3.Cursor): Database cursor.
        username (str): Username whose refresh token is to be fetched.

    Returns:
        str | None: Stored refresh token or None if not found.

    Raises:
        Exception: Query failure.
    """
    try:
        app.logger.debug(f"Fetching refresh token for user '{username}'")

        cursor.execute(
            "SELECT refresh_token FROM auth WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()

        token = row[0] if row else None

        app.logger.debug(
            f"Refresh token for '{username}': {'found' if token else 'not found'}"
        )

        return token

    except Exception as e:
        app.logger.error(f"Error retrieving refresh token for '{username}': {str(e)}")
        raise
