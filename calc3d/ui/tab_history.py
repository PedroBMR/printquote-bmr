"""Aba: Histórico de peças precificadas (biblioteca de peças salvas)."""
from __future__ import annotations

import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..data import repository as repo
from .format_utils import format_brl


class HistoryTab(QWidget):
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        self._build_ui()
        self.reload()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Data", "Peça", "Peso (g)", "Tempo (h)", "Preço sugerido"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self._on_select)
        layout.addWidget(self.table, stretch=2)

        side = QVBoxLayout()
        self.detail_view = QTextEdit()
        self.detail_view.setReadOnly(True)
        side.addWidget(self.detail_view)

        self.delete_btn = QPushButton("Excluir peça selecionada")
        self.delete_btn.setProperty("danger", "true")
        self.delete_btn.clicked.connect(self._on_delete)
        side.addWidget(self.delete_btn)

        layout.addLayout(side, stretch=1)

    def reload(self):
        self.rows = repo.list_parts_history(self.conn)
        self.table.setRowCount(0)
        for row_data in self.rows:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(row_data["created_at"]))
            self.table.setItem(row, 1, QTableWidgetItem(row_data["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(f"{row_data['weight_g']:.1f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{row_data['print_time_hours']:.2f}"))
            price = row_data["final_price"]
            self.table.setItem(row, 4, QTableWidgetItem(format_brl(price) if price else "-"))
            self.table.item(row, 0).setData(Qt.UserRole, row_data["id"])

    def _on_select(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        row = rows[0].row()
        part_id = self.table.item(row, 0).data(Qt.UserRole)
        data = next((r for r in self.rows if r["id"] == part_id), None)
        if not data:
            return
        materials = json.loads(data["materials_json"])
        labor = json.loads(data["labor_json"])
        breakdown = json.loads(data["breakdown_json"])

        lines = [f"Peça: {data['name']}", f"Criada em: {data['created_at']}", "", "Materiais:"]
        for m in materials:
            lines.append(f"  - {m['name']}: {m['grams']:.1f} g")
        lines.append("")
        lines.append("Mão de obra (horas):")
        for k, v in labor.items():
            lines.append(f"  - {k}: {v}")
        lines.append("")
        lines.append("Breakdown de custos:")
        for k, v in breakdown.items():
            lines.append(f"  - {k}: {format_brl(v)}")

        self.detail_view.setPlainText("\n".join(lines))

    def _on_delete(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        row = rows[0].row()
        part_id = self.table.item(row, 0).data(Qt.UserRole)
        resp = QMessageBox.question(self, "Excluir peça", "Tem certeza que deseja excluir esta peça do histórico?")
        if resp == QMessageBox.Yes:
            repo.delete_part_history(self.conn, part_id)
            self.detail_view.clear()
            self.reload()
