"""Widgets compartilhados da interface."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QDoubleSpinBox


class FlexibleDoubleSpinBox(QDoubleSpinBox):
    """QDoubleSpinBox que aceita tanto '.' quanto ',' como separador decimal.

    O locale do Windows em pt-BR espera vírgula; sem isso, digitar "3.5"
    é silenciosamente rejeitado e o campo volta para 0 sem nenhum aviso.
    """

    def keyPressEvent(self, event: QKeyEvent) -> None:
        decimal_point = self.locale().decimalPoint()
        if event.text() in (".", ",") and event.text() != decimal_point:
            translated = QKeyEvent(
                event.type(),
                Qt.Key_Comma if decimal_point == "," else Qt.Key_Period,
                event.modifiers(),
                decimal_point,
            )
            super().keyPressEvent(translated)
            return
        super().keyPressEvent(event)
