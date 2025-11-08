from flask import jsonify, request, render_template, Blueprint
from datetime import datetime

from app.repositories.github_repo import get_all_repos, get_all_top_repos, get_all_stats
from app.services.github_service import fetch_github_data, store_data

bp = Blueprint('repo', __name__)


@bp.route('/')
def home():
    return render_template('index.html')


@bp.route('/get_repos', methods=['GET'])
def get_repos():
    # Query parameters
    language = request.args.get('language')
    limit = request.args.get('limit', type=int)
    min_stars = request.args.get('min_stars', type=int)

    repos = get_all_repos(language, limit, min_stars)

    return jsonify({
        'count': len(repos),
        'repositories': repos
    })


@bp.route('/top_repos', methods=['GET'])
def get_top_repos():
    limit = request.args.get('limit', default=10, type=int)

    repos = get_all_top_repos(limit)

    return jsonify({
        'count': len(repos),
        'top_repositories': repos
    })


@bp.route('/stats', methods=['GET'])
def get_stats():
    total, total_stars, avg_stars, languages = get_all_stats()

    return jsonify({
        'total_repositories': total,
        'total_stars': total_stars,
        'average_stars': avg_stars,
        'languages': languages
    })


@bp.route('/fetch_repos', methods=['POST'])
def manual_fetch():
    try:
        # Parse JSON body
        data = request.get_json(force=True)  # force=True handles missing headers gracefully

        # Extract parameters with defaults
        topic = data.get('topic', 'Python')
        limit = int(data.get('limit', 10))

        # Call your fetch function with user parameters
        repos = fetch_github_data(topic=topic, per_page=limit)

        if repos:
            store_data(repos)
            return jsonify({
                'success': True,
                'message': f'Fetched and stored {len(repos)} repositories',
                'topic': topic,
                'limit': limit,
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'No repositories found for the given criteria',
                'topic': topic,
                'limit': limit
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Invalid request or internal error'
        }), 400
