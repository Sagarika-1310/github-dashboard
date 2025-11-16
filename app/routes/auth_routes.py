"""
Authentication routes for the Flask application.

This module defines routes for user authentication — including login, logout,
and user registration. It interacts with the authentication repository for
database operations and includes structured logging and error handling.

Blueprint:
    bp (Blueprint): Flask Blueprint for authentication routes.
"""

from flask import (
    render_template, Blueprint, make_response, flash,
    request, redirect, url_for, jsonify
)
from flask import current_app as app
from werkzeug.exceptions import BadRequest

from app.repositories.auth_repo import (
    username_exists, create_user, authenticate_user,
    store_refresh_token
)
from app.utils.jwt_utils import (
    create_access_token, create_refresh_token, decode_token
)

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Authenticate an existing user and create a cookie-based JWT session.

    Methods:
        GET: Render the login page.
        POST: Validate credentials, set access & refresh tokens as cookies.

    Returns:
        HTML page or JSON login success message.
    """
    try:
        if request.method == 'POST':
            user = request.get_json()

            if not user or "username" not in user or "password" not in user:
                app.logger.warning("Login attempt with malformed request data.")
                return jsonify({"error": "Invalid request format"}), 400

            username = user["username"]
            app.logger.info(f"Login attempt for user '{username}'")

            if not username_exists(username):
                app.logger.warning(f"Login failed — username '{username}' does not exist.")
                return jsonify({"error": "Username does not exist"}), 404

            if authenticate_user(user):
                access_token = create_access_token({"username": username})
                refresh_token = create_refresh_token({"username": username})

                # Store refresh token in DB
                store_refresh_token(username, refresh_token)

                # Send cookies
                resp = jsonify({"msg": "Logged in"})
                resp.set_cookie("access_token", access_token, httponly=True, samesite="Lax")
                resp.set_cookie("refresh_token", refresh_token, httponly=True, samesite="Lax")

                app.logger.info(f"User '{username}' logged in successfully.")
                return resp, 200

            app.logger.warning(f"Invalid password for user '{username}'.")
            return jsonify({"error": "Invalid credentials"}), 401

        # GET — return login page
        return render_template('login.html')

    except Exception as e:
        app.logger.error(f"Unexpected error in login route: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@bp.route('/logout')
def logout():
    """
    Log out the current user by clearing authentication cookies and
    invalidating the refresh token stored in the database.

    Returns:
        Redirect: Redirects to the login page.
    """
    try:
        refresh_token = request.cookies.get("refresh_token")

        username = None
        if refresh_token:
            decoded = decode_token(refresh_token)
            if "username" in decoded:
                username = decoded["username"]

        # Clear refresh token stored in DB
        if username:
            store_refresh_token(username, None)
            app.logger.info(f"User '{username}' logged out — refresh token removed.")

        resp = make_response(redirect(url_for('auth.login')))
        resp.delete_cookie("access_token")
        resp.delete_cookie("refresh_token")

        flash("Logged out successfully.", "info")
        return resp

    except Exception as e:
        app.logger.error(f"Error during logout: {str(e)}")
        flash("Error logging out. Please try again.", "danger")
        return redirect(url_for('auth.login')), 500


@bp.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """
    Register a new user.

    GET:
        Render registration form.
    POST:
        Validate form, check uniqueness, create user.

    Returns:
        HTML page or redirect to login page.
    """
    try:
        if request.method == 'POST':
            form_data = request.form.to_dict()

            if not form_data.get("username") or not form_data.get("password"):
                app.logger.warning("Registration attempt with missing fields.")
                flash("Username and password are required.", "warning")
                return redirect(url_for('auth.add_user'))

            username = form_data["username"]
            app.logger.info(f"Registration attempt for new user '{username}'")

            if username_exists(username):
                app.logger.warning(f"Registration failed — username '{username}' already exists.")
                flash("Username already exists! Choose another.", "danger")
                return redirect(url_for('auth.add_user'))

            create_user(form_data)

            app.logger.info(f"New account created successfully for '{username}'.")
            flash("Account created! You may now log in.", "success")
            return redirect(url_for('auth.login'))

        return render_template('add_user.html')

    except BadRequest as br:
        app.logger.error(f"Bad request during registration: {br}")
        flash("Invalid form submission.", "danger")
        return render_template('add_user.html'), 400

    except Exception as e:
        app.logger.error(f"Unexpected error in add_user route: {str(e)}")
        flash("Something went wrong while creating the account.", "danger")
        return render_template('add_user.html'), 500


@bp.route('/refresh', methods=['POST'])
def refresh():
    """
    Refresh the access token using the refresh token stored in HttpOnly cookies.

    Returns:
        JSON containing success message and updated cookie.
    """
    try:
        refresh_token = request.cookies.get("refresh_token")

        if not refresh_token:
            app.logger.warning("Refresh attempt without token.")
            return jsonify({"error": "Missing refresh token"}), 401

        decoded = decode_token(refresh_token)

        if "error" in decoded:
            app.logger.warning(f"Refresh token invalid: {decoded['error']}")
            return jsonify({"error": decoded["error"]}), 401

        username = decoded["username"]

        app.logger.info(f"Issuing new access token for user '{username}'")
        new_access = create_access_token({"username": username})

        resp = jsonify({"msg": "refreshed"})
        resp.set_cookie("access_token", new_access, httponly=True, samesite="Lax")

        return resp

    except Exception as e:
        app.logger.error(f"Error in refresh route: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
