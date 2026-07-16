"""Aba: Biblioteca de Materiais (filamentos e resinas).

Permite cadastrar, editar e excluir materiais para depois só puxar da
biblioteca na hora de precificar uma peça.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
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

from ..core.models import Material, MaterialType
from ..data import repository as repo
from .format_utils import format_brl
from .widgets import FlexibleDoubleSpinBox as QDoubleSpinBox


class MaterialsTab(QWidget):
    materials_changed = Signal()

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

        # Tabela
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Nome", "Tipo", "Preço", "Unidade", "Obs."])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self._on_select)
        layout.addWidget(self.table, stretch=2)

        # Formulário
        form_box = QGroupBox("Cadastrar / Editar material")
        form = QFormLayout(form_box)

        self.name_edit = QLineEdit()
        self.type_combo = QComboBox()
        self.type_combo.addItem("Filamento", MaterialType.FILAMENT)
        self.type_combo.addItem("Resina", MaterialType.RESIN)
        self.type_combo.currentIndexChanged.connect(self._update_unit_label)

        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 100000)
        self.price_spin.setDecimals(2)
        self.price_spin.setPrefix("R$ ")
        self.price_spin.setSingleStep(5)

        self.unit_label = QLineEdit("kg")
        self.unit_label.setReadOnly(True)

        self.notes_edit = QLineEdit()

        form.addRow("Nome:", self.name_edit)
        form.addRow("Tipo:", self.type_combo)
        form.addRow("Preço (por kg ou por L):", self.price_spin)
        form.addRow("Unidade:", self.unit_label)
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

        self._update_unit_label()

    def _update_unit_label(self):
        mtype = self.type_combo.currentData()
        self.unit_label.setText("kg" if mtype == MaterialType.FILAMENT else "L")

    def reload(self):
        self.materials = repo.list_materials(self.conn)
        self.table.setRowCount(0)
        for material in self.materials:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(material.name))
            tipo = "Filamento" if material.material_type == MaterialType.FILAMENT else "Resina"
            self.table.setItem(row, 1, QTableWidgetItem(tipo))
            self.table.setItem(row, 2, QTableWidgetItem(format_brl(material.price_per_kg)))
            self.table.setItem(row, 3, QTableWidgetItem(material.unit_label))
            self.table.setItem(row, 4, QTableWidgetItem(material.notes))
            self.table.item(row, 0).setData(Qt.UserRole, material.id)
        self.materials_changed.emit()

    def _on_select(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        row = rows[0].row()
        material_id = self.table.item(row, 0).data(Qt.UserRole)
        material = next((m for m in self.materials if m.id == material_id), None)
        if not material:
            return
        self._editing_id = material.id
        self.name_edit.setText(material.name)
        idx = self.type_combo.findData(material.material_type)
        self.type_combo.setCurrentIndex(max(idx, 0))
        self.price_spin.setValue(material.price_per_kg)
        self.notes_edit.setText(material.notes)
        self._update_unit_label()

    def _clear_form(self):
        self._editing_id = None
        self.name_edit.clear()
        self.type_combo.setCurrentIndex(0)
        self.price_spin.setValue(0)
        self.notes_edit.clear()
        self.table.clearSelection()

    def _on_save(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Campo obrigatório", "Informe o nome do material.")
            return
        material = Material(
            id=self._editing_id,
            name=name,
            material_type=MaterialType(self.type_combo.currentData()),
            price_per_kg=self.price_spin.value(),
            unit_label=self.unit_label.text(),
            notes=self.notes_edit.text().strip(),
        )
        repo.save_material(self.conn, material)
        self._clear_form()
        self.reload()

    def _on_delete(self):
        if self._editing_id is None:
            return
        resp = QMessageBox.question(self, "Excluir material", "Tem certeza que deseja excluir este material?")
        if resp == QMessageBox.Yes:
            repo.delete_material(self.conn, self._editing_id)
            self._clear_form()
            self.reload()
