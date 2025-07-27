#!/usr/bin/env python3
"""Entry point for the conductivity sensor UI."""

import sys
from PyQt6 import QtWidgets

from .mainwindow import MainWindow


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
