# 🛠️ DevForge - The Operating System for Student Developers

> **DevForge** is a production-quality backend application designed to help engineering students manage developer projects, analyze live GitHub repository activity, track portfolio progress, and receive AI-powered resume & skill insights.

---

## 🌟 Features

- 🔐 **JWT Authentication & Security:** Password hashing with `bcrypt`, stateless JSON Web Token generation, and OAuth2 protected routes.
- 📁 **Project Management (CRUD):** Create, update, delete, and filter portfolio projects by tech stack, project status (`in_progress`, `completed`), and title.
- 🐙 **GitHub REST API Integration:** Dynamic repository analysis, total star counts, language distribution, and activity fetching.
- 📊 **Dashboard & Portfolio Analytics:** Aggregated developer statistics, completion rates, and top programming languages across student projects.
- 🤖 **AI Portfolio Insights:** Heuristic engine that evaluates project count, database integration, testing breadth, and containerization to generate actionable resume improvement recommendations.
- 📑 **Self-Documenting API:** Interactive Swagger UI documentation automatically generated via FastAPI OpenAPI specs.

---

## 📐 System Architecture

```text
                               +-------------------+
                               |  Client / Swagger |
                               +---------+---------+
                                         |
                                         v
                               +---------+---------+
                               |  FastAPI Router   |
                               +---------+---------+
                                         |
          +------------------+-----------+-----------+------------------+
          |                  |                       |                  |
          v                  v                       v                  v
    +-----+------+    +------+-----+           +-----+------+     +-----+------+
    | Auth API   |    | Projects   |           | GitHub API |     | AI Insights|
    +-----+------+    +------+-----+           +-----+------+     +-----+------+
          |                  |                       |                  |
          v                  v                       v                  v
    +-----+------+    +------+-----+           +-----+------+     +-----+------+
    |  Security  |    | SQLAlchemy |           | GitHub REST|     | Portfolio  |
    | (JWT/Bcrypt|    |  ORM Model |           |  Service   |     | Analyzer   |
    +------------+    +------+-----+           +------------+     +------------+
                             |
                             v
                      +------+-----+
                      | PostgreSQL |
                      |  / SQLite  |
                      +------------+
```

---

## 🛠️ Tech Stack

- **Framework:** Python, FastAPI
- **Database:** PostgreSQL (Supabase / Production) / SQLite (Local Dev)
- **ORM:** SQLAlchemy (Session management & Relational Models)
- **Authentication:** PyJWT / `python-jose`, `bcrypt`
- **Validation:** Pydantic v2
- **Testing:** Pytest / TestClient
- **Configuration:** `python-dotenv`

---

## 🚀 Quick Start Guide

### 1. Clone & Set Up Environment

```bash
# Clone repository
git clone https://github.com/your-username/DevForge.git
cd DevForge

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```env
APP_NAME=DevForge
APP_VERSION=1.0.0
SECRET_KEY=your_super_secret_jwt_key_here
DATABASE_URL=sqlite:///./devforge.db
```

### 3. Run Application Server

```bash
uvicorn app.main:app --reload
```

Server will be running live at: `http://127.0.0.1:8000`  
Interactive Swagger API Docs available at: `http://127.0.0.1:8000/docs`

---

## 🔌 API Endpoint Summary

| Category | Method | Endpoint | Description | Auth Required |
|---|---|---|---|---|
| **Health** | `GET` | `/` | Health check & API status | No |
| **Auth** | `POST` | `/api/auth/register` | Register new student developer | No |
| **Auth** | `POST` | `/api/auth/login` | Authenticate user & receive JWT | No |
| **Auth** | `GET` | `/api/auth/me` | Get current user profile | Yes |
| **Projects** | `POST` | `/api/projects/` | Create portfolio project | Yes |
| **Projects** | `GET` | `/api/projects/` | List & filter projects | Yes |
| **Projects** | `GET` | `/api/projects/{id}` | Get single project | Yes |
| **Projects** | `PUT` | `/api/projects/{id}` | Update project | Yes |
| **Projects** | `DELETE` | `/api/projects/{id}` | Delete project | Yes |
| **Dashboard**| `GET` | `/api/dashboard/stats` | Portfolio metrics & stats | Yes |
| **GitHub** | `GET` | `/api/github/user-stats` | Authenticated user GitHub repos | Yes |
| **GitHub** | `GET` | `/api/github/user/{username}` | Any public GitHub profile stats | No |
| **AI** | `GET` | `/api/ai/resume-insights` | AI resume & skill suggestions | Yes |

---

## 💼 How to Pitch DevForge on your Resume

> **DevForge — Lead Backend Developer**  
> *Built a production-grade FastAPI & PostgreSQL backend application helping student engineers manage developer portfolios, track GitHub statistics, and receive automated skill insights.*
> - Engineered secure user authentication using **JWT** and **bcrypt** password hashing with custom FastAPI dependency injection for route protection.
> - Modeled relational database schemas using **SQLAlchemy ORM** for 1-to-Many User-to-Project relationships with query filtering.
> - Integrated external **GitHub REST API** to compute repository star metrics, language distributions, and commit activity.
> - Implemented a rule-based AI portfolio engine to analyze developer tech-stack diversity and generate actionable resume skill gap analysis.
