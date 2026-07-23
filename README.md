# AgencyDesk - Multi-Tenant Client & Project Portal

AgencyDesk is a multi-tenant client and project management platform built with **FastAPI (Python)**, **PostgreSQL (SQLAlchemy / Alembic)**, and **Next.js (TypeScript / Tailwind CSS)**.

---

## ⚡ Quick Start (< 10 Minutes)

### Prerequisites
* Python 3.10+
* Node.js 18+
* PostgreSQL database

---

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Seed initial database (creates 2 agencies, users, projects, & tasks)
python seed.py

# Start backend server
uvicorn app.main:app --reload --port 8000

```

Backend API will be running at `http://127.0.0.1:8000` (API Docs at `http://127.0.0.1:8000/docs`).

---

### 2. Frontend Setup

```bash
# Open a new terminal and navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Next.js development server
npm run dev

```

Frontend web app will be running at `http://localhost:3000`.

---

## 🔑 Demo Seed Credentials

| Role | Email | Password |
| --- | --- | --- |
| **Agency Admin** | `admin@apexdigital.com` | `password123` |
| **Agency Member** | `dev@apexdigital.com` | `password123` |
| **Client User** | `client@acmecorp.com` | `password123` |

---

## 🧪 Running Tests

To verify tenant isolation and RBAC rules:

```bash
cd backend
pytest
```