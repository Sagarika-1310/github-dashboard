"""
Repository layer for storing and retrieving GitHub repository metadata.

This module centralizes all data access logic for the `repositories` table,
including table creation, record insertion, filtering, statistics, and
top-repository queries. All DB operations are wrapped using the db_connect
decorator to ensure consistent connection handling.
"""

from flask import current_app as app
from datetime import datetime

from app.utils.db_utils import db_connect


@db_connect()
def init_repo_table(cursor):
    """
    Create the 'repositories' table if it does not exist.

    Args:
        cursor (sqlite3.Cursor): Provided by db_connect decorator.

    Raises:
        Exception: If table creation fails.
    """
    try:
        app.logger.info("Ensuring 'repositories' table exists...")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS repositories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_name TEXT NOT NULL,
                full_repo_name TEXT UNIQUE NOT NULL,
                repo_url TEXT NOT NULL,
                description TEXT,
                stars INTEGER DEFAULT 0,
                forks INTEGER DEFAULT 0,
                language TEXT,
                created_at TEXT,
                updated_at TEXT,
                fetched_at TEXT
            );
            """
        )

        app.logger.info("'repositories' table is ready.")

    except Exception as e:
        app.logger.error(f"Failed to create 'repositories' table: {str(e)}")
        raise


@db_connect()
def store_data(cursor, repos):
    """
    Insert or update GitHub repository metadata into the database.

    Args:
        cursor (sqlite3.Cursor): Provided by db_connect decorator.
        repos (list): List of GitHub repository JSON objects.

    Raises:
        ValueError: If repos is not a list.
        KeyError: If a repository object is missing required fields.
        Exception: For any SQL execution failure.
    """
    try:
        if not isinstance(repos, list):
            raise ValueError("Expected 'repos' to be a list of GitHub repositories.")

        count = len(repos)
        fetched_time = datetime.utcnow().isoformat()
        app.logger.info(f"Storing {count} repositories into the database...")

        for repo in repos:
            required_keys = ["name", "full_name", "html_url", "stargazers_count", "forks_count"]
            missing = [key for key in required_keys if key not in repo]

            if missing:
                raise KeyError(f"Missing required fields in repo object: {missing}")

            repo_name = repo["name"]
            app.logger.debug(f"Processing repo: '{repo_name}'")

            cursor.execute(
                """
                INSERT OR REPLACE INTO repositories
                (repo_name, full_repo_name, repo_url, description, stars, forks, language,
                    created_at, updated_at, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    repo["name"],
                    repo["full_name"],
                    repo["html_url"],
                    repo.get("description"),
                    repo.get("stargazers_count", 0),
                    repo.get("forks_count", 0),
                    (repo.get("language") or "").lower(),
                    repo.get("created_at"),
                    repo.get("updated_at"),
                    fetched_time
                )
            )

        app.logger.info("All repository records stored successfully.")

    except Exception as e:
        app.logger.error(f"Error storing repository data: {str(e)}")
        raise


@db_connect()
def get_all_repos(cursor, language=None, limit=None, min_stars=None):
    """
    Retrieve repositories with optional filters.

    Args:
        cursor (sqlite3.Cursor): Provided by db_connect decorator.
        language (str, optional): Filter by programming language.
        limit (int, optional): Limit the number of rows returned.
        min_stars (int, optional): Minimum number of stars required.

    Returns:
        list[dict]: List of repository rows as dictionaries.

    Raises:
        Exception: SQL execution error.
    """
    try:
        app.logger.info(
            "Fetching repositories with filters: "
            f"language={language}, min_stars={min_stars}, limit={limit}"
        )

        query = "SELECT * FROM repositories WHERE 1=1"
        params = []

        if language:
            query += " AND LOWER(language) = ?"
            params.append(language.lower())

        if min_stars is not None:
            query += " AND stars >= ?"
            params.append(min_stars)

        query += " ORDER BY stars DESC"

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        cursor.execute(query, params)
        repos = [dict(row) for row in cursor.fetchall()]

        app.logger.info(f"Successfully fetched {len(repos)} repositories.")
        return repos

    except Exception as e:
        app.logger.error(f"Error fetching repositories: {str(e)}")
        raise


@db_connect()
def get_all_top_repos(cursor, limit):
    """
    Retrieve the top N repositories sorted by star count.

    Args:
        cursor (sqlite3.Cursor): Provided by db_connect decorator.
        limit (int): Number of top repositories to return.

    Returns:
        list[dict]: List of top repository rows.

    Raises:
        Exception: SQL execution error.
    """
    try:
        app.logger.info(f"Fetching top {limit} repositories by stars...")

        cursor.execute(
            "SELECT * FROM repositories ORDER BY stars DESC LIMIT ?",
            (limit,)
        )

        repos = [dict(row) for row in cursor.fetchall()]

        app.logger.info(f"Fetched {len(repos)} top repositories.")
        return repos

    except Exception as e:
        app.logger.error(f"Error fetching top repositories: {str(e)}")
        raise


@db_connect()
def get_all_stats(cursor):
    """
    Compute repository statistics including total count, total stars,
    average stars, and language distribution.

    Args:
        cursor (sqlite3.Cursor): Provided by db_connect decorator.

    Returns:
        tuple:
            int: total number of repositories
            int: total stars
            float: average stars (rounded to 2 decimals)
            list[dict]: language distribution entries

    Raises:
        Exception: SQL execution failure.
    """
    try:
        app.logger.info("Computing repository statistics...")

        cursor.execute("SELECT COUNT(*) FROM repositories")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(stars) FROM repositories")
        total_stars = cursor.fetchone()[0] or 0

        cursor.execute("SELECT AVG(stars) FROM repositories")
        avg_stars = round(cursor.fetchone()[0] or 0.0, 2)

        cursor.execute(
            "SELECT language, COUNT(*) AS count FROM repositories "
            "GROUP BY language ORDER BY count DESC"
        )

        languages = [{"language": row[0], "count": row[1]} for row in cursor.fetchall()]

        app.logger.info("Repository statistics computed successfully.")
        return total, total_stars, avg_stars, languages

    except Exception as e:
        app.logger.error(f"Error computing repository statistics: {str(e)}")
        raise
