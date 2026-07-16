"""Camada de dados: conexão e schema SQLite.

Usa o mesmo formato de banco (SQLite) planejado para o NozzleNote, para
facilitar migração/compartilhamento de dados entre os dois apps no futuro.
"""
from __future__ import annotations

import os
import shutil
import sqlite3
from pathlib import Path

_LOCAL_APPDATA = Path(os.environ.get("LOCALAPPDATA", Path.home()))
DEFAULT_DB_PATH = _LOCAL_APPDATA / "BMR" / "PrintQuote by BMR" / "printquote.db"
_LEGACY_DB_PATH = Path.home() / ".bmr3d" / "calc3d.db"


def _migrate_legacy_db(db_path: Path) -> None:
    """Versões anteriores (antes do rebranding) gravavam em ~/.bmr3d/calc3d.db.
    Copia os dados existentes uma única vez para o novo local padrão."""
    if db_path == _LEGACY_DB_PATH:
        return
    if db_path.exists() or not _LEGACY_DB_PATH.exists():
        return
    db_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(_LEGACY_DB_PATH, db_path)

SCHEMA = """
CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    material_type TEXT NOT NULL,
    price_per_kg REAL NOT NULL,
    unit_label TEXT NOT NULL DEFAULT 'kg',
    notes TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS printers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    purchase_price REAL NOT NULL,
    lifetime_hours REAL NOT NULL,
    watts_avg REAL NOT NULL,
    maintenance_cost_per_hour REAL NOT NULL DEFAULT 0,
    notes TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS sale_channels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    fee_pct REAL NOT NULL DEFAULT 0,
    fee_fixed REAL NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS parts_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    printer_id INTEGER REFERENCES printers(id) ON DELETE SET NULL,
    print_time_hours REAL NOT NULL,
    weight_g REAL NOT NULL,
    materials_json TEXT NOT NULL,
    labor_json TEXT NOT NULL,
    breakdown_json TEXT NOT NULL,
    final_price REAL,
    notes TEXT DEFAULT ''
);
"""


def get_connection(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    _migrate_legacy_db(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()
