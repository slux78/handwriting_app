import sqlite3
import hashlib
import datetime
import os

DB_FILENAME = "transcription.db"

def get_db_path(base_dir=None):
    if base_dir is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, DB_FILENAME)

def init_db(db_path=None):
    if db_path is None:
        db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transcriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            category TEXT,
            content TEXT NOT NULL,
            char_count INTEGER NOT NULL,
            date TEXT NOT NULL,
            created_at TEXT NOT NULL,
            content_hash TEXT UNIQUE
        );
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_transcriptions_date ON transcriptions(date);
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS title_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            created_at TEXT NOT NULL
        );
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_title_history_title ON title_history(title);
    """)
    conn.commit()
    conn.close()

def _hash_content(text):
    # Normalize whitespace before hashing
    normalized = " ".join(text.strip().split())
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

def is_content_duplicate(content, db_path=None):
    if db_path is None:
        db_path = get_db_path()
    h = _hash_content(content)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id FROM transcriptions WHERE content_hash = ?", (h,))
    row = cur.fetchone()
    conn.close()
    return row is not None

def get_existing_titles_and_authors(limit=50, db_path=None):
    if db_path is None:
        db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT title, author, category FROM transcriptions ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return [{"title": r[0], "author": r[1] or "", "category": r[2] or ""} for r in rows]

def save_transcription(title, author, category, content, custom_date=None, db_path=None):
    if db_path is None:
        db_path = get_db_path()
    now = datetime.datetime.now()
    created_at = now.strftime("%Y-%m-%d %H:%M:%S")
    date_str = custom_date if custom_date else now.strftime("%Y-%m-%d")
    char_count = len(content.strip())
    content_hash = _hash_content(content)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO transcriptions (title, author, category, content, char_count, date, created_at, content_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (title.strip(), (author or "").strip(), (category or "").strip(), content.strip(), char_count, date_str, created_at, content_hash))
        conn.commit()
        record_id = cur.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        return None  # Duplicate
    conn.close()
    return get_transcription_by_id(record_id, db_path)

def get_transcription_by_id(record_id, db_path=None):
    if db_path is None:
        db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM transcriptions WHERE id = ?", (record_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def get_dates_summary(db_path=None):
    if db_path is None:
        db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        SELECT date, count(id) as cnt, max(created_at) as latest
        FROM transcriptions
        GROUP BY date
        ORDER BY date DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return [{"date": r[0], "count": r[1], "latest": r[2]} for r in rows]

def get_transcriptions_by_date(date_str, db_path=None):
    if db_path is None:
        db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, author, category, substr(content, 1, 100) as snippet, char_count, date, created_at
        FROM transcriptions
        WHERE date = ?
        ORDER BY id DESC
    """, (date_str,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_recent_transcriptions(limit=20, db_path=None):
    if db_path is None:
        db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, author, category, substr(content, 1, 120) as snippet, char_count, date, created_at
        FROM transcriptions
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_setting(key, default=None, db_path=None):
    if db_path is None:
        db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else default

def set_setting(key, value, db_path=None):
    if db_path is None:
        db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO settings (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
    """, (key, value))
    conn.commit()
    conn.close()

def save_title_history(title, author="", db_path=None):
    """생성된 제목을 이력에 저장 (중복 방지용)."""
    if db_path is None:
        db_path = get_db_path()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO title_history (title, author, created_at) VALUES (?, ?, ?)",
        (title.strip(), (author or "").strip(), now)
    )
    conn.commit()
    conn.close()

def get_title_history(limit=500, db_path=None):
    """생성 이력에서 제목 목록을 가져옴."""
    if db_path is None:
        db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "SELECT DISTINCT title, author FROM title_history ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    return [{"title": r[0], "author": r[1] or ""} for r in rows]
