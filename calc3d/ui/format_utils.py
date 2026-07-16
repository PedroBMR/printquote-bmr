"""Formatação de valores em Real (BRL) no padrão brasileiro (vírgula como
separador decimal, ponto como separador de milhar), consistente com o
padrão exibido pelos campos numéricos do Qt no locale pt-BR.
"""
from __future__ import annotations


def format_brl(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_pct(value: float) -> str:
    """Recebe a fração (ex: 0.12) e devolve '12,00%'."""
    return f"{value * 100:.2f}%".replace(".", ",")
