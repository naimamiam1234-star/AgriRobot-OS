"""Durable simulated dose ledger. No physical I/O."""
import json
import sqlite3
import threading
from datetime import datetime, timezone


class Store:
    def __init__(self, path):
        self.lock = threading.RLock()
        self.db = sqlite3.connect(str(path), check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY, created TEXT NOT NULL, payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS doses (
                request_id TEXT PRIMARY KEY, plant_id TEXT NOT NULL,
                volume_ml REAL NOT NULL, channel TEXT NOT NULL,
                created TEXT NOT NULL, status TEXT NOT NULL);
        ''')

    def close(self):
        self.db.close()

    def record_event(self, event):
        with self.lock, self.db:
            self.db.execute('INSERT INTO events(created,payload) VALUES(?,?)',
                            (datetime.now(timezone.utc).isoformat(), json.dumps(event, ensure_ascii=False, allow_nan=False)))

    def events(self):
        with self.lock:
            return [dict(r) for r in self.db.execute('SELECT * FROM events ORDER BY id DESC LIMIT 100')]

    def doses(self):
        with self.lock:
            return [dict(r) for r in self.db.execute('SELECT * FROM doses ORDER BY created')]

    def pending(self):
        with self.lock:
            return self.db.execute("SELECT count(*) FROM doses WHERE status='pending'").fetchone()[0]

    def reserve(self, request_id, plant_id, volume_ml, channel):
        now = datetime.now(timezone.utc).isoformat()
        with self.lock:
            try:
                self.db.execute('BEGIN IMMEDIATE')
                total = self.db.execute('''SELECT COALESCE(SUM(volume_ml),0) FROM doses
                    WHERE plant_id=? AND channel=? AND substr(created,1,10)=?''',
                    (plant_id, channel, now[:10])).fetchone()[0]
                if total + volume_ml > 2000:
                    raise ValueError('simulation_daily_limit')
                self.db.execute('INSERT INTO doses VALUES(?,?,?,?,?,?)',
                                (request_id, plant_id, volume_ml, channel, now, 'pending'))
                self.db.commit()
            except sqlite3.IntegrityError as exc:
                self.db.rollback()
                raise ValueError('duplicate_request') from exc
            except Exception:
                self.db.rollback()
                raise

    def finish_simulation(self, request_id):
        with self.lock, self.db:
            self.db.execute("UPDATE doses SET status='simulated' WHERE request_id=? AND status='pending'", (request_id,))
