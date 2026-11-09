import sqlite3
from pathlib import Path
from datetime import datetime


class HistoryDatabase:
    def __init__(self):
        data_dir = Path.home() / ".quantumcalc"
        data_dir.mkdir(parents=True, exist_ok=True)
        self.path = data_dir / "history.sqlite3"
        self._initialize()

    def _connect(self):
        return sqlite3.connect(self.path)

    def _initialize(self):
        with self._connect() as con:
            con.execute("""CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expression TEXT NOT NULL,
                result TEXT NOT NULL,
                created_at TEXT NOT NULL
            )""")

    def add(self, expression, result):
        with self._connect() as con:
            con.execute(
                "INSERT INTO history(expression, result, created_at) VALUES (?, ?, ?)",
                (expression, result, datetime.now().strftime("%d %b %Y, %I:%M %p"))
            )

    def latest(self, limit=100):
        with self._connect() as con:
            return con.execute(
                "SELECT expression, result, created_at FROM history ORDER BY id DESC LIMIT ?",
                (limit,)
            ).fetchall()

    def clear(self):
        with self._connect() as con:
            con.execute("DELETE FROM history")
