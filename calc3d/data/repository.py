"""Camada de dados: CRUD sobre SQLite para materiais, impressoras, canais de
venda, configurações globais e histórico de peças.

Converte linhas do SQLite em/para as dataclasses definidas em core.models,
mantendo a camada core (calculator.py) totalmente alheia à existência do
banco de dados.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import List, Optional

from ..core.models import GlobalSettings, Material, MaterialType, PrinterProfile, SaleChannel

# ---------------------------------------------------------------------------
# Materiais
# ---------------------------------------------------------------------------

def list_materials(conn: sqlite3.Connection) -> List[Material]:
    rows = conn.execute("SELECT * FROM materials ORDER BY name").fetchall()
    return [_row_to_material(r) for r in rows]


def get_material(conn: sqlite3.Connection, material_id: int) -> Optional[Material]:
    row = conn.execute("SELECT * FROM materials WHERE id = ?", (material_id,)).fetchone()
    return _row_to_material(row) if row else None


def save_material(conn: sqlite3.Connection, material: Material) -> Material:
    # MaterialType herda de str; widgets Qt (QComboBox.currentData()) às vezes
    # devolvem o valor já "achatado" para str puro em vez do membro do enum.
    # MaterialType(...) aceita os dois casos e normaliza.
    material_type_value = MaterialType(material.material_type).value
    if material.id is None:
        cur = conn.execute(
            "INSERT INTO materials (name, material_type, price_per_kg, unit_label, notes) "
            "VALUES (?,?,?,?,?)",
            (
                material.name,
                material_type_value,
                material.price_per_kg,
                material.unit_label,
                material.notes,
            ),
        )
        material.id = cur.lastrowid
    else:
        conn.execute(
            "UPDATE materials SET name=?, material_type=?, price_per_kg=?, unit_label=?, notes=? "
            "WHERE id=?",
            (
                material.name,
                material_type_value,
                material.price_per_kg,
                material.unit_label,
                material.notes,
                material.id,
            ),
        )
    conn.commit()
    return material


def delete_material(conn: sqlite3.Connection, material_id: int) -> None:
    conn.execute("DELETE FROM materials WHERE id=?", (material_id,))
    conn.commit()


def _row_to_material(row: sqlite3.Row) -> Material:
    return Material(
        id=row["id"],
        name=row["name"],
        material_type=MaterialType(row["material_type"]),
        price_per_kg=row["price_per_kg"],
        unit_label=row["unit_label"],
        notes=row["notes"] or "",
    )


# ---------------------------------------------------------------------------
# Impressoras
# ---------------------------------------------------------------------------

def list_printers(conn: sqlite3.Connection) -> List[PrinterProfile]:
    rows = conn.execute("SELECT * FROM printers ORDER BY name").fetchall()
    return [_row_to_printer(r) for r in rows]


def get_printer(conn: sqlite3.Connection, printer_id: int) -> Optional[PrinterProfile]:
    row = conn.execute("SELECT * FROM printers WHERE id=?", (printer_id,)).fetchone()
    return _row_to_printer(row) if row else None


def save_printer(conn: sqlite3.Connection, printer: PrinterProfile) -> PrinterProfile:
    if printer.id is None:
        cur = conn.execute(
            "INSERT INTO printers (name, purchase_price, lifetime_hours, watts_avg, "
            "maintenance_cost_per_hour, notes) VALUES (?,?,?,?,?,?)",
            (
                printer.name,
                printer.purchase_price,
                printer.lifetime_hours,
                printer.watts_avg,
                printer.maintenance_cost_per_hour,
                printer.notes,
            ),
        )
        printer.id = cur.lastrowid
    else:
        conn.execute(
            "UPDATE printers SET name=?, purchase_price=?, lifetime_hours=?, watts_avg=?, "
            "maintenance_cost_per_hour=?, notes=? WHERE id=?",
            (
                printer.name,
                printer.purchase_price,
                printer.lifetime_hours,
                printer.watts_avg,
                printer.maintenance_cost_per_hour,
                printer.notes,
                printer.id,
            ),
        )
    conn.commit()
    return printer


def delete_printer(conn: sqlite3.Connection, printer_id: int) -> None:
    conn.execute("DELETE FROM printers WHERE id=?", (printer_id,))
    conn.commit()


def _row_to_printer(row: sqlite3.Row) -> PrinterProfile:
    return PrinterProfile(
        id=row["id"],
        name=row["name"],
        purchase_price=row["purchase_price"],
        lifetime_hours=row["lifetime_hours"],
        watts_avg=row["watts_avg"],
        maintenance_cost_per_hour=row["maintenance_cost_per_hour"],
        notes=row["notes"] or "",
    )


# ---------------------------------------------------------------------------
# Canais de venda
# ---------------------------------------------------------------------------

def list_sale_channels(conn: sqlite3.Connection) -> List[SaleChannel]:
    rows = conn.execute("SELECT * FROM sale_channels ORDER BY name").fetchall()
    return [
        SaleChannel(id=r["id"], name=r["name"], fee_pct=r["fee_pct"], fee_fixed=r["fee_fixed"])
        for r in rows
    ]


def save_sale_channel(conn: sqlite3.Connection, channel: SaleChannel) -> SaleChannel:
    if channel.id is None:
        cur = conn.execute(
            "INSERT INTO sale_channels (name, fee_pct, fee_fixed) VALUES (?,?,?)",
            (channel.name, channel.fee_pct, channel.fee_fixed),
        )
        channel.id = cur.lastrowid
    else:
        conn.execute(
            "UPDATE sale_channels SET name=?, fee_pct=?, fee_fixed=? WHERE id=?",
            (channel.name, channel.fee_pct, channel.fee_fixed, channel.id),
        )
    conn.commit()
    return channel


def delete_sale_channel(conn: sqlite3.Connection, channel_id: int) -> None:
    conn.execute("DELETE FROM sale_channels WHERE id=?", (channel_id,))
    conn.commit()


# ---------------------------------------------------------------------------
# Configurações globais
# ---------------------------------------------------------------------------

SETTINGS_FIELDS = [
    "energy_tariff_kwh",
    "labor_rate_hour",
    "failure_rate_pct",
    "tax_pct",
    "payment_gateway_pct",
    "monthly_fixed_costs",
    "expected_monthly_volume",
    "packaging_cost_default",
]


def load_settings(conn: sqlite3.Connection) -> GlobalSettings:
    rows = conn.execute("SELECT key, value FROM app_settings").fetchall()
    values = {r["key"]: r["value"] for r in rows}
    defaults = GlobalSettings()
    merged = dict(defaults.__dict__)
    for field_name in SETTINGS_FIELDS:
        if field_name in values:
            cast = type(getattr(defaults, field_name))
            merged[field_name] = cast(values[field_name])
    return GlobalSettings(**merged)


def save_settings(conn: sqlite3.Connection, settings: GlobalSettings) -> None:
    for field_name in SETTINGS_FIELDS:
        value = getattr(settings, field_name)
        conn.execute(
            "INSERT INTO app_settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (field_name, str(value)),
        )
    conn.commit()


# ---------------------------------------------------------------------------
# Histórico de peças (biblioteca de peças salvas)
# ---------------------------------------------------------------------------

def save_part_history(
    conn: sqlite3.Connection,
    name: str,
    printer_id: Optional[int],
    print_time_hours: float,
    weight_g: float,
    materials_payload: list,
    labor_payload: dict,
    breakdown_payload: dict,
    final_price: Optional[float],
    notes: str = "",
) -> int:
    cur = conn.execute(
        "INSERT INTO parts_history (name, created_at, printer_id, print_time_hours, weight_g, "
        "materials_json, labor_json, breakdown_json, final_price, notes) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)",
        (
            name,
            datetime.now().isoformat(timespec="seconds"),
            printer_id,
            print_time_hours,
            weight_g,
            json.dumps(materials_payload, ensure_ascii=False),
            json.dumps(labor_payload, ensure_ascii=False),
            json.dumps(breakdown_payload, ensure_ascii=False),
            final_price,
            notes,
        ),
    )
    conn.commit()
    return cur.lastrowid


def list_parts_history(conn: sqlite3.Connection) -> List[sqlite3.Row]:
    return conn.execute("SELECT * FROM parts_history ORDER BY created_at DESC").fetchall()


def get_part_history(conn: sqlite3.Connection, part_id: int) -> Optional[sqlite3.Row]:
    return conn.execute("SELECT * FROM parts_history WHERE id=?", (part_id,)).fetchone()


def delete_part_history(conn: sqlite3.Connection, part_id: int) -> None:
    conn.execute("DELETE FROM parts_history WHERE id=?", (part_id,))
    conn.commit()
