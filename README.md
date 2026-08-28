# Hackulus 2026 FastAPI Backend (`hackulus26-be-fastAPI`)

A high-performance, asynchronous FastAPI backend service for managing the Hackulus Hackathon.

## 🚀 Features

- **Consolidated 6-Table DB Architecture**: Streamlined SQL schema combining User/Admin entities, atomic reviews with `UNIQUE(submission_id, judge_id)` conflict handling, and flexible event phase configuration.
- **Service Layer Architecture**: Clean decoupling between HTTP routes, business logic services, database models, and schemas.
- **Admin Endpoints**:
  - `POST /admin/team/create-with-members`: Create teams and bulk insert all members in a single atomic transaction.
  - `POST /admin/team/{team_id}/add-member`: Add individual members directly to existing teams.
  - `POST /admin/assign-panels`: Automatic FCFS track-to-panel assignment algorithm.
- **Interactive Swagger Documentation**: Built-in interactive documentation at `/docs` and `/redoc`.

---

## 🛠️ Setup Instructions

### 1. Environment & Dependencies

Create a virtual environment and install dependencies:

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Database Initialization

Ensure PostgreSQL is running and update connection details in `.env` if necessary.

Initialize tables:
```bash
python setup_db.py
```

Seed dummy tracks, panels, and Admin account:
```bash
python seed_dummy_data.py
```

### 3. Run Development Server

```bash
uvicorn app.main:app --reload --port 8000
```

Open your browser to [http://localhost:8000/docs](http://localhost:8000/docs) to view the API documentation.
