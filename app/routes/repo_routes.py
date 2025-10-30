from flask import jsonify, request, render_template, Blueprint
import sqlite3

bp = Blueprint('repo', __name__)

# API Endpoints
@bp.route('/')
def home():
    return render_template('index.html')


@bp.route('/repos', methods=['GET'])
def get_repos():
    conn = sqlite3.connect('github_data.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Query parameters
    language = request.args.get('language')
    limit = request.args.get('limit', type=int)
    min_stars = request.args.get('min_stars', type=int)

    query = 'SELECT * FROM repositories WHERE 1=1'
    params = []

    if language:
        query += ' AND language = ?'
        params.append(language)

    if min_stars:
        query += ' AND stars >= ?'
        params.append(min_stars)

    query += ' ORDER BY stars DESC'

    if limit:
        query += ' LIMIT ?'
        params.append(limit)

    c.execute(query, params)
    repos = [dict(row) for row in c.fetchall()]
    conn.close()

    return jsonify({
        'count': len(repos),
        'repositories': repos
    })


@bp.route('/repos/top', methods=['GET'])
def get_top_repos():
    limit = request.args.get('limit', default=10, type=int)

    conn = sqlite3.connect('github_data.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute('SELECT * FROM repositories ORDER BY stars DESC LIMIT ?', (limit,))
    repos = [dict(row) for row in c.fetchall()]
    conn.close()

    return jsonify({
        'count': len(repos),
        'top_repositories': repos
    })


@bp.route('/stats', methods=['GET'])
def get_stats():
    conn = sqlite3.connect('github_data.db')
    c = conn.cursor()

    c.execute('SELECT COUNT(*) FROM repositories')
    total = c.fetchone()[0]

    c.execute('SELECT language, COUNT(*) as count FROM repositories GROUP BY language ORDER BY count DESC')
    languages = [{'language': row[0], 'count': row[1]} for row in c.fetchall()]

    c.execute('SELECT SUM(stars) FROM repositories')
    total_stars = c.fetchone()[0] or 0

    c.execute('SELECT AVG(stars) FROM repositories')
    avg_stars = round(c.fetchone()[0] or 0, 2)

    conn.close()

    return jsonify({
        'total_repositories': total,
        'total_stars': total_stars,
        'average_stars': avg_stars,
        'languages': languages
    })


@bp.route('/fetch', methods=['POST'])
def manual_fetch():
    repos = fetch_github_data()
    if repos:
        store_data(repos)
        return jsonify({
            'success': True,
            'message': f'Fetched and stored {len(repos)} repositories',
            'timestamp': datetime.now().isoformat()
        })
    return jsonify({
        'success': False,
        'message': 'Failed to fetch data'
    }), 500

