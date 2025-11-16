"""
Repository-related endpoints for the Flask application.

This module exposes API endpoints to view, filter, fetch, and analyze GitHub
repository data stored locally. It integrates with the repo repository layer
for database operations and the GitHub service layer for API calls.

Blueprint:
    bp (Blueprint): Flask Blueprint for repository routes.
"""

from flask import jsonify, request, render_template, Blueprint
from flask import current_app as app
from datetime import datetime
from werkzeug.exceptions import BadRequest

from app.repositories.github_repo import (
    get_all_repos,
    get_all_top_repos,
    get_all_stats,
    store_data
)
from app.services.github_service import fetch_github_data
from app.utils.jwt_utils import jwt_required

bp = Blueprint('repo', __name__)


@bp.route('/')
@jwt_required
def home():
    """
    Render the main dashboard home page.

    Returns:
        HTML template for the dashboard.
    """
    try:
        app.logger.info("Rendering dashboard home page.")
        return render_template('index.html')

    except Exception as e:
        app.logger.error(f"Error rendering home page: {str(e)}")
        return "Internal Server Error", 500


@bp.route('/get_repos', methods=['GET'])
@jwt_required
def get_repos():
    """
    Fetch repositories from the local database using optional filters.

    Query Parameters:
        language (str, optional): Filter by programming language.
        limit (int, optional): Limit number of returned repos.
        min_stars (int, optional): Minimum star count.

    Returns:
        JSON with count and list of repositories.
    """
    try:
        language = request.args.get('language')
        limit = request.args.get('limit', type=int)
        min_stars = request.args.get('min_stars', type=int)

        app.logger.info(
            "Retrieving repositories from DB with filters -> "
            f"language={language}, limit={limit}, min_stars={min_stars}"
        )

        repos = get_all_repos(language, limit, min_stars)

        app.logger.info(f"{len(repos)} repositories retrieved successfully.")
        return jsonify({'count': len(repos), 'repositories': repos})

    except BadRequest:
        app.logger.error("Invalid query parameters supplied to /get_repos.")
        return jsonify({'error': 'Invalid query parameters.'}), 400

    except Exception as e:
        app.logger.error(f"Unexpected error in get_repos: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/top_repos', methods=['GET'])
@jwt_required
def get_top_repos():
    """
    Retrieve the top N repositories sorted by star count.

    Query Params:
        limit (int, optional): Number of repos to return. Default = 10.

    Returns:
        JSON with count and list of top repositories.
    """
    try:
        limit = request.args.get('limit', default=10, type=int)

        app.logger.info(f"Fetching top {limit} repositories by stars.")

        repos = get_all_top_repos(limit)

        app.logger.info(f"Successfully retrieved {len(repos)} top repositories.")
        return jsonify({'count': len(repos), 'top_repositories': repos})

    except Exception as e:
        app.logger.error(f"Unexpected error in /top_repos: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/stats', methods=['GET'])
@jwt_required
def get_stats():
    """
    Retrieve overall statistics for all stored repositories.

    Returns:
        JSON with:
            total_repositories (int)
            total_stars (int)
            average_stars (float)
            languages (list[dict])
    """
    try:
        app.logger.info("Fetching repository statistics.")

        total, total_stars, avg_stars, languages = get_all_stats()

        app.logger.info("Repository statistics successfully generated.")
        return jsonify({
            'total_repositories': total,
            'total_stars': total_stars,
            'average_stars': avg_stars,
            'languages': languages
        })

    except Exception as e:
        app.logger.error(f"Error fetching repository statistics: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/fetch_repos', methods=['POST'])
@jwt_required
def manual_fetch():
    """
    Manually fetch GitHub repositories and store them in the DB.

    JSON Body Fields:
        topic (str, optional): Search keyword/topic. Default = "Python".
        limit (int, optional): Number of repos to fetch. Default = 10.

    Returns:
        JSON with summary of the fetch and storage results.
    """
    try:
        app.logger.info("Manual fetch request received.")

        data = request.get_json(force=True)
        topic = data.get('topic', 'Python')
        limit = int(data.get('limit', 10))

        app.logger.info(f"Fetching GitHub data -> topic='{topic}', limit={limit}")

        repos = fetch_github_data(topic=topic, per_page=limit)

        if not repos:
            app.logger.warning(
                f"No repositories found from GitHub for topic='{topic}', limit={limit}"
            )
            return jsonify({
                'success': False,
                'message': 'No repositories found for the given criteria',
                'topic': topic,
                'limit': limit
            }), 404

        store_data(repos)

        app.logger.info(
            f"Fetched {len(repos)} repos from GitHub and stored them in the database."
        )

        return jsonify({
            'success': True,
            'message': f"Fetched and stored {len(repos)} repositories",
            'topic': topic,
            'limit': limit,
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except BadRequest as br:
        app.logger.error(f"Bad request in manual_fetch: {br}")
        return jsonify({'success': False, 'message': 'Invalid request body.'}), 400

    except ConnectionError as ce:
        app.logger.error(f"GitHub API connection error: {ce}")
        return jsonify({
            'success': False,
            'message': 'External API unavailable (GitHub failed).'
        }), 502

    except Exception as e:
        app.logger.error(f"Unexpected error in manual_fetch: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal error while fetching repositories.'
        }), 500
