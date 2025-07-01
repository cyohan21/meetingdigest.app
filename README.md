# MeetingDigest

MeetingDigest is a Flask backend for recording meeting audio, transcribing it, and generating concise summaries with OpenAI. The service provides JWT-based authentication as well as Google OAuth login and lets users store and manage their transcripts.

## Features
- RESTful API built with **Flask** and **SQLAlchemy**
- Endpoint to upload audio files which are transcribed and summarized
- User registration, login and password management with JWT tokens
- Optional Google OAuth sign-in
- Endpoints to view or delete previous recordings
- Database migrations managed by **Flask-Migrate**

## Setup
1. Create a virtual environment and install the requirements:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. Configure the environment variables listed in `backend/config.py`. Common settings include:
   - `SECRET_KEY` – Flask session secret
   - `OPENAI_API_KEY` – token for OpenAI API access
   - `JWT_SECRET_KEY` – signing key for JWTs
   - `DATABASE_URL` – database connection string (uses SQLite by default)
   - `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` – for OAuth (optional)
3. Run the database migrations:
   ```bash
   export FLASK_APP=app
   flask db upgrade
   ```
4. Start the development server:
   ```bash
   python backend/run.py
   ```

## Running tests
Execute the test suite with `pytest` while pointing `PYTHONPATH` at the backend directory:
```bash
PYTHONPATH=backend pytest -q
```
