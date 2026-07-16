"""Dados padrão (seed) inseridos na primeira execução do PrintQuote by BMR:
biblioteca de materiais com preços médios de mercado BR, perfis de
impressoras comuns e canais de venda. Tudo editável depois pela interface.
"""
from __future__ import annotations

import sqlite3

from ..core.models import GlobalSettings, Material, MaterialType, PrinterProfile, SaleChannel
from . import repository as repo


def seed_if_empty(conn: sqlite3.Connection) -> None:
    if not repo.list_materials(conn):
        for material in _default_materials():
            repo.save_material(conn, material)

    if not repo.list_printers(conn):
        for printer in _default_printers():
            repo.save_printer(conn, printer)

    if not repo.list_sale_channels(conn):
        for channel in _default_sale_channels():
            repo.save_sale_channel(conn, channel)

    existing = conn.execute("SELECT COUNT(*) AS c FROM app_settings").fetchone()["c"]
    if existing == 0:
        repo.save_settings(conn, GlobalSettings())


def _default_materials() -> list:
    # Preços da 3D Lab (fornecedor do usuário), calculados a partir do preço
    # cheio (o site mostra "à vista no Pix com 10% off" — o usuário não paga
    # via Pix, então o preço padrão aqui é o valor SEM esse desconto).
    return [
        Material(id=None, name="PLA Premium (3D Lab)", material_type=MaterialType.FILAMENT,
                 price_per_kg=99.89, unit_label="kg", notes="Preço cheio (sem desconto Pix) — 3dlab.com.br"),
        Material(id=None, name="PLA Silk (3D Lab)", material_type=MaterialType.FILAMENT,
                 price_per_kg=128.90, unit_label="kg", notes="Preço cheio (sem desconto Pix) — 3dlab.com.br"),
        Material(id=None, name="PETG Premium (3D Lab)", material_type=MaterialType.FILAMENT,
                 price_per_kg=119.87, unit_label="kg", notes="Preço cheio (sem desconto Pix) — 3dlab.com.br"),
        Material(id=None, name="PETG Low Cost (3D Lab)", material_type=MaterialType.FILAMENT,
                 price_per_kg=72.73, unit_label="kg", notes="Preço cheio (sem desconto Pix) — 3dlab.com.br"),
        Material(id=None, name="ABS Premium (3D Lab)", material_type=MaterialType.FILAMENT,
                 price_per_kg=97.67, unit_label="kg", notes="Preço cheio (sem desconto Pix) — 3dlab.com.br"),
        Material(id=None, name="ABS Natural Engineering (3D Lab)", material_type=MaterialType.FILAMENT,
                 price_per_kg=88.76, unit_label="kg", notes="Preço cheio (sem desconto Pix) — 3dlab.com.br"),
        Material(id=None, name="ASA", material_type=MaterialType.FILAMENT, price_per_kg=130.0,
                 unit_label="kg", notes="Preço médio de mercado BR (estimativa)"),
        Material(id=None, name="TPU", material_type=MaterialType.FILAMENT, price_per_kg=150.0,
                 unit_label="kg", notes="Preço médio de mercado BR (estimativa)"),
        Material(id=None, name="Resina Padrão", material_type=MaterialType.RESIN, price_per_kg=200.0,
                 unit_label="L", notes="Preço por litro, densidade ~1g/mL (estimativa)"),
        Material(id=None, name="Resina Tough/ABS-like", material_type=MaterialType.RESIN,
                 price_per_kg=280.0, unit_label="L", notes="Preço por litro (estimativa)"),
    ]


def _default_printers() -> list:
    return [
        PrinterProfile(
            id=None, name="Ender 3 S1", purchase_price=2200.0, lifetime_hours=6000,
            watts_avg=120.0, maintenance_cost_per_hour=0.15,
            notes="FDM doméstica",
        ),
        PrinterProfile(
            id=None, name="Bambu Lab A1 + AMS Lite", purchase_price=4200.0, lifetime_hours=6000,
            watts_avg=100.0, maintenance_cost_per_hour=0.20,
            notes="FDM multi-cor",
        ),
        PrinterProfile(
            id=None, name="P1S (P1P modificada)", purchase_price=5500.0, lifetime_hours=8000,
            watts_avg=140.0, maintenance_cost_per_hour=0.30,
            notes="Uso profissional, câmara fechada",
        ),
    ]


def _default_sale_channels() -> list:
    return [
        SaleChannel(id=None, name="Venda direta (sem taxa)", fee_pct=0.0, fee_fixed=0.0),
        SaleChannel(id=None, name="Mercado Livre (Clássico)", fee_pct=0.12, fee_fixed=6.0),
        SaleChannel(id=None, name="Shopee", fee_pct=0.14, fee_fixed=4.0),
        SaleChannel(id=None, name="Etsy", fee_pct=0.065, fee_fixed=0.20),
        SaleChannel(id=None, name="Elo7", fee_pct=0.12, fee_fixed=1.0),
    ]
