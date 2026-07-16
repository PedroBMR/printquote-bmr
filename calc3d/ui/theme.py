"""Tema visual do PrintQuote by BMR: fundo escuro, acento violeta, cards
com cantos arredondados e cores semânticas para status
(sucesso/alerta/perigo/info) — identidade própria da marca BMR.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Paleta (mesmas cores do NozzleNote)
# ---------------------------------------------------------------------------
BG = "#0d1017"              # fundo geral (quase preto)
SURFACE = "#141a26"         # cards/painéis
SURFACE_ALT = "#1a2233"     # inputs, linhas alternadas
BORDER = "#2a3244"          # bordas sutis

TEXT_PRIMARY = "#f8fafc"
TEXT_SECONDARY = "#94a3b8"
TEXT_MUTED = "#64748b"

ACCENT = "#7c3aed"          # violeta primário (mesmo do NozzleNote)
ACCENT_HOVER = "#8b5cf6"
ACCENT_PRESSED = "#6d28d9"
ACCENT_SOFT = "#2a2050"     # fundo sutil (linhas selecionadas, abas ativas)
ACCENT_LIGHT = "#c4b5fd"

SUCCESS = "#22c55e"
SUCCESS_SOFT = "#86efac"
WARNING = "#f59e0b"
WARNING_SOFT = "#fcd34d"
DANGER = "#ef4444"
DANGER_SOFT = "#fca5a5"
INFO = "#0891b2"
INFO_SOFT = "#a5f3fc"

FONT_FAMILY = "Segoe UI, Inter, -apple-system, sans-serif"

# Cores fixas por categoria no gráfico de composição de custo, para manter
# consistência visual entre recálculos.
CHART_COLORS = {
    "Material": ACCENT_LIGHT,
    "Energia": WARNING_SOFT,
    "Máquina (depreciação+manutenção)": INFO_SOFT,
    "Mão de obra": SUCCESS_SOFT,
    "Overhead": DANGER_SOFT,
    "Embalagem": TEXT_SECONDARY,
    "Frete absorvido": "#f0abfc",
}


def stylesheet() -> str:
    return f"""
    * {{
        font-family: {FONT_FAMILY};
    }}

    QWidget {{
        background-color: {BG};
        color: {TEXT_PRIMARY};
        font-size: 13px;
    }}

    QMainWindow {{
        background-color: {BG};
    }}

    /* ---------------- Abas ---------------- */
    QTabWidget::pane {{
        border: 1px solid {BORDER};
        border-radius: 12px;
        top: -1px;
        background-color: {BG};
    }}

    QTabBar::tab {{
        background: transparent;
        color: {TEXT_SECONDARY};
        padding: 9px 18px;
        margin-right: 4px;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        font-weight: 600;
    }}

    QTabBar::tab:selected {{
        background: {ACCENT_SOFT};
        color: {TEXT_PRIMARY};
    }}

    QTabBar::tab:hover:!selected {{
        background: rgba(124, 58, 237, 0.12);
        color: {TEXT_PRIMARY};
    }}

    /* ---------------- Cards (GroupBox) ---------------- */
    QGroupBox {{
        background-color: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 16px;
        margin-top: 14px;
        padding: 14px 12px 12px 12px;
        font-weight: 600;
        color: {TEXT_PRIMARY};
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 12px;
        top: -2px;
        padding: 0 8px;
        color: {ACCENT_LIGHT};
        background-color: {BG};
    }}

    /* ---------------- Inputs ---------------- */
    QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox, QTextEdit {{
        background-color: {SURFACE_ALT};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 5px 8px;
        color: {TEXT_PRIMARY};
        selection-background-color: {ACCENT};
    }}

    QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus, QTextEdit:focus {{
        border: 1px solid {ACCENT};
    }}

    QLineEdit:read-only {{
        color: {TEXT_SECONDARY};
    }}

    QComboBox::drop-down {{
        border: none;
        width: 22px;
    }}

    QComboBox QAbstractItemView {{
        background-color: {SURFACE_ALT};
        border: 1px solid {BORDER};
        selection-background-color: {ACCENT};
        selection-color: {TEXT_PRIMARY};
        outline: none;
    }}

    QDoubleSpinBox::up-button, QSpinBox::up-button,
    QDoubleSpinBox::down-button, QSpinBox::down-button {{
        background-color: transparent;
        border: none;
        width: 16px;
    }}

    /* ---------------- Botões ---------------- */
    QPushButton {{
        background-color: {SURFACE_ALT};
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 8px 16px;
        color: {TEXT_PRIMARY};
        font-weight: 600;
    }}

    QPushButton:hover {{
        border: 1px solid {ACCENT};
        color: {TEXT_PRIMARY};
    }}

    QPushButton:pressed {{
        background-color: {ACCENT_SOFT};
    }}

    QPushButton[accent="true"] {{
        background-color: {ACCENT};
        border: 1px solid {ACCENT};
        color: {TEXT_PRIMARY};
    }}

    QPushButton[accent="true"]:hover {{
        background-color: {ACCENT_HOVER};
        border: 1px solid {ACCENT_HOVER};
    }}

    QPushButton[accent="true"]:pressed {{
        background-color: {ACCENT_PRESSED};
    }}

    QPushButton[danger="true"] {{
        background-color: transparent;
        border: 1px solid {DANGER};
        color: {DANGER_SOFT};
    }}

    QPushButton[danger="true"]:hover {{
        background-color: rgba(239, 68, 68, 0.14);
    }}

    /* ---------------- Tabelas ---------------- */
    QTableWidget {{
        background-color: {SURFACE};
        alternate-background-color: {SURFACE_ALT};
        border: 1px solid {BORDER};
        border-radius: 12px;
        gridline-color: {BORDER};
        selection-background-color: {ACCENT_SOFT};
        selection-color: {TEXT_PRIMARY};
    }}

    QTableWidget::item {{
        padding: 4px;
    }}

    QHeaderView::section {{
        background-color: {SURFACE_ALT};
        color: {TEXT_SECONDARY};
        padding: 6px;
        border: none;
        border-bottom: 1px solid {BORDER};
        font-weight: 600;
    }}

    QTableCornerButton::section {{
        background-color: {SURFACE_ALT};
        border: none;
    }}

    /* ---------------- Scroll ---------------- */
    QScrollArea {{
        border: none;
        background-color: transparent;
    }}

    QScrollBar:vertical {{
        background: transparent;
        width: 10px;
        margin: 0;
    }}

    QScrollBar::handle:vertical {{
        background: {BORDER};
        border-radius: 5px;
        min-height: 24px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: {ACCENT};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}

    /* ---------------- Splitter ---------------- */
    QSplitter::handle {{
        background-color: {BORDER};
        width: 2px;
    }}

    /* ---------------- Diálogos ---------------- */
    QMessageBox {{
        background-color: {SURFACE};
    }}

    QLabel {{
        color: {TEXT_PRIMARY};
        background: transparent;
    }}
    """
