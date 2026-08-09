# DevForge
Developer Portfolio Intelligence Platform

DevForge is a full-stack developer portfolio workspace designed to help engineering students and early-career developers understand and improve their technical portfolio. By combining personal project management with real GitHub activity analytics and AI-powered insights, DevForge provides actionable evidence of your technical strengths and identifies skill gaps before your next interview.

## 🌐 Live Demo
- **Live Application**: `https://devforge-w3kd.onrender.com/`
- **GitHub Repository**: `https://github.com/siddharth1728/DevForge`

---

## 🎯 Why DevForge?

Most student portfolios simply list projects without providing a clear way to understand the technical depth or the evidence behind those projects. 

DevForge bridges this gap. Instead of a static resume, DevForge securely connects to your GitHub account and uses Gemini AI to analyze your repository data alongside your manually entered projects. It returns a dynamic "Portfolio Readiness Score" and highlights exactly what your current codebase demonstrates to an engineering hiring manager.

---

## ✨ Features

### 🔐 Authentication
- Secure User Registration & Login
- JWT-based authentication
- Password hashing using `passlib` (bcrypt)
- Protected API routes ensuring strict user data isolation

### 📁 Project Management
- Complete CRUD operations (Create, Read, Update, Delete) for personal projects
- Track technologies, GitHub URLs, live URLs, and completion status
- Secure ownership checks (users can only access their own projects)

### 🐙 GitHub Integration
- Authenticated, server-side GitHub REST API integration (bypasses unauthenticated rate limits)
- Graceful rate-limit detection and reset-time handling
- Retrieves total repositories, total stars, and top languages
- Generates an estimated language distribution based on real repository byte counts

### 📊 Dashboard
- Real-time aggregation of your total projects, GitHub stars, and top technologies
- A clean, professional UI displaying your strongest technical signals

### 🤖 AI Portfolio Insights
- Integrates with the **Google Gemini API**
- Analyzes your project tech stacks and GitHub data to return:
  - **Portfolio Readiness Score** (0-100)
  - **Strengths** (e.g., "Strong backend foundation in Python")
  - **Missing Skills / Gaps** (e.g., "Lack of CI/CD or testing evidence")
  - **Actionable Recommendations** for your next best steps

---

## 🧠 How DevForge Works

```
      User
       │
       ▼
  Projects + GitHub Activity
       │
       ▼
  Portfolio Data Aggregation
       │
       ▼
  Analytics + AI Analysis (Gemini)
       │
       ▼
  Portfolio Insights
       │
       ▼
  Actionable Improvements
```

---

## 🏗️ System Architecture

```text
       [ Vanilla HTML/CSS/JS Frontend ]
                   │
           (REST API / JSON)
                   │
                   ▼
         [ FastAPI Application ]
         │          │          │
    (urllib)    (SQLAlchemy)  (google-genai)
         │          │          │
         ▼          ▼          ▼
   [ GitHub ]  [ Database ] [ Gemini API ]
```

- **Production Database**: Supabase (PostgreSQL)
- **Local Database**: SQLite

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI, Python 3.14+
- **Data Validation**: Pydantic
- **ORM**: SQLAlchemy

### Database
- SQLite (Local development)
- PostgreSQL (Production via Supabase)

### Authentication
- JWT (JSON Web Tokens)
- `passlib` & `bcrypt`

### External APIs
- **GitHub REST API** (using standard library `urllib` for zero-dependency HTTP requests)
- **Google Gemini API** (`google-genai`)

### Frontend
- HTML5
- Vanilla JavaScript (ES6+)
- Pure CSS (Custom properties, Flexbox/Grid)

### Testing
- `pytest`
- `unittest.mock` (for isolating external API calls)
- `httpx` (for FastAPI `TestClient`)

### Deployment
- **Hosting**: Render (Web Service)
- **Containerization**: Docker (Dockerfile included)

---

## 📂 Project Structure

```text
DevForge/
├── app/
│   ├── api/          # FastAPI route handlers (auth, projects, github, ai)
│   ├── config/       # Environment variables and configuration
│   ├── core/         # JWT security and password hashing
│   ├── database/     # SQLAlchemy engine and session management
│   ├── models/       # SQLAlchemy database models
│   ├── schemas/      # Pydantic schemas for request/response validation
│   ├── services/     # External API logic (GitHub, Gemini)
│   └── static/       # Frontend (index.html, style.css, app.js)
├── tests/            # Pytest test suite and API mocks
├── e2e_test.py       # End-to-end verification script
├── requirements.txt  # Python dependencies
├── .env.example      # Environment variable template
├── Dockerfile        # Production container configuration
└── README.md         # Project documentation
```

---

## 🔌 API Documentation

| Category | Method | Endpoint | Description | Auth |
|---|---|---|---|---|
| **Auth** | POST | `/api/auth/register` | Register a new user account | ❌ |
| **Auth** | POST | `/api/auth/login` | Authenticate and receive JWT | ❌ |
| **Auth** | GET | `/api/auth/me` | Get current user profile | 🔒 |
| **Auth** | PUT | `/api/auth/me` | Update current user profile | 🔒 |
| **Projects** | GET | `/api/projects/` | List all projects for current user | 🔒 |
| **Projects** | POST | `/api/projects/` | Create a new project | 🔒 |
| **Projects** | PUT | `/api/projects/{id}` | Update an existing project | 🔒 |
| **Projects** | DELETE | `/api/projects/{id}` | Delete a project | 🔒 |
| **GitHub** | GET | `/api/github/user-stats` | Fetch real GitHub repo and language stats | 🔒 |
| **AI** | GET | `/api/ai/resume-insights` | Generate AI portfolio readiness analysis | 🔒 |
| **Dashboard** | GET | `/api/dashboard/stats` | Get aggregated stats for the frontend UI | 🔒 |

---

## 🔐 Security

- **Password Security**: Passwords are never stored in plaintext; hashed securely via `bcrypt`.
- **JWT Protection**: All data routes are heavily protected by `Depends(get_current_user)`.
- **Data Isolation**: SQLAlchemy queries strictly filter by `user_id`, preventing lateral data access.
- **Server-Side API Keys**: The `GITHUB_TOKEN` and `GEMINI_API_KEY` are kept securely on the backend. The frontend never touches these tokens.
- **Git Safety**: `.env` is properly ignored via `.gitignore` to prevent secret leaks.

---

## 🧪 Testing

The project is tested using `pytest`.

- **Current Status**: 14/14 tests passing.
- **Test Strategy**: Validates database CRUD operations, JWT token generation, route protection, and edge cases.
- **Mocking**: External calls to the GitHub API are securely isolated and mocked using `unittest.mock.patch` to ensure tests run fast and without internet/rate-limit dependencies.

---

## 🚀 Local Setup

### 1. Clone the repository
```bash
git clone <!-- Add GitHub URL here -->
cd DevForge
```

### 2. Create a virtual environment
**Windows:**
```cmd
python -m venv .venv
.venv\Scripts\activate
```
**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the template file:
```bash
cp .env.example .env
```
Populate `.env` with your values (do not commit this file):
```env
APP_NAME=DevForge
APP_VERSION=1.0.0
SECRET_KEY=
DATABASE_URL=sqlite:///./devforge.db
GEMINI_API_KEY=
GITHUB_TOKEN=
```

### 5. Run the application
```bash
uvicorn app.main:app --reload
```
- **Live Application**: `http://127.0.0.1:8000`
- **API Swagger Docs**: `http://127.0.0.1:8000/docs`

---

## ☁️ Deployment

This application is configured for deployment on **Render** (Web Service) using **Supabase** for the production PostgreSQL database.

Required Render Environment Variables:
- `DATABASE_URL` (Supabase connection string)
- `SECRET_KEY`
- `GEMINI_API_KEY`
- `GITHUB_TOKEN`

---

## 🧩 Engineering Challenges & Solutions

### GitHub API Rate Limiting
**Problem**: The initial implementation used unauthenticated requests to the GitHub REST API, which resulted in severe rate-limiting (60 requests/hour) blocking the production application.
**Solution**: Upgraded the backend to utilize a server-side GitHub Personal Access Token (PAT). Implemented custom header parsing to read `x-ratelimit-remaining` and `x-ratelimit-reset`. If the limit is hit, the backend intercepts the response, calculates the exact reset time from the UNIX timestamp, and gracefully returns a human-readable 429 error to the frontend without crashing.

---

## 💡 Design Decisions

- **Why FastAPI?** Chosen for its exceptional speed, built-in async support, and automatic OpenAPI documentation generation.
- **Why Vanilla JavaScript?** To demonstrate a fundamental understanding of DOM manipulation, asynchronous fetch requests, and frontend architecture without hiding behind the abstractions of React or Vue.
- **Why Server-Side GitHub Auth?** Exposing a GitHub PAT in the frontend exposes it to theft. Proxying requests through the FastAPI backend keeps the token secure while allowing the frontend to receive enriched data safely.
- **Why Mocked API Tests?** Automated tests should be deterministic. Hitting the real GitHub API during CI/CD introduces network latency, rate limits, and flaky tests if repositories change. Mocking ensures rock-solid test reliability.

---

## 📸 Screenshots

### Dashboard
`<!-- Add Dashboard screenshot here -->`

### Projects
`<!-- Add Projects screenshot here -->`

### GitHub Analytics
`<!-- Add GitHub Analytics screenshot here -->`

### AI Portfolio Insights
`<!-- Add AI Insights screenshot here -->`

---

## 🎬 Demo Flow
1. **Register** a secure account.
2. **Login** to enter the workspace.
3. **Create Projects** mapping to your real work.
4. **Fetch Real GitHub Data** to visualize languages and repositories.
5. **Run AI Analysis** to aggregate your projects and GitHub data via Gemini.
6. **Review Insights** to discover your portfolio strengths and skill gaps.

---

## 🎓 Why I Built This

I wanted to build something beyond a standard CRUD tutorial. DevForge forced me to understand how authentication, relational databases, external APIs (GitHub), generative AI (Gemini), testing, and deployment all interconnect in a complete, cohesive application. By keeping the frontend simple with Vanilla JS and the backend strict with FastAPI, I was able to focus heavily on architecture, error handling, and building a polished, reliable product.

---

## 📈 Future Improvements
*(Potential future improvements)*
- Richer GitHub commit activity analysis
- Resume PDF generation
- Job-description parsing and matching
- Integrated interview preparation

---

## Resume Description

**DevForge — Developer Portfolio Intelligence Platform**
- Architected a FastAPI backend using SQLAlchemy and PostgreSQL to manage secure user portfolios and JWT authentication.
- Integrated the GitHub REST API and Google Gemini API to dynamically analyze repositories and generate actionable portfolio insights.
- Implemented robust error handling and rate-limit detection for external APIs using Python's `urllib`, isolating external requests with `unittest.mock` for a 100% passing test suite.
- Designed a cohesive, responsive Vanilla JS frontend prioritizing clean UX, deployed via Docker on Render with a Supabase database.

---

## What This Project Demonstrates
- REST API design and documentation
- Secure JWT Authentication
- Relational Database modeling and ORM usage
- External API integration and Rate-limit handling
- Prompt engineering and AI API integration
- Automated testing with mocks
- Frontend/backend integration
- Production deployment (Render + Supabase)
