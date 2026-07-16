"""Aba: Configurações globais (tarifa de energia, mão de obra, overhead,
taxa de falha padrão e impostos). Tudo usado como default e pode ser
sobrescrito por peça na aba Calculadora.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..core.models import GlobalSettings
from ..data import repository as repo
from .format_utils import format_brl
from .widgets import FlexibleDoubleSpinBox as QDoubleSpinBox


class SettingsTab(QWidget):
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        self._build_ui()
        self.reload()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        box = QGroupBox("Configurações globais (valores padrão)")
        form = QFormLayout(box)

        self.tariff_spin = QDoubleSpinBox()
        self.tariff_spin.setRange(0, 10)
        self.tariff_spin.setDecimals(3)
        self.tariff_spin.setPrefix("R$ ")
        self.tariff_spin.setSuffix(" /kWh")

        self.labor_rate_spin = QDoubleSpinBox()
        self.labor_rate_spin.setRange(0, 1000)
        self.labor_rate_spin.setPrefix("R$ ")
        self.labor_rate_spin.setSuffix(" /hora")

        self.failure_spin = QDoubleSpinBox()
        self.failure_spin.setRange(0, 95)
        self.failure_spin.setSuffix(" %")
        self.failure_spin.setDecimals(1)

        self.tax_spin = QDoubleSpinBox()
        self.tax_spin.setRange(0, 50)
        self.tax_spin.setSuffix(" %")
        self.tax_spin.setDecimals(2)

        self.gateway_spin = QDoubleSpinBox()
        self.gateway_spin.setRange(0, 20)
        self.gateway_spin.setSuffix(" %")
        self.gateway_spin.setDecimals(2)

        self.monthly_fixed_spin = QDoubleSpinBox()
        self.monthly_fixed_spin.setRange(0, 100000)
        self.monthly_fixed_spin.setPrefix("R$ ")
        self.monthly_fixed_spin.setDecimals(2)

        self.expected_volume_spin = QSpinBox()
        self.expected_volume_spin.setRange(1, 100000)

        self.packaging_default_spin = QDoubleSpinBox()
        self.packaging_default_spin.setRange(0, 1000)
        self.packaging_default_spin.setPrefix("R$ ")
        self.packaging_default_spin.setDecimals(2)

        form.addRow("Tarifa de energia:", self.tariff_spin)
        form.addRow("Valor da hora de trabalho:", self.labor_rate_spin)
        form.addRow("Taxa de falha padrão:", self.failure_spin)
        form.addRow("Imposto (MEI/Simples etc.):", self.tax_spin)
        form.addRow("Taxa de gateway de pagamento padrão:", self.gateway_spin)
        form.addRow("Custos fixos mensais (overhead):", self.monthly_fixed_spin)
        form.addRow("Volume mensal esperado (peças):", self.expected_volume_spin)
        form.addRow("Custo de embalagem padrão:", self.packaging_default_spin)

        self.overhead_preview = QLabel()
        form.addRow("Overhead por peça (calculado):", self.overhead_preview)

        for spin in (self.monthly_fixed_spin, self.expected_volume_spin):
            spin.valueChanged.connect(self._update_overhead_preview)

        save_btn = QPushButton("Salvar configurações")
        save_btn.setProperty("accent", "true")
        save_btn.clicked.connect(self._on_save)
        form.addRow(save_btn)

        layout.addWidget(box)
        layout.addStretch()

    def reload(self):
        settings = repo.load_settings(self.conn)
        self.tariff_spin.setValue(settings.energy_tariff_kwh)
        self.labor_rate_spin.setValue(settings.labor_rate_hour)
        self.failure_spin.setValue(settings.failure_rate_pct * 100)
        self.tax_spin.setValue(settings.tax_pct * 100)
        self.gateway_spin.setValue(settings.payment_gateway_pct * 100)
        self.monthly_fixed_spin.setValue(settings.monthly_fixed_costs)
        self.expected_volume_spin.setValue(settings.expected_monthly_volume)
        self.packaging_default_spin.setValue(settings.packaging_cost_default)
        self._update_overhead_preview()

    def _update_overhead_preview(self):
        volume = max(self.expected_volume_spin.value(), 1)
        overhead = self.monthly_fixed_spin.value() / volume
        self.overhead_preview.setText(f"{format_brl(overhead)} por peça")

    def current_settings(self) -> GlobalSettings:
        return GlobalSettings(
            energy_tariff_kwh=self.tariff_spin.value(),
            labor_rate_hour=self.labor_rate_spin.value(),
            failure_rate_pct=self.failure_spin.value() / 100.0,
            tax_pct=self.tax_spin.value() / 100.0,
            payment_gateway_pct=self.gateway_spin.value() / 100.0,
            monthly_fixed_costs=self.monthly_fixed_spin.value(),
            expected_monthly_volume=self.expected_volume_spin.value(),
            packaging_cost_default=self.packaging_default_spin.value(),
        )

    def _on_save(self):
        repo.save_settings(self.conn, self.current_settings())
        QMessageBox.information(self, "Configurações", "Configurações salvas com sucesso.")
