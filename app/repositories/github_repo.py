"""Repositories table queries for application"""

from flask import current_app as app
from datetime import datetime

from app.utils.db_utils import db_connect


@db_connect
def init_repo_table(cursor):
    """Method to create table if it does not exist"""
    try:
        app.logger.info("Creating table repositories if not exists")
        cursor.execute('''CREATE TABLE IF NOT EXISTS repositories
                     (id INTEGER AUTOINCREMENT,
                      repo_name TEXT,
                      full_repo_name TEXT PRIMARY KEY,
                      repo_url TEXT,
                      description TEXT,
                      stars INTEGER,
                      forks INTEGER,
                      language TEXT,
                      created_at TEXT,
                      updated_at TEXT,
                      fetched_at TEXT)''')
        app.logger.info("Created table repositories successfully")
    except Exception as e:
        app.logger.error(f"Error creating repositories table. ERROR: {str(e)}")
        raise


@db_connect
def store_data(cursor, repos):
    """Method to store repo data in DB"""
    # Check and create table
    init_repo_table()
    fetched_time = datetime.now().isoformat()

    app.logger.info("Storing repo data in DB")
    for repo in repos:
        try:
            app.logger.info(f"Executing insert query for repo {repo.get('name')}")
            cursor.execute('''INSERT OR REPLACE INTO repositories 
                        (name, full_name, repo_url, description, stars, forks, language, created_at, updated_at, fetched_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (repo['name'], repo['full_name'], repo['html_url'], repo['description'],
                            repo['stargazers_count'], repo['forks_count'], repo['language'],
                            repo['created_at'], repo['updated_at'], fetched_time))
        except Exception as e:
            app.logger.error(f"Error storing repo {repo.get('name')} data in DB. ERROR: {str(e)}")
            raise
    app.logger.info("Stored repo data in DB successfully")


@db_connect
def get_all_repos(cursor, language=None, limit=None, min_stars=None):
    """Method to fetch all repositories from DB for the defined language, limit and min stars"""
    try:
        app.logger.info(f"Fetching all repo for language: {language.upper()}, limit: {limit}, min stars {min_stars}")
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

        app.logger.info("Executing query to fetch all repo")
        cursor.execute(query, params)
        repos = [dict(row) for row in cursor.fetchall()]

        app.logger.info("Fetched all repo successfully")

        return repos
    except Exception as e:
        app.logger.error(f"Error fetching repos. ERROR: {str(e)}")
        raise


@db_connect
def get_all_top_repos(cursor, limit):
    """Method to get all the top repos with the defined limit"""
    try:
        app.logger.info(f"Executing query to fetch top {limit} repo")
        cursor.execute('SELECT * FROM repositories ORDER BY stars DESC LIMIT ?', (limit,))
        repos = [dict(row) for row in cursor.fetchall()]
        app.logger.info(f"Fetched all top {limit} repo successfully")

        return repos
    except Exception as e:
        app.logger.error(f"Error fetching top repos. ERROR: {str(e)}")
        raise


@db_connect
def get_all_stats(cursor):
    """Method to get repo statistics"""
    try:
        app.logger.info("Calculating repo statistics")
        cursor.execute('SELECT COUNT(*) FROM repositories')
        total = cursor.fetchone()[0]

        cursor.execute('SELECT language, COUNT(*) as count FROM repositories GROUP BY language ORDER BY count DESC')
        languages = [{'language': row[0], 'count': row[1]} for row in cursor.fetchall()]

        cursor.execute('SELECT SUM(stars) FROM repositories')
        total_stars = cursor.fetchone()[0] or 0

        cursor.execute('SELECT AVG(stars) FROM repositories')
        avg_stars = round(cursor.fetchone()[0] or 0, 2)
        app.logger.info("Calculated repo statistics successfully")

        return total, total_stars, avg_stars, languages
    except Exception as e:
        app.logger.error(f"Error calculating repo statistics. ERROR: {str(e)}")
