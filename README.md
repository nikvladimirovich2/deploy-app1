# APP stack usage
This document describes how to use the `deployctl.py` utility to manage the application stack.
---
## Requirements

Before using `deployctl.py`, ensure the following components are installed on the host:

- Python 3.9+
- Docker
- Docker Compose (v2)
- PostgreSQL client libraries
- curl

### Python dependencies

The following Python packages are required:

- psycopg2
- python-dotenv

---

## Environment Variables

The utility loads its configuration from a `.env` file or directly from environment variables.

### Required / Optional Variables
- DB_HOST=localhost
- DB_USER=app1_user
- POSTGRES_PASS=app1_pass
- DB_NAME=app1_db

Replace the default values with your own configuration before running the application.

## Commands
1. Deploy application stack

Starts the Docker Compose stack, waits for the database to become ready, applies migrations, and checks application health.
   ```
   python3 deployctl.py up
   ```

Expected behavior

- Runs docker compose up -d
- Polls PostgreSQL until it is reachable (up to 30 seconds)
- Applies SQL migrations from scripts/migrations.sql
- Waits for the application to start
- Checks application health via HTTP endpoint

Example output
    ```
    {
        "status": "Application deployed successfully"
    }
    ```

2. Roll back the deployment

Restarts the Docker Compose stack to restore the previous application state.

To perform a rollback, update the APP_TAG (or another relevant tag variable) in the .env file to the required value, then run:
   ```
   python3 deployctl.py rollback
   ```

Example output
    ```
    {
        "status": "App rolled back successfully"
    }
    ```

3. Stop the application stack

Stops and removes all containers defined in the Docker Compose file.

   ```
   python3 deployctl.py down
   ```

Example output
    ```
    {
        "status": "Application down successfully"
    }
    ```