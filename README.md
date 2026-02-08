# APP stack usage

## Requirements
Before using deployctl.py, ensure the following are installed on the host:
### Python 3.9+
### Docker
### Docker Compose (v2)
### PostgreSQL client libraries
### curl

Python dependencies:
### psycopg2
### python-dotenv

## Environment Variables

The utility loads configuration from a .env file or environment variables.

Required / Optional Variables
### DB_HOST=localhost
### DB_USER=app1_user
### POSTGRES_PASS=app1_pass
### DB_NAME=app1_db

Put your definitions insted defaults

## Commands
1. Deploy application stack:
   ```
   python3 deployctl.py up
   ```
Expected behavior

### Runs docker compose up -d
### Polls PostgreSQL until it is reachable (up to 30 seconds)
### Applies SQL migrations from scripts/migrations.sql
### Waits for the application to start
### Checks application health via HTTP endpoint

Example output
    ```
    {
        "status": "Application deployed successfully"
    }
    ```

2. Rollback deployment:
Re-runs the Docker Compose stack to restore the previous application state.
For using change TAG variable in .env file to needed and run command
   ```
   python3 deployctl.py rollback
   ```

Example output
    ```
    {
        "status": "App rolled back successfully"
    }
    ```

3. Stop application stack:
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