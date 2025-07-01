# Backend Service

This directory contains the Flask application for MeetingDigest.

## Requirements

- Python 3.11+
- The packages listed in `requirements.txt`

## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Provide the required environment variables (either in a `.env` file or in your shell):
   - `SECRET_KEY`
   - `JWT_SECRET_KEY`
   - `OPENAI_API_KEY`
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `DATABASE_URL` (optional, defaults to `sqlite:///dev.db`)
4. Initialize the database (for a new setup):
   ```bash
   export FLASK_APP=run.py
   flask db upgrade
   ```

## Running the server

Start the app in development mode:
```bash
python run.py
```
The service listens on port `1011`. Set `FLASK_ENV` to `dev`, `prod`, or `test` to switch configurations.

## Basic usage

Key endpoints:
- `/api/auth/*` – register, log in, refresh tokens, and similar operations
- `/api/oauth/google/*` – Google OAuth flow
- `/transcribe` – upload an audio file and receive a transcript and summary (requires authentication)
- `/records/view` – list, retrieve, or delete saved records (requires authentication)

Run the unit tests with:
```bash
pytest
```

