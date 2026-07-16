"""Modelos de dados do motor de cálculo (core).

Este módulo não depende de UI nem de banco de dados — apenas dataclasses
puras usadas pelo motor de cálculo em calculator.py. Isso permite que a
camada de dados (SQLite) e a camada de interface (PySide6) sejam trocadas
livremente sem alterar a lógica de precificação.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class MaterialType(str, Enum):
    FILAMENT = "filamento"
    RESIN = "resina"


@dataclass
class Material:
    id: Optional[int]
    name: str
    material_type: "MaterialType"
    price_per_kg: float  # para resina, representa preço por litro
    unit_label: str = "kg"  # "kg" ou "L"
    notes: str = ""

    @property
    def price_per_gram(self) -> float:
        return self.price_per_kg / 1000.0


@dataclass
class PrinterProfile:
    id: Optional[int]
    name: str
    purchase_price: float
    lifetime_hours: float
    watts_avg: float
    maintenance_cost_per_hour: float = 0.0
    notes: str = ""

    @property
    def depreciation_per_hour(self) -> float:
        if self.lifetime_hours <= 0:
            return 0.0
        return self.purchase_price / self.lifetime_hours


@dataclass
class MaterialUsage:
    material: Material
    grams: float


@dataclass
class LaborStages:
    modeling_hours: float = 0.0
    slicing_hours: float = 0.0
    post_processing_hours: float = 0.0
    packaging_hours: float = 0.0

    def total_hours(self) -> float:
        return (
            self.modeling_hours
            + self.slicing_hours
            + self.post_processing_hours
            + self.packaging_hours
        )


@dataclass
class SaleChannel:
    id: Optional[int]
    name: str
    fee_pct: float = 0.0
    fee_fixed: float = 0.0


@dataclass
class GlobalSettings:
    energy_tariff_kwh: float = 0.76  # Copel B1 residencial, Pato Branco/PR (c/ impostos, reajuste 06/2026)
    labor_rate_hour: float = 25.0
    failure_rate_pct: float = 0.10
    tax_pct: float = 0.06
    payment_gateway_pct: float = 0.0
    monthly_fixed_costs: float = 0.0
    expected_monthly_volume: int = 1
    packaging_cost_default: float = 0.0


@dataclass
class ShippingConfig:
    mode: str = "repassar"  # "repassar" | "subsidiar" | "gratis_embutido"
    shipping_cost: float = 0.0
    subsidize_pct: float = 0.0


@dataclass
class PieceInput:
    name: str
    printer: PrinterProfile
    print_time_hours: float
    materials: list  # list[MaterialUsage]
    waste_pct: float = 0.05
    labor: LaborStages = field(default_factory=LaborStages)
    labor_rate_hour: Optional[float] = None
    failure_rate_pct: Optional[float] = None
    packaging_cost: float = 0.0
    shipping: ShippingConfig = field(default_factory=ShippingConfig)
    sale_channel: Optional[SaleChannel] = None
    tax_pct: Optional[float] = None
    payment_gateway_pct: Optional[float] = None
    overhead_per_piece: float = 0.0
    energy_tariff_kwh: Optional[float] = None

    def total_weight_g(self) -> float:
        return sum(u.grams for u in self.materials)


@dataclass
class CostBreakdown:
    material_cost: float
    energy_cost: float
    depreciation_cost: float
    maintenance_cost: float
    labor_cost: float
    base_cost: float
    failure_adjusted_cost: float
    overhead_cost: float
    packaging_cost: float
    shipping_cost_absorbed: float
    total_cost: float

    def as_dict(self) -> dict:
        return {
            "material_cost": self.material_cost,
            "energy_cost": self.energy_cost,
            "depreciation_cost": self.depreciation_cost,
            "maintenance_cost": self.maintenance_cost,
            "labor_cost": self.labor_cost,
            "base_cost": self.base_cost,
            "failure_adjusted_cost": self.failure_adjusted_cost,
            "overhead_cost": self.overhead_cost,
            "packaging_cost": self.packaging_cost,
            "shipping_cost_absorbed": self.shipping_cost_absorbed,
            "total_cost": self.total_cost,
        }

    def chart_items(self) -> list:
        """Itens para gráfico de pizza/barras (categoria, valor), somando
        depreciação+manutenção em 'Máquina' e omitindo zeros."""
        items = [
            ("Material", self.material_cost),
            ("Energia", self.energy_cost),
            ("Máquina (depreciação+manutenção)", self.depreciation_cost + self.maintenance_cost),
            ("Mão de obra", self.labor_cost),
            ("Overhead", self.overhead_cost),
            ("Embalagem", self.packaging_cost),
            ("Frete absorvido", self.shipping_cost_absorbed),
        ]
        return [(label, value) for label, value in items if value > 0.0001]


@dataclass
class PricingScenario:
    label: str
    margin_pct: float
    price_cost_plus: float
    price_margin_on_price: float
    net_profit_cost_plus: float
    net_profit_margin_on_price: float


@dataclass
class PricingResult:
    breakdown: CostBreakdown
    scenarios: list  # list[PricingScenario]
    competitor_price: Optional[float] = None
    competitor_analysis: Optional[dict] = None
