from datetime import datetime
import requests
from flask import current_app as app
import schedule
import time

from app.repositories.github_repo import store_data


# Fetch data from GitHub API
def fetch_github_data(topic, per_page=30):
    url = f'https://api.github.com/search/repositories?q=topic:{topic}&sort=stars&order=desc&per_page={per_page}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('items', [])
    except Exception as e:
        app.logger.info(f"Error fetching data: {e}")
        return []


# Automated data fetching
def auto_fetch():
    app.logger.info(f"[{datetime.now()}] Fetching GitHub data...")
    repos = fetch_github_data()
    if repos:
        store_data(repos)
        app.logger.info(f"Stored {len(repos)} repositories")


# Schedule background task
def run_scheduler():
    schedule.every(1).hours.do(auto_fetch)
    while True:
        schedule.run_pending()
        time.sleep(60)
