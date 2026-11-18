"""Database access layer.

- If DATABASE_URL is set (e.g. Postgres (Neon)), connects with psycopg.
- Otherwise falls back to the local SQLite file (config DATABASE).

Route code keeps using the sqlite3-style API:
    conn.execute(sql_with_?_placeholders, params) -> cursor
    cursor.fetchone() / fetchall() / lastrowid
    conn.commit() / rollback() / close()
"""
import os
import sqlite3
from flask import current_app


def _database_url():
    return os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL')


def _to_pg_sql(sql):
    """Convert sqlite '?' placeholders to psycopg '%s' and escape literal '%'.

    Characters inside single-quoted string literals are left untouched
    (except '%', which must always be doubled when params are passed).
    """
    out = []
    in_str = False
    for ch in sql:
        if ch == "'":
            in_str = not in_str
            out.append(ch)
        elif ch == '%':
            out.append('%%')
        elif ch == '?' and not in_str:
            out.append('%s')
        else:
            out.append(ch)
    return ''.join(out)


class _PgCursor:
    def __init__(self, cur, lastrowid=None, prefetched=None):
        self._cur = cur
        self.lastrowid = lastrowid
        self._prefetched = prefetched

    def fetchone(self):
        if self._prefetched is not None:
            return self._prefetched[0] if self._prefetched else None
        if self._cur.description is None:
            return None
        return self._cur.fetchone()

    def fetchall(self):
        if self._prefetched is not None:
            return list(self._prefetched)
        if self._cur.description is None:
            return []
        return self._cur.fetchall()

    def __iter__(self):
        return iter(self.fetchall())

    @property
    def rowcount(self):
        return self._cur.rowcount


class _PgConnection:
    def __init__(self, url):
        import psycopg
        from psycopg.rows import dict_row
        # prepare_threshold=None -> works with pgbouncer-style poolers (Neon pooled URL, Supabase pooler)
        self._conn = psycopg.connect(url, row_factory=dict_row, prepare_threshold=None,
                                     connect_timeout=10)

    def execute(self, sql, params=()):
        pg_sql = _to_pg_sql(sql).rstrip().rstrip(';')
        is_insert = pg_sql.lstrip().upper().startswith('INSERT')
        if is_insert and 'RETURNING' not in pg_sql.upper():
            pg_sql += ' RETURNING id'
        cur = self._conn.cursor()
        # Always pass a tuple so psycopg parses placeholders and un-escapes '%%'
        cur.execute(pg_sql, tuple(params or ()))
        if is_insert:
            rows = cur.fetchall() if cur.description else []
            lastrowid = rows[0]['id'] if rows and 'id' in rows[0] else None
            return _PgCursor(cur, lastrowid=lastrowid, prefetched=rows)
        return _PgCursor(cur)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()


def get_db():
    url = _database_url()
    if url:
        return _PgConnection(url)
    conn = sqlite3.connect(current_app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn
