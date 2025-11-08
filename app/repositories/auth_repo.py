"""User table queries for application"""

from flask import current_app as app
from datetime import datetime
from werkzeug.security import generate_password_hash

from app.utils.db_utils import db_connect


@db_connect
def init_auth_table(cursor):
    try:
        app.logger.info("Creating table auth if not exists")
        cursor.execute('''CREATE TABLE IF NOT EXISTS auth
                             (id INTEGER AUTOINCREMENT,
                              username TEXT PRIMARY KEY,
                              first_name TEXT,
                              last_name TEXT,
                              password TEXT,
                              created_at INTEGER)''')
        app.logger.info("Created table auth successfully")
    except Exception as e:
        app.logger.error(f"Error creating auth table. ERROR: {str(e)}")
        raise


@db_connect
def username_exists(cursor, username):
    try:
        app.logger.info("Checking if username exists")
        cursor.execute("SELECT EXISTS(SELECT 1 FROM auth WHERE username = ?)", (username,))
        return cursor.fetchone()[0] == 1
    except Exception as e:
        app.logger.error(f"Error checking username exists. ERROR: {str(e)}")
        raise


@db_connect
def create_user(cursor, user):
    try:
        created_time = datetime.now().isoformat()
        # Encrypt password for security
        password = generate_password_hash(user['password'])
        app.logger.info(f"Adding user {user['username']} in auth table")
        cursor.execute('''INSERT INTO auth (first_name, last_name, username, password, created_at) VALUES (?,?,?,?)''',
                       (user['first_name'], user['last_name'], user['username'], password, created_time))
        app.logger.info(f"Added user {user['username']} in auth table")
    except Exception as e:
        app.logger.error(f"Error adding new user {user['username']} to auth table. ERROR: {str(e)}")
        raise

@db_connect
def authenticate_user(cursor, user):
    try:
        app.logger.info(f"Authenticating user {user['username']}")
    except Exception as e:
        app.logger.info(f"Error authenticating user {user['username']}. ERROR: {str(e)}")