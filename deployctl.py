import argparse
import subprocess
import time
import json
import os
import psycopg2
import sys
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

load_dotenv()

COMPOSE_FILE = 'docker-compose.yaml'
MIGRATION_FILE = './scripts/migrations.sql'
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = 5432
DB_USER = os.getenv("DB_USER", "app1_user")
DB_PASSWORD = os.getenv("POSTGRES_PASS", "app1_pass")
DB_NAME = os.getenv("DB_NAME", "app1_db")
APP_HEALTH_URL = 'http://localhost:8080/health'

def run_command(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode()
    except subprocess.CalledProcessError as e:
        return {"error": e.output.decode()}

def wait_for_db():
    for _ in range(30):
        try:
            conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, dbname=DB_NAME)
            conn.close()
            return True
        except:
            time.sleep(1)
    return False

def apply_migration():
    with open(MIGRATION_FILE, 'r') as f:
        sql = f.read()
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, dbname=DB_NAME)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(sql)
    cur.close()
    conn.close()

def check_app_health():
    response = run_command("curl -f " + APP_HEALTH_URL)
    return "error" not in response

def up():
    output = run_command(f"docker compose -f {COMPOSE_FILE} up -d")
    if "error" in output:
        return {"status": "failed", "details": output}
    else:
        print("Docker compose started successfully")

    if not wait_for_db():
        return {"status": "failed", "details": "DB not ready"}
    else:
        print("DB is ready")

    apply_migration()

    time.sleep(5)  # Wait for app
    if not check_app_health():
        return {"status": "failed", "details": "App healthcheck failed"}
    else:
        print("App is healthy")

    return {"status": "success"}

def rollback():
    output = run_command(f"docker compose -f {COMPOSE_FILE} up -d")
    return {"status": "success" if "error" not in output else "failed", "details": output}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    subparsers.add_parser('up')
    subparsers.add_parser('rollback')

    args = parser.parse_args()

    if args.command == 'up':
        result = up()
    elif args.command == 'rollback':
        result = rollback()
    else:
        print("Invalid command\nUsage: deployctl.py [up|rollback]")
        sys.exit(1)

    print(json.dumps(result))