"""Aba: Perfis de Impressora (depreciação, energia, manutenção)."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..core.models import PrinterProfile
from ..data import repository as repo
from .format_utils import format_brl
from .widgets import FlexibleDoubleSpinBox as QDoubleSpinBox


class PrintersTab(QWidget):
    printers_changed = Signal()

    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        self._editing_id = None
        self._build_ui()
        self.reload()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Nome", "Valor pago (R$)", "Vida útil (h)", "Potência (W)", "Manutenção (R$/h)"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self._on_select)
        layout.addWidget(self.table, stretch=2)

        form_box = QGroupBox("Cadastrar / Editar impressora")
        form = QFormLayout(form_box)

        self.name_edit = QLineEdit()
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 1_000_000)
        self.price_spin.setPrefix("R$ ")
        self.price_spin.setDecimals(2)

        self.lifetime_spin = QDoubleSpinBox()
        self.lifetime_spin.setRange(1, 100000)
        self.lifetime_spin.setSuffix(" h")
        self.lifetime_spin.setDecimals(0)

        self.watts_spin = QDoubleSpinBox()
        self.watts_spin.setRange(1, 5000)
        self.watts_spin.setSuffix(" W")
        self.watts_spin.setDecimals(0)

        self.maintenance_spin = QDoubleSpinBox()
        self.maintenance_spin.setRange(0, 1000)
        self.maintenance_spin.setPrefix("R$ ")
        self.maintenance_spin.setDecimals(3)

        self.notes_edit = QLineEdit()

        form.addRow("Nome:", self.name_edit)
        form.addRow("Valor pago:", self.price_spin)
        form.addRow("Vida útil estimada:", self.lifetime_spin)
        form.addRow("Potência média:", self.watts_spin)
        form.addRow("Manutenção (por hora de uso):", self.maintenance_spin)
        form.addRow("Observações:", self.notes_edit)

        btn_row = QHBoxLayout()
        self.save_btn = QPushButton("Salvar")
        self.save_btn.setProperty("accent", "true")
        self.new_btn = QPushButton("Novo")
        self.delete_btn = QPushButton("Excluir")
        self.delete_btn.setProperty("danger", "true")
        self.save_btn.clicked.connect(self._on_save)
        self.new_btn.clicked.connect(self._clear_form)
        self.delete_btn.clicked.connect(self._on_delete)
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.new_btn)
        btn_row.addWidget(self.delete_btn)
        form.addRow(btn_row)

        side = QVBoxLayout()
        side.addWidget(form_box)
        side.addStretch()
        layout.addLayout(side, stretch=1)

    def reload(self):
        self.printers = repo.list_printers(self.conn)
        self.table.setRowCount(0)
        for printer in self.printers:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(printer.name))
            self.table.setItem(row, 1, QTableWidgetItem(format_brl(printer.purchase_price)))
            self.table.setItem(row, 2, QTableWidgetItem(f"{printer.lifetime_hours:.0f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{printer.watts_avg:.0f}"))
            self.table.setItem(row, 4, QTableWidgetItem(format_brl(printer.maintenance_cost_per_hour)))
            self.table.item(row, 0).setData(Qt.UserRole, printer.id)
        self.printers_changed.emit()

    def _on_select(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        row = rows[0].row()
        printer_id = self.table.item(row, 0).data(Qt.UserRole)
        printer = next((p for p in self.printers if p.id == printer_id), None)
        if not printer:
            return
        self._editing_id = printer.id
        self.name_edit.setText(printer.name)
        self.price_spin.setValue(printer.purchase_price)
        self.lifetime_spin.setValue(printer.lifetime_hours)
        self.watts_spin.setValue(printer.watts_avg)
        self.maintenance_spin.setValue(printer.maintenance_cost_per_hour)
        self.notes_edit.setText(printer.notes)

    def _clear_form(self):
        self._editing_id = None
        self.name_edit.clear()
        self.price_spin.setValue(0)
        self.lifetime_spin.setValue(6000)
        self.watts_spin.setValue(120)
        self.maintenance_spin.setValue(0.15)
        self.notes_edit.clear()
        self.table.clearSelection()

    def _on_save(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Campo obrigatório", "Informe o nome da impressora.")
            return
        printer = PrinterProfile(
            id=self._editing_id,
            name=name,
            purchase_price=self.price_spin.value(),
            lifetime_hours=self.lifetime_spin.value(),
            watts_avg=self.watts_spin.value(),
            maintenance_cost_per_hour=self.maintenance_spin.value(),
            notes=self.notes_edit.text().strip(),
        )
        repo.save_printer(self.conn, printer)
        self._clear_form()
        self.reload()

    def _on_delete(self):
        if self._editing_id is None:
            return
        resp = QMessageBox.question(self, "Excluir impressora", "Tem certeza que deseja excluir este perfil?")
        if resp == QMessageBox.Yes:
            repo.delete_printer(self.conn, self._editing_id)
            self._clear_form()
            self.reload()
