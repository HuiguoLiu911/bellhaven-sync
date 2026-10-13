"""SQLite-backed proposal queue.

Idempotency rules (what makes daily re-runs safe):
  * A proposal is identified by `key` (what it is about) + `fingerprint` (the exact change).
  * If a row with the same key+fingerprint was already approved/applied or rejected, the
    pipeline does NOT re-propose it.
  * If the same key comes back with a *different* fingerprint (the facts changed), it is
    proposed again as a new row and any older pending row for that key is superseded.
  * Pending rows that a new run no longer generates (someone fixed the CRM by hand, the
    site changed back) are marked superseded so reviewers never act on stale advice.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  started_at TEXT, finished_at TEXT, status TEXT, stats TEXT
);
CREATE TABLE IF NOT EXISTS proposals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  key TEXT NOT NULL, fingerprint TEXT NOT NULL,
  kind TEXT NOT NULL, title TEXT, slug TEXT, account_id TEXT,
  actions TEXT, evidence TEXT,
  status TEXT NOT NULL,            -- pending | applying | applied | rejected | failed | superseded | info
  first_run INTEGER, last_run INTEGER,
  decided_at TEXT, reviewer_note TEXT, result TEXT
);
CREATE INDEX IF NOT EXISTS ix_prop_key ON proposals(key, fingerprint);
CREATE INDEX IF NOT EXISTS ix_prop_status ON proposals(status);
"""
DECIDED = ("applied", "rejected", "applying")  # applying = a reviewer is writing it right now


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def connect(path: Path = DB_PATH) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=30)
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    return db


def start_run(db) -> int:
    cur = db.execute("INSERT INTO runs(started_at, status) VALUES (?, 'running')", (now(),))
    db.commit()
    return cur.lastrowid


def finish_run(db, run_id: int, status: str, stats: dict):
    db.execute("UPDATE runs SET finished_at=?, status=?, stats=? WHERE id=?",
               (now(), status, json.dumps(stats), run_id))
    db.commit()


def last_good_run(db):
    return db.execute("SELECT * FROM runs WHERE status='ok' ORDER BY id DESC LIMIT 1").fetchone()


def upsert_proposals(db, run_id: int, proposals: list[dict]) -> dict:
    stats = {"new": 0, "refreshed": 0, "already_decided": 0, "superseded": 0, "confirmed": 0}
    seen_ids: set[int] = set()
    with db:  # one transaction
        for p in proposals:
            if p["kind"] == "confirmed":
                # informational: one row per key, always refreshed
                row = db.execute("SELECT id FROM proposals WHERE key=? AND status='info'", (p["key"],)).fetchone()
                if row:
                    db.execute("UPDATE proposals SET evidence=?, title=?, last_run=? WHERE id=?",
                               (json.dumps(p["evidence"]), p["title"], run_id, row["id"]))
                    seen_ids.add(row["id"])
                else:
                    cur = db.execute(
                        "INSERT INTO proposals(key,fingerprint,kind,title,slug,account_id,actions,evidence,status,first_run,last_run)"
                        " VALUES (?,?,?,?,?,?,?,?, 'info', ?, ?)",
                        (p["key"], p["fingerprint"], p["kind"], p["title"], p["slug"], p["account_id"],
                         "[]", json.dumps(p["evidence"]), run_id, run_id))
                    seen_ids.add(cur.lastrowid)
                stats["confirmed"] += 1
                continue

            decided = db.execute("SELECT id FROM proposals WHERE key=? AND fingerprint=? AND status IN (?,?,?)",
                                 (p["key"], p["fingerprint"], *DECIDED)).fetchone()
            if decided:
                stats["already_decided"] += 1
                continue
            open_row = db.execute("SELECT id FROM proposals WHERE key=? AND fingerprint=? AND status IN ('pending','failed')",
                                  (p["key"], p["fingerprint"])).fetchone()
            if open_row:
                db.execute("UPDATE proposals SET actions=?, evidence=?, title=?, last_run=? WHERE id=?",
                           (json.dumps(p["actions"]), json.dumps(p["evidence"]), p["title"], run_id, open_row["id"]))
                seen_ids.add(open_row["id"])
                stats["refreshed"] += 1
                continue
            cur = db.execute(
                "INSERT INTO proposals(key,fingerprint,kind,title,slug,account_id,actions,evidence,status,first_run,last_run)"
                " VALUES (?,?,?,?,?,?,?,?, 'pending', ?, ?)",
                (p["key"], p["fingerprint"], p["kind"], p["title"], p["slug"], p["account_id"],
                 json.dumps(p["actions"]), json.dumps(p["evidence"]), run_id, run_id))
            seen_ids.add(cur.lastrowid)
            stats["new"] += 1

        # anything still open that this run didn't produce is no longer valid advice -- except a
        # failed proposal that already completed some writes: it must stay retryable/visible.
        for row in db.execute("SELECT id, result FROM proposals WHERE status IN ('pending','failed','info')").fetchall():
            if row["id"] not in seen_ids and not _has_progress(row["result"]):
                db.execute("UPDATE proposals SET status='superseded', decided_at=?, reviewer_note=? WHERE id=?",
                           (now(), f"Not regenerated by run {run_id}", row["id"]))
                stats["superseded"] += 1
    return stats


def _has_progress(result_json) -> bool:
    try:
        return bool(json.loads(result_json or "{}").get("done"))
    except ValueError:
        return False


def claim(db, pid: int) -> bool:
    """Atomically move a proposal to 'applying'. Only one concurrent caller can win."""
    cur = db.execute("UPDATE proposals SET status='applying' WHERE id=? AND status IN ('pending','failed')", (pid,))
    db.commit()
    return cur.rowcount == 1


def reject(db, pid: int, note: str = "") -> bool:
    """Reject a pending/failed proposal. Keeps any partial-progress record (e.g. a created account id)."""
    cur = db.execute("UPDATE proposals SET status='rejected', decided_at=?, reviewer_note=COALESCE(NULLIF(?,''), reviewer_note)"
                     " WHERE id=? AND status IN ('pending','failed')", (now(), note, pid))
    db.commit()
    return cur.rowcount == 1


def get(db, pid: int):
    return db.execute("SELECT * FROM proposals WHERE id=?", (pid,)).fetchone()


def listing(db, status: str | None):
    if status == "all":
        return db.execute("SELECT * FROM proposals WHERE status!='info' ORDER BY id").fetchall()
    return db.execute("SELECT * FROM proposals WHERE status=? ORDER BY kind, title", (status,)).fetchall()


def counts(db) -> dict:
    return {r["status"]: r["n"] for r in db.execute("SELECT status, COUNT(*) n FROM proposals GROUP BY status")}


def set_status(db, pid: int, status: str, note: str = "", result=None):
    db.execute("UPDATE proposals SET status=?, decided_at=?, reviewer_note=COALESCE(NULLIF(?,''), reviewer_note), result=? WHERE id=?",
               (status, now(), note, json.dumps(result) if result is not None else None, pid))
    db.commit()


def save_result(db, pid: int, result):
    db.execute("UPDATE proposals SET result=? WHERE id=?", (json.dumps(result), pid))
    db.commit()
