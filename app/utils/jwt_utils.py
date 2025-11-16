"""
JWT utility module for managing authentication tokens in the application.

Provides helper functions for:
    - Generating access and refresh tokens
    - Decoding and validating tokens
    - Route protection through the jwt_required decorator

This implementation uses:
    - HS256 signing
    - Cookie-based authentication (HttpOnly cookies)
    - Automatic JSON vs HTML response handling
"""

import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import (
    current_app as app,
    request,
    jsonify,
    redirect,
    url_for
)


def create_access_token(payload):
    """
    Create a short-lived access token.

    Args:
        payload (dict): Data to embed in the token.

    Returns:
        str: Encoded JWT string.
    """
    try:
        app.logger.debug(f"Creating access token for payload: {payload}")

        payload = payload.copy()
        payload.update({
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=15)
        })

        token = jwt.encode(
            payload,
            app.config["SECRET_KEY"],
            algorithm="HS256"
        )

        app.logger.debug("Access token created successfully.")
        return token

    except Exception as e:
        app.logger.error(f"Failed to create access token: {str(e)}")
        raise


def create_refresh_token(payload):
    """
    Create a long-lived refresh token.

    Args:
        payload (dict): Data to embed in the token.

    Returns:
        str: Encoded JWT string.
    """
    try:
        app.logger.debug(f"Creating refresh token for payload: {payload}")

        payload = payload.copy()
        payload.update({
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(days=7)
        })

        token = jwt.encode(
            payload,
            app.config["SECRET_KEY"],
            algorithm="HS256"
        )

        app.logger.debug("Refresh token created successfully.")
        return token

    except Exception as e:
        app.logger.error(f"Failed to create refresh token: {str(e)}")
        raise


def decode_token(token):
    """
    Decode a JWT token and validate expiry/signature.

    Args:
        token (str): Encoded JWT string.

    Returns:
        dict: Decoded payload OR {"error": "expired"} OR {"error": "invalid"}.
    """
    try:
        decoded = jwt.decode(
            token,
            app.config["SECRET_KEY"],
            algorithms=["HS256"]
        )
        return decoded

    except jwt.ExpiredSignatureError:
        app.logger.warning("JWT decode failed — token expired.")
        return {"error": "expired"}

    except jwt.InvalidTokenError:
        app.logger.warning("JWT decode failed — invalid token.")
        return {"error": "invalid"}

    except Exception as e:
        app.logger.error(f"Unexpected error decoding token: {str(e)}")
        return {"error": "invalid"}


def jwt_required(f):
    """
    Decorator to protect routes using cookie-based JWT authentication.

    Behavior:
        - Checks `access_token` from HttpOnly cookie.
        - Redirects browser-based requests to login on failure.
        - Returns JSON 401 for API/XHR requests.
        - On success: attaches decoded payload to `request.current_user`.

    Returns:
        Wrapped function output OR authentication error response.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.cookies.get("access_token")

        # Missing token → unauthorized
        if not token:
            app.logger.warning(
                "Unauthorized access attempt — missing access token."
            )

            if request.accept_mimetypes.best == "application/json":
                return jsonify({"error": "Missing token"}), 401

            return redirect(url_for('auth.login'))

        # Decode and validate
        decoded = decode_token(token)

        if "error" in decoded:
            reason = decoded["error"]
            app.logger.warning(
                f"Access token rejected — {reason}. Redirecting to login."
            )

            if request.accept_mimetypes.best == "application/json":
                return jsonify({"error": f"Token {reason}"}), 401

            return redirect(url_for('auth.login'))

        # Success — attach user to request
        request.current_user = decoded
        return f(*args, **kwargs)

    return wrapper
