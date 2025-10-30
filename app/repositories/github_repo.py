from flask import current_app as app
import sqlite3
from datetime import datetime
import os

db_file = 'github_data.db'
db_dir = os.path.join(app.instance_path, "db")
os.makedirs(db_dir, exist_ok=True)
db_path = os.path.join(db_dir, db_file)


# Database setup
def init_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS repositories
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  full_name TEXT UNIQUE,
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
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    fetched_time = datetime.now().isoformat()

    for repo in repos:
        try:
            c.execute('''INSERT OR REPLACE INTO repositories 
                        (name, full_name, description, stars, forks, language, created_at, updated_at, fetched_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (repo['name'], repo['full_name'], repo['description'],
                       repo['stargazers_count'], repo['forks_count'], repo['language'],
                       repo['created_at'], repo['updated_at'], fetched_time))
        except Exception as e:
            app.logger.info(f"Error storing repo {repo.get('name')}: {e}")

    conn.commit()
    conn.close()
