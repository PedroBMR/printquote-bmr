"""Aba: Canais de Venda (marketplaces e taxas)."""
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

from ..core.models import SaleChannel
from ..data import repository as repo
from .format_utils import format_brl, format_pct
from .widgets import FlexibleDoubleSpinBox as QDoubleSpinBox


class ChannelsTab(QWidget):
    channels_changed = Signal()

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

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Canal", "Taxa (%)", "Taxa fixa (R$)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self._on_select)
        layout.addWidget(self.table, stretch=2)

        form_box = QGroupBox("Cadastrar / Editar canal de venda")
        form = QFormLayout(form_box)

        self.name_edit = QLineEdit()
        self.fee_pct_spin = QDoubleSpinBox()
        self.fee_pct_spin.setRange(0, 100)
        self.fee_pct_spin.setSuffix(" %")
        self.fee_pct_spin.setDecimals(2)

        self.fee_fixed_spin = QDoubleSpinBox()
        self.fee_fixed_spin.setRange(0, 1000)
        self.fee_fixed_spin.setPrefix("R$ ")
        self.fee_fixed_spin.setDecimals(2)

        form.addRow("Nome do canal:", self.name_edit)
        form.addRow("Taxa percentual:", self.fee_pct_spin)
        form.addRow("Taxa fixa por venda:", self.fee_fixed_spin)

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
        self.channels = repo.list_sale_channels(self.conn)
        self.table.setRowCount(0)
        for channel in self.channels:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(channel.name))
            self.table.setItem(row, 1, QTableWidgetItem(format_pct(channel.fee_pct)))
            self.table.setItem(row, 2, QTableWidgetItem(format_brl(channel.fee_fixed)))
            self.table.item(row, 0).setData(Qt.UserRole, channel.id)
        self.channels_changed.emit()

    def _on_select(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        row = rows[0].row()
        channel_id = self.table.item(row, 0).data(Qt.UserRole)
        channel = next((c for c in self.channels if c.id == channel_id), None)
        if not channel:
            return
        self._editing_id = channel.id
        self.name_edit.setText(channel.name)
        self.fee_pct_spin.setValue(channel.fee_pct * 100)
        self.fee_fixed_spin.setValue(channel.fee_fixed)

    def _clear_form(self):
        self._editing_id = None
        self.name_edit.clear()
        self.fee_pct_spin.setValue(0)
        self.fee_fixed_spin.setValue(0)
        self.table.clearSelection()

    def _on_save(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Campo obrigatório", "Informe o nome do canal.")
            return
        channel = SaleChannel(
            id=self._editing_id,
            name=name,
            fee_pct=self.fee_pct_spin.value() / 100.0,
            fee_fixed=self.fee_fixed_spin.value(),
        )
        repo.save_sale_channel(self.conn, channel)
        self._clear_form()
        self.reload()

    def _on_delete(self):
        if self._editing_id is None:
            return
        resp = QMessageBox.question(self, "Excluir canal", "Tem certeza que deseja excluir este canal?")
        if resp == QMessageBox.Yes:
            repo.delete_sale_channel(self.conn, self._editing_id)
            self._clear_form()
            self.reload()
