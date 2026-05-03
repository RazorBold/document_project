import os
import sqlite3

basedir = os.path.abspath(os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

DB_PATH = os.path.join(basedir, os.getenv('DB_PATH', 'monitoring.db'))
SCHEMA_PATH = os.path.join(basedir, 'schema.sql')


def init():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    with open(SCHEMA_PATH, encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print(f"Database initialized at: {DB_PATH}")


if __name__ == '__main__':
    init()
