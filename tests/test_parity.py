"""Testes de paridade entre os dois motores de cálculo do PrintQuote.

Garante que o motor da versão web (docs/js/core.js, rodado via Node) e o
motor da versão desktop (calc3d.core, Python) produzem exatamente os mesmos
números para os mesmos casos de entrada (tests/cases.json).

Se alguém mudar uma fórmula em um lado e esquecer o outro, este teste falha.
Também há um teste "golden" com valores conhecidos, que pega um erro
conceitual capaz de afetar os dois motores ao mesmo tempo.

Rodar:  pytest tests/ -v
Requer: Node no PATH (para executar o motor JS).
"""
from __future__ import annotations

import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from calc3d.core.calculator import compute_pricing  # noqa: E402
from calc3d.core.models import (  # noqa: E402
    GlobalSettings,
    LaborStages,
    Material,
    MaterialType,
    MaterialUsage,
    PieceInput,
    PrinterProfile,
    SaleChannel,
    ShippingConfig,
)

CASES = json.loads((ROOT / "tests" / "cases.json").read_text(encoding="utf-8"))
ABS_TOL = 1e-9


def _n(x):
    """Não-finitos (inf/nan) viram 'inf' pra bater com o lado JS."""
    if isinstance(x, (int, float)) and math.isfinite(x):
        return float(x)
    return "inf"


def _build(case) -> tuple[PieceInput, GlobalSettings]:
    s = case["settings"]
    settings = GlobalSettings(
        energy_tariff_kwh=s["energyTariffKwh"],
        labor_rate_hour=s["laborRateHour"],
        failure_rate_pct=s["failureRatePct"],
        tax_pct=s["taxPct"],
        payment_gateway_pct=s["paymentGatewayPct"],
    )
    p = case["printer"]
    printer = PrinterProfile(
        id=None,
        name="printer",
        purchase_price=p["purchasePrice"],
        lifetime_hours=p["lifetimeHours"],
        watts_avg=p["wattsAvg"],
        maintenance_cost_per_hour=p["maintenanceCostPerHour"],
    )
    materials = [
        MaterialUsage(
            Material(
                id=None,
                name="mat",
                material_type=MaterialType.FILAMENT,
                price_per_kg=m["pricePerKg"],
            ),
            m["grams"],
        )
        for m in case["materials"]
    ]
    lb = case["labor"]
    labor = LaborStages(
        modeling_hours=lb["modelingHours"],
        slicing_hours=lb["slicingHours"],
        post_processing_hours=lb["postProcessingHours"],
        packaging_hours=lb["packagingHours"],
    )
    sh = case["shipping"]
    shipping = ShippingConfig(
        mode=sh["mode"],
        shipping_cost=sh["shippingCost"],
        subsidize_pct=sh["subsidizePct"],
    )
    channel = None
    if case["saleChannel"] is not None:
        channel = SaleChannel(
            id=None,
            name="channel",
            fee_pct=case["saleChannel"]["feePct"],
            fee_fixed=case["saleChannel"]["feeFixed"],
        )
    piece = PieceInput(
        name=case["id"],
        printer=printer,
        print_time_hours=case["printTimeHours"],
        materials=materials,
        waste_pct=case["wastePct"],
        labor=labor,
        labor_rate_hour=case["laborRateHour"],
        failure_rate_pct=case["failureRatePct"],
        packaging_cost=case["packagingCost"],
        shipping=shipping,
        sale_channel=channel,
        tax_pct=case["taxPct"],
        payment_gateway_pct=case["paymentGatewayPct"],
        overhead_per_piece=case["overheadPerPiece"],
        energy_tariff_kwh=case["energyTariffKwh"],
    )
    return piece, settings


def _python_result(case) -> dict:
    piece, settings = _build(case)
    res = compute_pricing(
        piece,
        settings,
        margins=tuple(case["margins"]),
        competitor_price=case["competitorPrice"],
    )
    b = res.breakdown
    return {
        "breakdown": {
            "materialCost": _n(b.material_cost),
            "energyCost": _n(b.energy_cost),
            "depreciationCost": _n(b.depreciation_cost),
            "maintenanceCost": _n(b.maintenance_cost),
            "laborCost": _n(b.labor_cost),
            "baseCost": _n(b.base_cost),
            "failureAdjustedCost": _n(b.failure_adjusted_cost),
            "overheadCost": _n(b.overhead_cost),
            "packagingCost": _n(b.packaging_cost),
            "shippingAbsorbed": _n(b.shipping_cost_absorbed),
            "totalCost": _n(b.total_cost),
        },
        "scenarios": [
            {
                "marginPct": _n(sc.margin_pct),
                "priceCostPlus": _n(sc.price_cost_plus),
                "priceMarginOnPrice": _n(sc.price_margin_on_price),
                "netProfitCostPlus": _n(sc.net_profit_cost_plus),
                "netProfitMarginOnPrice": _n(sc.net_profit_margin_on_price),
            }
            for sc in res.scenarios
        ],
        "competitor": (
            {
                "price": _n(res.competitor_analysis["price"]),
                "fees": _n(res.competitor_analysis["fees"]),
                "netProfit": _n(res.competitor_analysis["net_profit"]),
                "netMarginPct": _n(res.competitor_analysis["net_margin_pct"]),
            }
            if res.competitor_analysis is not None
            else None
        ),
    }


@pytest.fixture(scope="session")
def js_results() -> dict:
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node não encontrado no PATH — necessário para o motor JS.")
    runner = ROOT / "tests" / "parity_runner.js"
    proc = subprocess.run(
        [node, str(runner)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert proc.returncode == 0, f"parity_runner.js falhou:\n{proc.stderr}"
    return json.loads(proc.stdout)


def _assert_equal(py, js, path=""):
    """Compara recursivamente floats (com tolerância), 'inf' e estruturas."""
    if isinstance(py, dict):
        assert set(py) == set(js), f"chaves diferentes em {path}: {set(py) ^ set(js)}"
        for k in py:
            _assert_equal(py[k], js[k], f"{path}.{k}")
    elif isinstance(py, list):
        assert len(py) == len(js), f"tamanhos diferentes em {path}"
        for i, (a, b) in enumerate(zip(py, js)):
            _assert_equal(a, b, f"{path}[{i}]")
    elif isinstance(py, float):
        assert isinstance(js, (int, float)), f"{path}: JS='{js}' não é número (Py={py})"
        assert py == pytest.approx(js, abs=ABS_TOL, rel=1e-9), f"{path}: Py={py} != JS={js}"
    else:  # "inf" ou outra string
        assert py == js, f"{path}: Py={py!r} != JS={js!r}"


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_paridade_js_vs_python(case, js_results):
    py = _python_result(case)
    js = js_results[case["id"]]
    _assert_equal(py["breakdown"], js["breakdown"], "breakdown")
    _assert_equal(py["scenarios"], js["scenarios"], "scenarios")
    _assert_equal(py["competitor"], js["competitor"], "competitor")


def test_golden_valores_conhecidos():
    """Trava valores absolutos do caso base — pega erro que afete os dois motores juntos."""
    case = next(c for c in CASES if c["id"] == "basico-1-material")
    res = _python_result(case)
    assert res["breakdown"]["totalCost"] == pytest.approx(36.3185155, abs=1e-4)
    assert res["breakdown"]["materialCost"] == pytest.approx(6.337464, abs=1e-4)
    assert res["breakdown"]["laborCost"] == pytest.approx(20.0, abs=1e-6)
    # cenário recomendado (índice 1, margem 50%) usado na UI e no orçamento
    assert res["scenarios"][1]["priceCostPlus"] == pytest.approx(54.477773, abs=1e-4)
