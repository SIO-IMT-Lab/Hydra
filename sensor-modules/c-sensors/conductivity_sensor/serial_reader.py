from __future__ import annotations

import time
import serial
from PyQt6.QtCore import QThread, pyqtSignal


class SerialReader(QThread):
    """Read lines from the conductivity sensor in a background thread."""

    new_sample = pyqtSignal(float, float)  # timestamp_epoch_s, value
    error = pyqtSignal(str)
    stopped = pyqtSignal()

    def __init__(self, port: str, baud: int = 9600, parent=None) -> None:
        super().__init__(parent)
        self.port = port
        self.baud = baud
        self._ser: serial.Serial | None = None
        self._running = False

    def run(self) -> None:
        try:
            self._ser = serial.Serial(self.port, self.baud, timeout=1)
        except Exception as exc:  # pragma: no cover - runtime error path
            self.error.emit(f"Serial open failed: {exc}")
            self.stopped.emit()
            return

        self._running = True
        while self._running:
            try:
                line = self._ser.readline().decode(errors="ignore").strip()
                if line:
                    try:
                        val = float(line)
                        self.new_sample.emit(time.time(), val)
                    except ValueError:
                        pass
            except Exception as exc:  # pragma: no cover - runtime error path
                self.error.emit(f"Serial read error: {exc}")
                break

        try:
            if self._ser and self._ser.is_open:
                self._ser.close()
        except Exception:
            pass

        self.stopped.emit()

    def write(self, data: bytes) -> None:
        try:
            if self._ser and self._ser.is_open:
                self._ser.write(data)
                self._ser.flush()
        except Exception as exc:  # pragma: no cover - runtime error path
            self.error.emit(f"Serial write error: {exc}")

    def stop(self) -> None:
        self._running = False
