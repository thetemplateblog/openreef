"""SQLite persistence. One file, WAL mode, plain sqlite3 (no ORM) so it runs on a
Pi Zero without extra dependencies."""
from __future__ import annotations

import json
import sqlite3
import time
from contextlib import contextmanager
from typing import Any, Dict, Iterable, List, Optional

SCHEMA = """
CREATE TABLE IF NOT EXISTS results (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts REAL NOT NULL,
  test TEXT NOT NULL,              -- alkalinity | phosphate | nitrate
  value REAL,                      -- dKH or ppm
  unit TEXT,
  quality REAL,
  flags TEXT,                      -- JSON list
  raw TEXT,                        -- JSON: titration points / channel counts
  temp_c REAL,
  duration_s REAL,
  run_id INTEGER,
  calibration_id INTEGER
);
CREATE INDEX IF NOT EXISTS results_test_ts ON results(test, ts);

CREATE TABLE IF NOT EXISTS runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts_start REAL NOT NULL,
  ts_end REAL,
  test TEXT NOT NULL,
  status TEXT NOT NULL,            -- running | done | failed | aborted
  error TEXT,
  trigger TEXT                     -- schedule | api | calibration
);

CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts REAL NOT NULL,
  type TEXT NOT NULL,
  payload TEXT
);
CREATE INDEX IF NOT EXISTS events_ts ON events(ts);

CREATE TABLE IF NOT EXISTS calibrations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts REAL NOT NULL,
  test TEXT NOT NULL,
  kind TEXT NOT NULL,              -- acid_normality | curve | ph_electrode
  data TEXT NOT NULL,              -- JSON
  active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS reagents (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  bottle_ml REAL NOT NULL,
  remaining_ml REAL NOT NULL,
  pump TEXT NOT NULL,
  updated_ts REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
"""


class Database:
    def __init__(self, path: str):
        self.path = path
        self._conn = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=NORMAL")
        self._conn.executescript(SCHEMA)

    def close(self) -> None:
        self._conn.close()

    @contextmanager
    def tx(self):
        cur = self._conn.cursor()
        cur.execute("BEGIN")
        try:
            yield cur
            cur.execute("COMMIT")
        except Exception:
            cur.execute("ROLLBACK")
            raise

    # ------------------------------------------------------------------ runs
    def start_run(self, test: str, trigger: str) -> int:
        cur = self._conn.execute("INSERT INTO runs(ts_start,test,status,trigger) VALUES(?,?,?,?)",
                                 (time.time(), test, "running", trigger))
        return int(cur.lastrowid)

    def end_run(self, run_id: int, status: str, error: Optional[str] = None) -> None:
        self._conn.execute("UPDATE runs SET ts_end=?, status=?, error=? WHERE id=?",
                           (time.time(), status, error, run_id))

    def runs(self, limit: int = 50) -> List[Dict[str, Any]]:
        rows = self._conn.execute("SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------ results
    def add_result(self, test: str, value: float, unit: str, quality: float, flags: Iterable[str],
                   raw: Dict[str, Any], temp_c: float, duration_s: float, run_id: Optional[int],
                   calibration_id: Optional[int]) -> int:
        cur = self._conn.execute(
            "INSERT INTO results(ts,test,value,unit,quality,flags,raw,temp_c,duration_s,run_id,calibration_id)"
            " VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (time.time(), test, value, unit, quality, json.dumps(list(flags)), json.dumps(raw),
             temp_c, duration_s, run_id, calibration_id))
        return int(cur.lastrowid)

    def results(self, test: Optional[str] = None, since: Optional[float] = None,
                until: Optional[float] = None, limit: int = 200, include_raw: bool = False) -> List[Dict[str, Any]]:
        q = "SELECT * FROM results WHERE 1=1"
        args: List[Any] = []
        if test:
            q += " AND test=?"; args.append(test)
        if since:
            q += " AND ts>=?"; args.append(since)
        if until:
            q += " AND ts<=?"; args.append(until)
        q += " ORDER BY ts DESC LIMIT ?"; args.append(limit)
        rows = self._conn.execute(q, args).fetchall()
        return [self._result_row(r, include_raw) for r in rows]

    def result(self, rid: int) -> Optional[Dict[str, Any]]:
        r = self._conn.execute("SELECT * FROM results WHERE id=?", (rid,)).fetchone()
        return self._result_row(r, True) if r else None

    def latest(self) -> Dict[str, Dict[str, Any]]:
        out = {}
        for test in ("alkalinity", "phosphate", "nitrate"):
            r = self._conn.execute("SELECT * FROM results WHERE test=? ORDER BY ts DESC LIMIT 1",
                                   (test,)).fetchone()
            if r:
                out[test] = self._result_row(r, False)
        return out

    @staticmethod
    def _result_row(r: sqlite3.Row, include_raw: bool) -> Dict[str, Any]:
        d = dict(r)
        d["flags"] = json.loads(d.get("flags") or "[]")
        if include_raw:
            d["raw"] = json.loads(d.get("raw") or "{}")
        else:
            d.pop("raw", None)
        return d

    # ------------------------------------------------------------------ events
    def add_event(self, type_: str, payload: Dict[str, Any]) -> None:
        self._conn.execute("INSERT INTO events(ts,type,payload) VALUES(?,?,?)",
                           (payload.get("ts", time.time()), type_, json.dumps(payload, default=str)))

    def events(self, limit: int = 100, type_: Optional[str] = None) -> List[Dict[str, Any]]:
        if type_:
            rows = self._conn.execute("SELECT * FROM events WHERE type=? ORDER BY id DESC LIMIT ?",
                                      (type_, limit)).fetchall()
        else:
            rows = self._conn.execute("SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [{**dict(r), "payload": json.loads(r["payload"] or "{}")} for r in rows]

    # ------------------------------------------------------------------ calibrations
    def add_calibration(self, test: str, kind: str, data: Dict[str, Any]) -> int:
        with self.tx() as cur:
            cur.execute("UPDATE calibrations SET active=0 WHERE test=? AND kind=?", (test, kind))
            cur.execute("INSERT INTO calibrations(ts,test,kind,data,active) VALUES(?,?,?,?,1)",
                        (time.time(), test, kind, json.dumps(data)))
            return int(cur.lastrowid)

    def active_calibration(self, test: str, kind: str) -> Optional[Dict[str, Any]]:
        r = self._conn.execute("SELECT * FROM calibrations WHERE test=? AND kind=? AND active=1 "
                               "ORDER BY id DESC LIMIT 1", (test, kind)).fetchone()
        return {**dict(r), "data": json.loads(r["data"])} if r else None

    def calibrations(self, test: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        if test:
            rows = self._conn.execute("SELECT * FROM calibrations WHERE test=? ORDER BY id DESC LIMIT ?",
                                      (test, limit)).fetchall()
        else:
            rows = self._conn.execute("SELECT * FROM calibrations ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [{**dict(r), "data": json.loads(r["data"])} for r in rows]

    # ------------------------------------------------------------------ reagents
    def upsert_reagent(self, rid: str, name: str, bottle_ml: float, remaining_ml: float, pump: str) -> None:
        self._conn.execute(
            "INSERT INTO reagents(id,name,bottle_ml,remaining_ml,pump,updated_ts) VALUES(?,?,?,?,?,?)"
            " ON CONFLICT(id) DO UPDATE SET name=excluded.name, bottle_ml=excluded.bottle_ml, pump=excluded.pump",
            (rid, name, bottle_ml, remaining_ml, pump, time.time()))

    def reagents(self) -> List[Dict[str, Any]]:
        return [dict(r) for r in self._conn.execute("SELECT * FROM reagents ORDER BY id").fetchall()]

    def reagent(self, rid: str) -> Optional[Dict[str, Any]]:
        r = self._conn.execute("SELECT * FROM reagents WHERE id=?", (rid,)).fetchone()
        return dict(r) if r else None

    def consume_reagent(self, rid: str, ml: float) -> float:
        self._conn.execute("UPDATE reagents SET remaining_ml=MAX(0, remaining_ml-?), updated_ts=? WHERE id=?",
                           (ml, time.time(), rid))
        r = self.reagent(rid)
        return r["remaining_ml"] if r else 0.0

    def refill_reagent(self, rid: str, remaining_ml: Optional[float] = None) -> Dict[str, Any]:
        r = self.reagent(rid)
        if not r:
            raise KeyError(rid)
        new = remaining_ml if remaining_ml is not None else r["bottle_ml"]
        self._conn.execute("UPDATE reagents SET remaining_ml=?, updated_ts=? WHERE id=?", (new, time.time(), rid))
        return self.reagent(rid)  # type: ignore[return-value]

    # ------------------------------------------------------------------ settings
    def get_setting(self, key: str, default: Any = None) -> Any:
        r = self._conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return json.loads(r["value"]) if r else default

    def set_setting(self, key: str, value: Any) -> None:
        self._conn.execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                           (key, json.dumps(value)))

    # ------------------------------------------------------------------ export
    def export_csv(self, test: Optional[str] = None) -> str:
        rows = self.results(test=test, limit=100000)
        lines = ["id,ts_iso,test,value,unit,quality,temp_c,flags"]
        for r in reversed(rows):
            iso = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(r["ts"]))
            lines.append(f'{r["id"]},{iso},{r["test"]},{r["value"]},{r["unit"]},{r["quality"]},'
                         f'{r["temp_c"]},"{";".join(r["flags"])}"')
        return "\n".join(lines) + "\n"
