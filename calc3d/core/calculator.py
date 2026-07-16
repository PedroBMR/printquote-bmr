"""Motor de cálculo de custos e precificação para impressão 3D.

Camada 100% Python puro, sem dependência de UI ou banco de dados.
Recebe um PieceInput + GlobalSettings e devolve um PricingResult completo
(breakdown de custos + cenários de preço). Esta é a camada que deve ser
importada diretamente dentro do NozzleNote quando a integração acontecer.
"""
from __future__ import annotations

from typing import Optional, Sequence

from .models import (
    CostBreakdown,
    GlobalSettings,
    PieceInput,
    PricingResult,
    PricingScenario,
)

DEFAULT_MARGIN_SCENARIOS: Sequence[float] = (0.30, 0.50, 1.00)


def compute_material_cost(piece: PieceInput) -> float:
    total = 0.0
    for usage in piece.materials:
        grams_com_perda = usage.grams * (1 + piece.waste_pct)
        total += grams_com_perda * usage.material.price_per_gram
    return total


def compute_energy_cost(piece: PieceInput, settings: GlobalSettings) -> float:
    tarifa = (
        piece.energy_tariff_kwh
        if piece.energy_tariff_kwh is not None
        else settings.energy_tariff_kwh
    )
    kwh = (piece.printer.watts_avg / 1000.0) * piece.print_time_hours
    return kwh * tarifa


def compute_depreciation_cost(piece: PieceInput) -> float:
    return piece.printer.depreciation_per_hour * piece.print_time_hours


def compute_maintenance_cost(piece: PieceInput) -> float:
    return piece.printer.maintenance_cost_per_hour * piece.print_time_hours


def compute_labor_cost(piece: PieceInput, settings: GlobalSettings) -> float:
    rate = (
        piece.labor_rate_hour
        if piece.labor_rate_hour is not None
        else settings.labor_rate_hour
    )
    return piece.labor.total_hours() * rate


def compute_shipping_absorbed(piece: PieceInput) -> float:
    modo = piece.shipping.mode
    if modo == "repassar":
        return 0.0
    if modo == "gratis_embutido":
        return piece.shipping.shipping_cost
    if modo == "subsidiar":
        return piece.shipping.shipping_cost * piece.shipping.subsidize_pct
    return 0.0


def compute_breakdown(piece: PieceInput, settings: GlobalSettings) -> CostBreakdown:
    material_cost = compute_material_cost(piece)
    energy_cost = compute_energy_cost(piece, settings)
    depreciation_cost = compute_depreciation_cost(piece)
    maintenance_cost = compute_maintenance_cost(piece)
    labor_cost = compute_labor_cost(piece, settings)

    base_cost = material_cost + energy_cost + depreciation_cost + maintenance_cost + labor_cost

    failure_rate = (
        piece.failure_rate_pct
        if piece.failure_rate_pct is not None
        else settings.failure_rate_pct
    )
    failure_rate = min(max(failure_rate, 0.0), 0.95)
    failure_adjusted_cost = base_cost / (1 - failure_rate) if failure_rate < 1 else base_cost

    overhead_cost = piece.overhead_per_piece
    packaging_cost = piece.packaging_cost
    shipping_absorbed = compute_shipping_absorbed(piece)

    total_cost = failure_adjusted_cost + overhead_cost + packaging_cost + shipping_absorbed

    return CostBreakdown(
        material_cost=material_cost,
        energy_cost=energy_cost,
        depreciation_cost=depreciation_cost,
        maintenance_cost=maintenance_cost,
        labor_cost=labor_cost,
        base_cost=base_cost,
        failure_adjusted_cost=failure_adjusted_cost,
        overhead_cost=overhead_cost,
        packaging_cost=packaging_cost,
        shipping_cost_absorbed=shipping_absorbed,
        total_cost=total_cost,
    )


def total_fee_pct(piece: PieceInput, settings: GlobalSettings) -> float:
    channel_pct = piece.sale_channel.fee_pct if piece.sale_channel else 0.0
    gateway_pct = (
        piece.payment_gateway_pct
        if piece.payment_gateway_pct is not None
        else settings.payment_gateway_pct
    )
    tax_pct = piece.tax_pct if piece.tax_pct is not None else settings.tax_pct
    return channel_pct + gateway_pct + tax_pct


def channel_fixed_fee(piece: PieceInput) -> float:
    return piece.sale_channel.fee_fixed if piece.sale_channel else 0.0


def price_cost_plus(total_cost: float, markup_multiplier: float) -> float:
    """Preço = custo total x multiplicador (ex: markup de 1.5x)."""
    return total_cost * markup_multiplier


def price_margin_on_price(
    total_cost: float, margin_pct: float, fee_pct: float, fee_fixed: float
) -> float:
    """Resolve o preço de venda P tal que:
    P - (P*fee_pct + fee_fixed) - total_cost = P*margin_pct
    """
    denom = 1 - margin_pct - fee_pct
    if denom <= 0:
        return float("inf")
    return (total_cost + fee_fixed) / denom


def analyze_price(price: float, total_cost: float, fee_pct: float, fee_fixed: float) -> dict:
    """Dado um preço de venda, calcula taxas, lucro líquido e margem real."""
    fees = price * fee_pct + fee_fixed
    net_profit = price - fees - total_cost
    net_margin_pct = net_profit / price if price else 0.0
    return {
        "price": price,
        "fees": fees,
        "net_profit": net_profit,
        "net_margin_pct": net_margin_pct,
    }


def build_scenarios(
    total_cost: float,
    piece: PieceInput,
    settings: GlobalSettings,
    margins: Sequence[float] = DEFAULT_MARGIN_SCENARIOS,
) -> list:
    fee_pct = total_fee_pct(piece, settings)
    fee_fixed = channel_fixed_fee(piece)
    scenarios = []
    for m in margins:
        cp_price = price_cost_plus(total_cost, 1 + m)
        cp_analysis = analyze_price(cp_price, total_cost, fee_pct, fee_fixed)
        mp_price = price_margin_on_price(total_cost, m, fee_pct, fee_fixed)
        mp_analysis = analyze_price(mp_price, total_cost, fee_pct, fee_fixed)
        scenarios.append(
            PricingScenario(
                label=f"{int(round(m * 100))}%",
                margin_pct=m,
                price_cost_plus=cp_price,
                price_margin_on_price=mp_price,
                net_profit_cost_plus=cp_analysis["net_profit"],
                net_profit_margin_on_price=mp_analysis["net_profit"],
            )
        )
    return scenarios


def compute_pricing(
    piece: PieceInput,
    settings: GlobalSettings,
    margins: Sequence[float] = DEFAULT_MARGIN_SCENARIOS,
    competitor_price: Optional[float] = None,
) -> PricingResult:
    breakdown = compute_breakdown(piece, settings)
    scenarios = build_scenarios(breakdown.total_cost, piece, settings, margins)

    competitor_analysis = None
    if competitor_price:
        fee_pct = total_fee_pct(piece, settings)
        fee_fixed = channel_fixed_fee(piece)
        competitor_analysis = analyze_price(
            competitor_price, breakdown.total_cost, fee_pct, fee_fixed
        )

    return PricingResult(
        breakdown=breakdown,
        scenarios=scenarios,
        competitor_price=competitor_price,
        competitor_analysis=competitor_analysis,
    )
