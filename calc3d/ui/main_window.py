"""Janela principal: agrega as abas em um QTabWidget."""
from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QTabWidget

from .tab_calculator import CalculatorTab
from .tab_channels import ChannelsTab
from .tab_history import HistoryTab
from .tab_materials import MaterialsTab
from .tab_printers import PrintersTab
from .tab_settings import SettingsTab


class MainWindow(QMainWindow):
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.setWindowTitle("PrintQuote by BMR")
        self.resize(1300, 850)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.settings_tab = SettingsTab(conn)
        self.materials_tab = MaterialsTab(conn)
        self.printers_tab = PrintersTab(conn)
        self.channels_tab = ChannelsTab(conn)
        self.calculator_tab = CalculatorTab(conn, self.settings_tab)
        self.history_tab = HistoryTab(conn)

        self.tabs.addTab(self.calculator_tab, "Calculadora")
        self.tabs.addTab(self.materials_tab, "Materiais")
        self.tabs.addTab(self.printers_tab, "Impressoras")
        self.tabs.addTab(self.channels_tab, "Canais de venda")
        self.tabs.addTab(self.settings_tab, "Configurações")
        self.tabs.addTab(self.history_tab, "Histórico")

        # Mantém a calculadora sincronizada com a biblioteca sempre que ela mudar
        self.materials_tab.materials_changed.connect(self.calculator_tab.reload_libraries)
        self.printers_tab.printers_changed.connect(self.calculator_tab.reload_libraries)
        self.channels_tab.channels_changed.connect(self.calculator_tab.reload_libraries)

        self.tabs.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index: int):
        widget = self.tabs.widget(index)
        if widget is self.history_tab:
            self.history_tab.reload()
        elif widget is self.calculator_tab:
            self.calculator_tab.reload_libraries()
