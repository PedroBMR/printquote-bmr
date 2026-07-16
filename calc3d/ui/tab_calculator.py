"""Aba: Calculadora de peça — puxa materiais e impressoras da biblioteca,
monta um PieceInput e chama o motor de cálculo (core.calculator) para
gerar o breakdown de custos e os cenários de preço.
"""
from __future__ import annotations

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QTextDocument
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..core.calculator import compute_pricing
from ..core.models import (
    LaborStages,
    MaterialUsage,
    PieceInput,
    ShippingConfig,
)
from ..data import repository as repo
from .format_utils import format_brl, format_pct
from .theme import (
    ACCENT_LIGHT,
    CHART_COLORS,
    DANGER_SOFT,
    SUCCESS_SOFT,
    SURFACE,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)
from .widgets import FlexibleDoubleSpinBox as QDoubleSpinBox

SHIPPING_MODES = [
    ("Repassar integral ao cliente", "repassar"),
    ("Subsidiar parcialmente", "subsidiar"),
    ("Grátis (embutido no preço)", "gratis_embutido"),
]


class MaterialRowsWidget(QTableWidget):
    ROW_HEIGHT = 36
    HEADER_HEIGHT = 30
    MAX_VISIBLE_ROWS = 4

    def __init__(self, get_materials, parent=None):
        super().__init__(0, 3, parent)
        self._get_materials = get_materials
        self.setHorizontalHeaderLabels(["Material", "Peso (g)", ""])
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.verticalHeader().setDefaultSectionSize(self.ROW_HEIGHT)
        self._update_height()

    def add_row(self):
        row = self.rowCount()
        self.insertRow(row)

        combo = QComboBox()
        for material in self._get_materials():
            combo.addItem(f"{material.name} ({material.unit_label})", material)
        self.setCellWidget(row, 0, combo)

        weight_spin = QDoubleSpinBox()
        weight_spin.setRange(0, 100000)
        weight_spin.setDecimals(2)
        weight_spin.setSuffix(" g")
        self.setCellWidget(row, 1, weight_spin)

        remove_btn = QPushButton("Remover")
        remove_btn.clicked.connect(lambda: self._remove_row(remove_btn))
        self.setCellWidget(row, 2, remove_btn)
        self._update_height()

    def _remove_row(self, button):
        for row in range(self.rowCount()):
            if self.cellWidget(row, 2) is button:
                self.removeRow(row)
                break
        self._update_height()

    def _update_height(self):
        visible_rows = min(max(self.rowCount(), 1), self.MAX_VISIBLE_ROWS)
        total = self.HEADER_HEIGHT + self.ROW_HEIGHT * visible_rows + 4
        self.setMinimumHeight(total)
        self.setMaximumHeight(total)

    def refresh_materials(self, materials):
        for row in range(self.rowCount()):
            combo = self.cellWidget(row, 0)
            current = combo.currentData()
            combo.blockSignals(True)
            combo.clear()
            for material in materials:
                combo.addItem(f"{material.name} ({material.unit_label})", material)
            if current is not None:
                idx = combo.findData(current)
                if idx >= 0:
                    combo.setCurrentIndex(idx)
            combo.blockSignals(False)

    def usages(self) -> list:
        result = []
        for row in range(self.rowCount()):
            combo = self.cellWidget(row, 0)
            spin = self.cellWidget(row, 1)
            material = combo.currentData()
            grams = spin.value()
            if material is not None and grams > 0:
                result.append(MaterialUsage(material=material, grams=grams))
        return result


class CalculatorTab(QWidget):
    def __init__(self, conn, settings_tab, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.settings_tab = settings_tab
        self._last_result = None
        self._last_piece = None
        self._build_ui()
        self.reload_libraries()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        splitter = QSplitter(Qt.Horizontal, self)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.addWidget(splitter)

        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setMinimumWidth(480)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setSpacing(14)
        left_layout.setContentsMargins(2, 2, 10, 2)
        left_scroll.setWidget(left)
        splitter.addWidget(left_scroll)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setSpacing(14)
        right_layout.setContentsMargins(10, 2, 2, 2)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([520, 900])

        # --- Dados básicos ---
        basics_box = QGroupBox("Peça")
        basics = QFormLayout(basics_box)
        self.name_edit = QLineEdit()
        self.printer_combo = QComboBox()
        self.print_time_spin = QDoubleSpinBox()
        self.print_time_spin.setRange(0, 5000)
        self.print_time_spin.setSuffix(" h")
        self.print_time_spin.setDecimals(2)
        basics.addRow("Nome da peça:", self.name_edit)
        basics.addRow("Impressora:", self.printer_combo)
        basics.addRow("Tempo de impressão:", self.print_time_spin)
        left_layout.addWidget(basics_box)

        # --- Materiais ---
        materials_box = QGroupBox("Materiais (da biblioteca)")
        materials_layout = QVBoxLayout(materials_box)
        self.material_rows = MaterialRowsWidget(lambda: self.materials)
        materials_layout.addWidget(self.material_rows)
        add_material_btn = QPushButton("+ Adicionar material")
        add_material_btn.clicked.connect(self.material_rows.add_row)
        materials_layout.addWidget(add_material_btn)

        self.waste_spin = QDoubleSpinBox()
        self.waste_spin.setRange(0, 100)
        self.waste_spin.setSuffix(" %")
        self.waste_spin.setValue(5)
        waste_row = QFormLayout()
        waste_row.addRow("Desperdício/purga:", self.waste_spin)
        materials_layout.addLayout(waste_row)
        left_layout.addWidget(materials_box)

        # --- Mão de obra ---
        labor_box = QGroupBox("Mão de obra (horas)")
        labor_form = QFormLayout(labor_box)
        self.modeling_spin = self._hours_spin()
        self.slicing_spin = self._hours_spin()
        self.post_spin = self._hours_spin()
        self.packaging_hours_spin = self._hours_spin()
        self.labor_rate_spin = QDoubleSpinBox()
        self.labor_rate_spin.setRange(0, 1000)
        self.labor_rate_spin.setPrefix("R$ ")
        self.labor_rate_spin.setSuffix(" /h (deixe 0 para usar padrão)")
        labor_form.addRow("Modelagem/preparação:", self.modeling_spin)
        labor_form.addRow("Fatiamento/setup:", self.slicing_spin)
        labor_form.addRow("Pós-processamento:", self.post_spin)
        labor_form.addRow("Embalagem:", self.packaging_hours_spin)
        labor_form.addRow("Valor hora (override):", self.labor_rate_spin)
        left_layout.addWidget(labor_box)

        # --- Falha, overhead, embalagem, frete ---
        extra_box = QGroupBox("Falha, overhead, embalagem e frete")
        extra_form = QFormLayout(extra_box)
        self.failure_spin = QDoubleSpinBox()
        self.failure_spin.setRange(0, 95)
        self.failure_spin.setSuffix(" % (0 = usar padrão)")
        self.overhead_spin = QDoubleSpinBox()
        self.overhead_spin.setRange(0, 10000)
        self.overhead_spin.setPrefix("R$ ")
        self.packaging_cost_spin = QDoubleSpinBox()
        self.packaging_cost_spin.setRange(0, 10000)
        self.packaging_cost_spin.setPrefix("R$ ")

        self.shipping_mode_combo = QComboBox()
        for label, value in SHIPPING_MODES:
            self.shipping_mode_combo.addItem(label, value)
        self.shipping_cost_spin = QDoubleSpinBox()
        self.shipping_cost_spin.setRange(0, 10000)
        self.shipping_cost_spin.setPrefix("R$ ")
        self.shipping_subsidize_spin = QDoubleSpinBox()
        self.shipping_subsidize_spin.setRange(0, 100)
        self.shipping_subsidize_spin.setSuffix(" %")

        extra_form.addRow("Taxa de falha (override):", self.failure_spin)
        extra_form.addRow("Overhead por peça (override):", self.overhead_spin)
        extra_form.addRow("Custo de embalagem:", self.packaging_cost_spin)
        extra_form.addRow("Frete - modo:", self.shipping_mode_combo)
        extra_form.addRow("Frete - custo:", self.shipping_cost_spin)
        extra_form.addRow("Frete - % subsidiado:", self.shipping_subsidize_spin)
        left_layout.addWidget(extra_box)

        # --- Venda ---
        sale_box = QGroupBox("Canal de venda, impostos e comparação")
        sale_form = QFormLayout(sale_box)
        self.channel_combo = QComboBox()
        self.gateway_spin = QDoubleSpinBox()
        self.gateway_spin.setRange(0, 20)
        self.gateway_spin.setSuffix(" % (0 = usar padrão)")
        self.tax_spin = QDoubleSpinBox()
        self.tax_spin.setRange(0, 50)
        self.tax_spin.setSuffix(" % (0 = usar padrão)")
        self.competitor_price_spin = QDoubleSpinBox()
        self.competitor_price_spin.setRange(0, 100000)
        self.competitor_price_spin.setPrefix("R$ ")

        sale_form.addRow("Canal de venda:", self.channel_combo)
        sale_form.addRow("Taxa de gateway (override):", self.gateway_spin)
        sale_form.addRow("Imposto (override):", self.tax_spin)
        sale_form.addRow("Preço concorrente (opcional):", self.competitor_price_spin)
        left_layout.addWidget(sale_box)

        btn_row = QHBoxLayout()
        self.calc_btn = QPushButton("Calcular")
        self.calc_btn.setProperty("accent", "true")
        self.calc_btn.clicked.connect(self.calculate)
        self.save_history_btn = QPushButton("Salvar no histórico")
        self.save_history_btn.clicked.connect(self.save_to_history)
        self.export_pdf_btn = QPushButton("Exportar PDF")
        self.export_pdf_btn.clicked.connect(self.export_pdf)
        btn_row.addWidget(self.calc_btn)
        btn_row.addWidget(self.save_history_btn)
        btn_row.addWidget(self.export_pdf_btn)
        left_layout.addLayout(btn_row)
        left_layout.addStretch()

        # --- Resultado (direita) ---
        result_box = QGroupBox("Breakdown de custos")
        result_layout = QVBoxLayout(result_box)
        self.breakdown_table = QTableWidget(0, 2)
        self.breakdown_table.setHorizontalHeaderLabels(["Categoria", "Valor"])
        self.breakdown_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.breakdown_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.breakdown_table.setAlternatingRowColors(True)
        result_layout.addWidget(self.breakdown_table)

        self.figure = Figure(figsize=(4, 3))
        self.figure.patch.set_facecolor(SURFACE)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setStyleSheet(f"background-color: {SURFACE};")
        result_layout.addWidget(self.canvas)
        right_layout.addWidget(result_box)

        scenarios_box = QGroupBox("Cenários de preço")
        scenarios_layout = QVBoxLayout(scenarios_box)
        self.scenarios_table = QTableWidget(0, 5)
        self.scenarios_table.setHorizontalHeaderLabels(
            ["Margem", "Preço (cost-plus)", "Lucro (cost-plus)", "Preço (margem)", "Lucro (margem)"]
        )
        self.scenarios_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.scenarios_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.scenarios_table.setAlternatingRowColors(True)
        scenarios_layout.addWidget(self.scenarios_table)

        self.competitor_label = QLineEdit()
        self.competitor_label.setReadOnly(True)
        scenarios_layout.addWidget(self.competitor_label)
        right_layout.addWidget(scenarios_box)

    def _hours_spin(self) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(0, 500)
        spin.setSuffix(" h")
        spin.setDecimals(2)
        return spin

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------
    def reload_libraries(self):
        self.materials = repo.list_materials(self.conn)
        self.printers = repo.list_printers(self.conn)
        self.channels = repo.list_sale_channels(self.conn)

        self.material_rows.refresh_materials(self.materials)

        current_printer = self.printer_combo.currentData()
        self.printer_combo.clear()
        for printer in self.printers:
            self.printer_combo.addItem(printer.name, printer)
        if current_printer is not None:
            idx = self.printer_combo.findData(current_printer)
            if idx >= 0:
                self.printer_combo.setCurrentIndex(idx)

        current_channel = self.channel_combo.currentData()
        self.channel_combo.clear()
        for channel in self.channels:
            self.channel_combo.addItem(channel.name, channel)
        if current_channel is not None:
            idx = self.channel_combo.findData(current_channel)
            if idx >= 0:
                self.channel_combo.setCurrentIndex(idx)

    # ------------------------------------------------------------------
    # Build PieceInput from form
    # ------------------------------------------------------------------
    def _build_piece(self) -> PieceInput | None:
        printer = self.printer_combo.currentData()
        if printer is None:
            QMessageBox.warning(self, "Impressora", "Cadastre e selecione uma impressora na aba Impressoras.")
            return None

        usages = self.material_rows.usages()
        if not usages:
            QMessageBox.warning(self, "Materiais", "Adicione ao menos um material com peso maior que zero.")
            return None

        labor = LaborStages(
            modeling_hours=self.modeling_spin.value(),
            slicing_hours=self.slicing_spin.value(),
            post_processing_hours=self.post_spin.value(),
            packaging_hours=self.packaging_hours_spin.value(),
        )

        shipping = ShippingConfig(
            mode=self.shipping_mode_combo.currentData(),
            shipping_cost=self.shipping_cost_spin.value(),
            subsidize_pct=self.shipping_subsidize_spin.value() / 100.0,
        )

        return PieceInput(
            name=self.name_edit.text().strip() or "Peça sem nome",
            printer=printer,
            print_time_hours=self.print_time_spin.value(),
            materials=usages,
            waste_pct=self.waste_spin.value() / 100.0,
            labor=labor,
            labor_rate_hour=self.labor_rate_spin.value() or None,
            failure_rate_pct=(self.failure_spin.value() / 100.0) or None,
            packaging_cost=self.packaging_cost_spin.value(),
            shipping=shipping,
            sale_channel=self.channel_combo.currentData(),
            tax_pct=(self.tax_spin.value() / 100.0) or None,
            payment_gateway_pct=(self.gateway_spin.value() / 100.0) or None,
            overhead_per_piece=self.overhead_spin.value(),
        )

    # ------------------------------------------------------------------
    # Calculate
    # ------------------------------------------------------------------
    def _set_profit_item(self, column: int, row: int, value: float) -> None:
        item = QTableWidgetItem(format_brl(value))
        item.setForeground(QColor(SUCCESS_SOFT if value >= 0 else DANGER_SOFT))
        self.scenarios_table.setItem(row, column, item)

    def calculate(self):
        piece = self._build_piece()
        if piece is None:
            return
        settings = self.settings_tab.current_settings()
        competitor = self.competitor_price_spin.value() or None
        result = compute_pricing(piece, settings, competitor_price=competitor)
        self._last_result = result
        self._last_piece = piece
        self._render_result(result)

    def _render_result(self, result):
        breakdown = result.breakdown
        rows = [
            ("Material", breakdown.material_cost),
            ("Energia", breakdown.energy_cost),
            ("Depreciação", breakdown.depreciation_cost),
            ("Manutenção", breakdown.maintenance_cost),
            ("Mão de obra", breakdown.labor_cost),
            ("Custo base", breakdown.base_cost),
            ("Custo ajustado p/ falha", breakdown.failure_adjusted_cost),
            ("Overhead", breakdown.overhead_cost),
            ("Embalagem", breakdown.packaging_cost),
            ("Frete absorvido", breakdown.shipping_cost_absorbed),
            ("CUSTO TOTAL", breakdown.total_cost),
        ]
        self.breakdown_table.setRowCount(0)
        for label, value in rows:
            row = self.breakdown_table.rowCount()
            self.breakdown_table.insertRow(row)
            label_item = QTableWidgetItem(label)
            value_item = QTableWidgetItem(format_brl(value))
            if label == "CUSTO TOTAL":
                bold = label_item.font()
                bold.setBold(True)
                label_item.setFont(bold)
                value_item.setFont(bold)
                label_item.setForeground(QColor(ACCENT_LIGHT))
                value_item.setForeground(QColor(ACCENT_LIGHT))
            self.breakdown_table.setItem(row, 0, label_item)
            self.breakdown_table.setItem(row, 1, value_item)

        self.figure.clear()
        self.figure.patch.set_facecolor(SURFACE)
        ax = self.figure.add_subplot(111)
        ax.set_facecolor(SURFACE)
        items = breakdown.chart_items()
        if items:
            labels = [i[0] for i in items]
            values = [i[1] for i in items]
            colors = [CHART_COLORS.get(label, TEXT_SECONDARY) for label in labels]
            wedges, texts, autotexts = ax.pie(
                values,
                labels=labels,
                autopct="%1.1f%%",
                textprops={"fontsize": 7, "color": TEXT_PRIMARY},
                colors=colors,
                wedgeprops={"linewidth": 1, "edgecolor": SURFACE},
            )
            for autotext in autotexts:
                autotext.set_color(SURFACE)
                autotext.set_fontweight("bold")
            ax.set_title("Composição do custo", color=TEXT_PRIMARY)
        self.canvas.draw()

        self.scenarios_table.setRowCount(0)
        for scenario in result.scenarios:
            row = self.scenarios_table.rowCount()
            self.scenarios_table.insertRow(row)
            self.scenarios_table.setItem(row, 0, QTableWidgetItem(scenario.label))
            self.scenarios_table.setItem(row, 1, QTableWidgetItem(format_brl(scenario.price_cost_plus)))
            self._set_profit_item(2, row, scenario.net_profit_cost_plus)
            mp_price = "Inviável (margem alta demais p/ taxas)" if scenario.price_margin_on_price == float("inf") else format_brl(scenario.price_margin_on_price)
            self.scenarios_table.setItem(row, 3, QTableWidgetItem(mp_price))
            if scenario.price_margin_on_price == float("inf"):
                self.scenarios_table.setItem(row, 4, QTableWidgetItem("-"))
            else:
                self._set_profit_item(4, row, scenario.net_profit_margin_on_price)

        if result.competitor_analysis:
            ca = result.competitor_analysis
            self.competitor_label.setText(
                f"Preço concorrente {format_brl(ca['price'])} -> lucro real {format_brl(ca['net_profit'])} "
                f"({format_pct(ca['net_margin_pct'])} de margem líquida)"
            )
        else:
            self.competitor_label.setText("")

    # ------------------------------------------------------------------
    # Persistence / export
    # ------------------------------------------------------------------
    def save_to_history(self):
        if not self._last_result or not self._last_piece:
            QMessageBox.information(self, "Histórico", "Calcule a peça antes de salvar.")
            return
        piece = self._last_piece
        breakdown = self._last_result.breakdown
        materials_payload = [
            {"material_id": u.material.id, "name": u.material.name, "grams": u.grams}
            for u in piece.materials
        ]
        labor_payload = {
            "modeling_hours": piece.labor.modeling_hours,
            "slicing_hours": piece.labor.slicing_hours,
            "post_processing_hours": piece.labor.post_processing_hours,
            "packaging_hours": piece.labor.packaging_hours,
        }
        recommended_price = self._last_result.scenarios[1].price_cost_plus if self._last_result.scenarios else None
        repo.save_part_history(
            self.conn,
            name=piece.name,
            printer_id=piece.printer.id,
            print_time_hours=piece.print_time_hours,
            weight_g=piece.total_weight_g(),
            materials_payload=materials_payload,
            labor_payload=labor_payload,
            breakdown_payload=breakdown.as_dict(),
            final_price=recommended_price,
        )
        QMessageBox.information(self, "Histórico", "Peça salva no histórico com sucesso.")

    def export_pdf(self):
        if not self._last_result or not self._last_piece:
            QMessageBox.information(self, "Exportar PDF", "Calcule a peça antes de exportar.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Exportar orçamento", f"{self._last_piece.name}.pdf", "PDF (*.pdf)")
        if not path:
            return
        html = self._build_export_html()
        document = QTextDocument()
        document.setHtml(html)
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(path)
        document.print_(printer)
        QMessageBox.information(self, "Exportar PDF", f"Orçamento exportado para:\n{path}")

    def _build_export_html(self) -> str:
        piece = self._last_piece
        breakdown = self._last_result.breakdown
        rows_html = "".join(
            f"<tr><td>{label}</td><td style='text-align:right'>{format_brl(value)}</td></tr>"
            for label, value in [
                ("Material", breakdown.material_cost),
                ("Energia", breakdown.energy_cost),
                ("Depreciação", breakdown.depreciation_cost),
                ("Manutenção", breakdown.maintenance_cost),
                ("Mão de obra", breakdown.labor_cost),
                ("Overhead", breakdown.overhead_cost),
                ("Embalagem", breakdown.packaging_cost),
                ("Frete absorvido", breakdown.shipping_cost_absorbed),
                ("<b>Custo total</b>", breakdown.total_cost),
            ]
        )
        def _fmt_price(value: float) -> str:
            return "inviável" if value == float("inf") else format_brl(value)

        scenarios_html = "".join(
            f"<tr><td>{s.label}</td><td style='text-align:right'>{format_brl(s.price_cost_plus)}</td>"
            f"<td style='text-align:right'>{_fmt_price(s.price_margin_on_price)}</td></tr>"
            for s in self._last_result.scenarios
        )
        return f"""
        <h2>Orçamento — {piece.name}</h2>
        <p>Impressora: {piece.printer.name} | Tempo de impressão: {piece.print_time_hours:.2f} h</p>
        <table border='1' cellspacing='0' cellpadding='4' width='100%'>
        <tr><th>Categoria</th><th>Valor</th></tr>
        {rows_html}
        </table>
        <h3>Cenários de preço sugeridos</h3>
        <table border='1' cellspacing='0' cellpadding='4' width='100%'>
        <tr><th>Margem</th><th>Preço (cost-plus)</th><th>Preço (margem s/ preço)</th></tr>
        {scenarios_html}
        </table>
        <p>PrintQuote by BMR — Orçamento gerado automaticamente.</p>
        """
