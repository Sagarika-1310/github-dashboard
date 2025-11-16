# 🌐 GitScope – GitHub Repository Intelligence Dashboard

GitScope is a lightweight Flask application that fetches GitHub repository data, stores it in SQLite, and exposes structured APIs for filtering, analytics, and exploration. Includes secure authentication, modular architecture, logging, and clean repository-service patterns.

---

## 🚀 Features

- 🔐 **User Authentication** (Login & Registration, hashed passwords)
- 📊 **GitHub Repository Fetching** (topic-based, sorted by stars)
- 📡 **REST API Endpoints**
  - `/repo/get_repos`
  - `/repo/top_repos`
  - `/repo/stats`
  - `/repo/fetch_repos`
- 🧱 **Scalable Architecture**
  - Routes → Services → Repositories → DB
- 🗃️ **SQLite Database** for local caching
- 📝 **Structured Logging** with rotating file logs
- 🎨 **Minimal HTML UI** for login & actions

---

## 🏗️ Architecture Overview

                       ┌─────────────────────────┐
                       │       Client (UI)       │
                       │  HTML Templates + JS    │
                       └────────────┬────────────┘
                                    │ HTTP
                                    ▼
                      ┌────────────────────────────┐
                      │        Flask App           │
                      │     (Application Factory)  │
                      └────────────┬───────────────┘
                                   │
               ┌───────────────────┼────────────────────┐
               ▼                   ▼                    ▼
    ┌────────────────┐  ┌────────────────────┐  ┌────────────────────┐
    │   Auth Routes  │  │   Github Routes    │  │  Logger Setup      │
    └──────┬─────────┘  └──────────┬─────────┘  └─────────┬──────────┘
           │                       │                      │
           ▼                       ▼                      │
  ┌───────────────────┐   ┌────────────────────┐          │
  │  Auth Repository  │   │ GitHub Repository  │          │
  └────────┬──────────┘   └──────────┬─────────┘          │
           │                         │                    │
           ▼                         ▼                    │
 ┌─────────────────┐     ┌─────────────────────────┐      │
 │ SQLite Database │◄────│ Decorator: db_connect() │──────┘
 └─────────────────┘     └─────────────────────────┘

---

## ⚙️ Setup

- git clone <repo>
- cd GitScope
- python -m venv venv
- source venv/bin/activate
- pip install -r requirements.txt
- flask run

---


---

## 📡 API Summary

### GET `/repo/get_repos`
Query params: `language`, `limit`, `min_stars`

### GET `/repo/top_repos`
Query params: `limit`

### GET `/repo/stats`
Returns total repo count, stars, averages, languages

### POST `/repo/fetch_repos`
Body:
```json
{ "topic": "python", "limit": 10 }

