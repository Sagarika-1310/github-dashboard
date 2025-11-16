"""Service layer for managing GitHub API interactions.

This module provides functions to interact with the GitHub REST API
to fetch repository data based on topics. All external API calls are
centralized here to maintain clean separation of concerns.

Functions:
    fetch_github_data(topic: str, per_page: int) -> list
"""

import requests
from requests.exceptions import (
    ConnectionError,
    Timeout,
    HTTPError,
    RequestException
)
from flask import current_app as app


def fetch_github_data(topic: str = "python", per_page: int = 30) -> list:
    """
    Fetch GitHub repositories for a given topic, sorted by stars (descending).

    Args:
        topic (str): GitHub topic to search for (default: "python").
        per_page (int): Number of repositories to fetch per page (max 100 allowed by GitHub).

    Returns:
        list: A list of repository objects retrieved from the GitHub API.

    Raises:
        ConnectionError: If network issues prevent API communication.
        Timeout: If the API call times out.
        HTTPError: If GitHub API returns a non-2xx status.
        RequestException: For any other request-level exceptions.
        Exception: For unexpected/unclassified errors.
    """
    app.logger.info(
        f"Fetching repositories from GitHub API -> topic={topic}, per_page={per_page}"
    )

    url = (
        "https://api.github.com/search/repositories"
        f"?q=topic:{topic}&sort=stars&order=desc&per_page={per_page}"
    )

    headers = {}

    try:
        response = requests.get(url, headers=headers, timeout=10)

        # Raise HTTPError for non-200 status
        response.raise_for_status()

        data = response.json()
        items = data.get("items", [])

        app.logger.info(
            f"Successfully fetched {len(items)} repositories for topic={topic}"
        )

        return items

    except ConnectionError as ce:
        app.logger.error(f"GitHub API connection error: {str(ce)}")
        raise ConnectionError("Unable to connect to GitHub API.") from ce

    except Timeout as te:
        app.logger.error(f"GitHub API request timed out: {str(te)}")
        raise Timeout("GitHub API request timed out.") from te

    except HTTPError as he:
        status = getattr(he.response, 'status_code', None)
        if status == 403:
            app.logger.error("GitHub rate limit exceeded.")
            raise HTTPError("GitHub API rate limit exceeded.") from he

        app.logger.error(f"GitHub API returned an HTTP error: {str(he)}")
        raise HTTPError(f"GitHub API HTTP error: {str(he)}") from he

    except RequestException as re:
        app.logger.error(f"Unexpected error during GitHub request: {str(re)}")
        raise RequestException("Unexpected error during GitHub request.") from re

    except Exception as e:
        app.logger.error(f"Unexpected exception in fetch_github_data: {str(e)}")
        raise Exception("Internal error fetching GitHub data.") from e
