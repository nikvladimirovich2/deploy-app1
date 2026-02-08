import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify

app = Flask(__name__)

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT", 5432),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

TABLE_NAME = os.getenv("DB_TABLE")


def get_db_connection():
    return psycopg2.connect(
        **DB_CONFIG,
        cursor_factory=RealDictCursor
    )


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}, 200


@app.route("/data", methods=["GET"])
def get_table_data():
    if not TABLE_NAME:
        return {"error": "DB_TABLE is not set"}, 500

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        query = f"SELECT * FROM {TABLE_NAME};"
        cur.execute(query)

        rows = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify({
            "table": TABLE_NAME,
            "count": len(rows),
            "data": rows
        })

    except Exception as e:
        return {
            "error": "database query failed",
            "details": str(e)
        }, 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)