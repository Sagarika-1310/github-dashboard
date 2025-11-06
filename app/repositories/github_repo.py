from flask import current_app as app
import sqlite3
from datetime import datetime
import os


def get_db_path():
    """Return the full path to the SQLite database file."""
    db_file = 'github_data.db'
    db_dir = os.path.join(app.instance_path, "db")
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, db_file)


def table_exists(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT 1 FROM {table_name} LIMIT 1;")
        exists = True
    except sqlite3.OperationalError:
        exists = False
    conn.close()
    return exists


# Database setup
def init_db():
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS repositories
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  full_name TEXT UNIQUE,
                  repo_url TEXT,
                  description TEXT,
                  stars INTEGER,
                  forks INTEGER,
                  language TEXT,
                  created_at TEXT,
                  updated_at TEXT,
                  fetched_at TEXT)''')
    conn.commit()
    conn.close()


# Store data in SQLite
def store_data(repos):
    db_path = get_db_path()
    if not table_exists(db_path, "repositories"):
        init_db()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    fetched_time = datetime.now().isoformat()

    for repo in repos:
        try:
            c.execute('''INSERT OR REPLACE INTO repositories 
                        (name, full_name, repo_url, description, stars, forks, language, created_at, updated_at, fetched_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (repo['name'], repo['full_name'], repo['html_url'], repo['description'],
                       repo['stargazers_count'], repo['forks_count'], repo['language'],
                       repo['created_at'], repo['updated_at'], fetched_time))
        except Exception as e:
            app.logger.info(f"Error storing repo {repo.get('name')}: {e}")

    conn.commit()
    conn.close()


def get_all_repos(language=None, limit=None, min_stars=None):
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    query = 'SELECT * FROM repositories WHERE 1=1'
    params = []

    if language:
        query += ' AND LOWER(language) = ?'
        params.append(language.lower())

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

    return repos


def get_all_top_repos(limit):
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute('SELECT * FROM repositories ORDER BY stars DESC LIMIT ?', (limit,))
    repos = [dict(row) for row in c.fetchall()]
    conn.close()

    return repos


def get_all_stats():
    conn = sqlite3.connect(get_db_path())
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

    return total, total_stars, avg_stars, languages
