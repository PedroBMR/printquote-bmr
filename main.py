"""Ponto de entrada do PrintQuote by BMR — calculadora de custos e
precificação para impressão 3D.
"""
import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from calc3d.data.database import get_connection, init_db
from calc3d.data.defaults import seed_if_empty
from calc3d.ui.main_window import MainWindow
from calc3d.ui.theme import stylesheet

if getattr(sys, "frozen", False):
    # Empacotado pelo PyInstaller: os recursos ficam em sys._MEIPASS, não
    # ao lado deste arquivo .py (que não existe mais como tal no .exe).
    _BASE_DIR = Path(sys._MEIPASS)
else:
    _BASE_DIR = Path(__file__).resolve().parent

ICON_PATH = _BASE_DIR / "calc3d" / "ui" / "assets" / "icon.ico"


def main():
    conn = get_connection()
    init_db(conn)
    seed_if_empty(conn)

    app = QApplication(sys.argv)
    app.setApplicationName("PrintQuote by BMR")
    app.setStyleSheet(stylesheet())
    if ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(ICON_PATH)))
    window = MainWindow(conn)
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
