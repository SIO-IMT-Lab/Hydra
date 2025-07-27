from __future__ import annotations

import csv
from collections import deque
from datetime import datetime
from typing import Optional

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QTimer
import pyqtgraph as pg
import serial.tools.list_ports

from .serial_reader import SerialReader


class MainWindow(QtWidgets.QMainWindow):
    """Main application window for the conductivity UI."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("SIO:Conductivity")
        self.setMinimumSize(1000, 600)

        self.reader: Optional[SerialReader] = None
        self.logging_enabled = False
        self.log_writer: Optional[csv.writer] = None
        self.log_file = None
        self.notes_file = None
        self.base_filename: Optional[str] = None

        self.plot_seconds = 60
        self.time_buf = deque(maxlen=10_000)
        self.data_buf = deque(maxlen=10_000)

        self._build_ui()
        self._apply_style()

        self.plot_timer = QTimer(self)
        self.plot_timer.setInterval(50)
        self.plot_timer.timeout.connect(self.update_plot)
        self.plot_timer.start()

        self.refresh_ports()

    # ---------- UI ----------
    def _build_ui(self) -> None:
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        top_row = QtWidgets.QHBoxLayout()

        self.port_combo = QtWidgets.QComboBox()
        self.port_refresh_btn = QtWidgets.QPushButton("Refresh")
        self.port_refresh_btn.clicked.connect(self.refresh_ports)

        self.connect_btn = QtWidgets.QPushButton("Connect")
        self.connect_btn.setCheckable(True)
        self.connect_btn.clicked.connect(self.toggle_connection)

        self.prefix_edit = QtWidgets.QLineEdit()
        self.prefix_edit.setPlaceholderText("Log prefix (e.g., FoamRuns)")
        self.prefix_edit.setText("FoamRuns")

        self.duration_spin = QtWidgets.QSpinBox()
        self.duration_spin.setRange(5, 24 * 60 * 60)
        self.duration_spin.setValue(60)
        self.duration_spin.valueChanged.connect(self.on_duration_changed)

        self.log_btn = QtWidgets.QPushButton("Start Logging")
        self.log_btn.setEnabled(False)
        self.log_btn.setCheckable(True)
        self.log_btn.clicked.connect(self.toggle_logging)

        self.status_lbl = QtWidgets.QLabel("Disconnected")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        top_row.addWidget(QtWidgets.QLabel("Port:"))
        top_row.addWidget(self.port_combo, 1)
        top_row.addWidget(self.port_refresh_btn)
        top_row.addSpacing(10)
        top_row.addWidget(self.connect_btn)
        top_row.addSpacing(20)
        top_row.addWidget(QtWidgets.QLabel("Prefix:"))
        top_row.addWidget(self.prefix_edit, 1)
        top_row.addSpacing(10)
        top_row.addWidget(QtWidgets.QLabel("Plot window (s):"))
        top_row.addWidget(self.duration_spin)
        top_row.addSpacing(20)
        top_row.addWidget(self.log_btn)
        top_row.addSpacing(20)
        top_row.addWidget(self.status_lbl, 1)

        layout.addLayout(top_row)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground("#202124")
        self.plot_widget.showGrid(x=True, y=True, alpha=0.2)
        self.plot_data_item = self.plot_widget.plot([], [], pen=pg.mkPen(width=2))
        self.plot_widget.setLabel("left", "Conductivity")
        self.plot_widget.setLabel("bottom", "Time (s)")
        layout.addWidget(self.plot_widget, 1)

        notes_row = QtWidgets.QHBoxLayout()
        self.notes_edit = QtWidgets.QLineEdit()
        self.notes_edit.setPlaceholderText("Enter a note and click 'Add Note'...")
        self.add_note_btn = QtWidgets.QPushButton("Add Note")
        self.add_note_btn.setEnabled(False)
        self.add_note_btn.clicked.connect(self.add_note)
        notes_row.addWidget(QtWidgets.QLabel("Notes:"))
        notes_row.addWidget(self.notes_edit, 1)
        notes_row.addWidget(self.add_note_btn)
        layout.addLayout(notes_row)

        self.console = QtWidgets.QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.setMaximumBlockCount(1000)
        layout.addWidget(self.console, 0)

        self._set_status("Disconnected", "red")

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            QWidget {
                background-color: #121212;
                color: #E0E0E0;
                font-size: 14px;
            }
            QLineEdit, QComboBox, QSpinBox, QPlainTextEdit {
                background-color: #1E1E1E;
                border: 1px solid #2E2E2E;
                padding: 4px;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #2A2A2A;
                border: 1px solid #3A3A3A;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:checked {
                background-color: #37474F;
            }
            QPushButton:disabled {
                background-color: #444444;
                color: #777777;
            }
            QLabel {
                font-size: 14px;
            }
            """
        )

    # ---------- Serial + Logging ----------
    def refresh_ports(self) -> None:
        self.port_combo.clear()
        for p in serial.tools.list_ports.comports():
            self.port_combo.addItem(p.device)

    def toggle_connection(self, checked: bool) -> None:
        if checked:
            port = self.port_combo.currentText().strip()
            if not port:
                self.console_append("No serial port selected.")
                self.connect_btn.setChecked(False)
                return
            self.reader = SerialReader(port=port, baud=9600)
            self.reader.new_sample.connect(self.on_new_sample)
            self.reader.error.connect(self.on_serial_error)
            self.reader.stopped.connect(self.on_reader_stopped)
            self.reader.start()
            self.connect_btn.setText("Disconnect")
            self._set_status("Connected (idle)", "#FFB300")
            self.log_btn.setEnabled(True)
            self.console_append(f"Connected to {port}")
            self.reader.write(b"SC\r\n")
        else:
            if self.reader:
                self.reader.write(b"SC\r\n")
                self.reader.wait(1000)
            self.stop_logging_if_needed(send_stop_command=True)
            if self.reader:
                self.reader.stop()
                self.reader.wait(2000)
                self.reader = None
            self.connect_btn.setText("Connect")
            self._set_status("Disconnected", "red")
            self.log_btn.setEnabled(False)
            self.console_append("Disconnected.")

    def toggle_logging(self, checked: bool) -> None:
        if checked:
            if not self.reader:
                self.console_append("Not connected.")
                self.log_btn.setChecked(False)
                return
            prefix = self.prefix_edit.text().strip()
            if not prefix:
                self.console_append("Please enter a file prefix.")
                self.log_btn.setChecked(False)
                return
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.base_filename = f"{prefix}_{ts}"
            data_fname = f"{self.base_filename}.csv"
            notes_fname = f"{self.base_filename}.notes.txt"
            try:
                self.log_file = open(data_fname, "w", newline="")
                self.log_writer = csv.writer(self.log_file)
                self.log_writer.writerow(["timestamp_iso", "timestamp_epoch_s", "conductivity"])
                self.notes_file = open(notes_fname, "a", buffering=1)
            except Exception as exc:
                self.console_append(f"Failed to open log files: {exc}")
                self.log_btn.setChecked(False)
                return
            self.time_buf.clear()
            self.data_buf.clear()
            self.logging_enabled = True
            self.log_btn.setText("Stop Logging")
            self.add_note_btn.setEnabled(True)
            self._set_status(f"Logging -> {self.base_filename}.csv", "green")
            self.console_append(f"Logging to {data_fname}")
        else:
            self.stop_logging_if_needed(send_stop_command=True)

    def stop_logging_if_needed(self, send_stop_command: bool) -> None:
        if not self.logging_enabled:
            return
        self.logging_enabled = False
        self.log_btn.setText("Start Logging")
        self.add_note_btn.setEnabled(False)
        self._set_status("Connected (idle)", "#FFB300")
        try:
            if self.log_file:
                self.log_file.flush()
                self.log_file.close()
        except Exception:
            pass
        try:
            if self.notes_file:
                self.notes_file.flush()
                self.notes_file.close()
        except Exception:
            pass
        self.log_file = None
        self.log_writer = None
        self.notes_file = None
        self.console_append("Stopped logging.")

    # ---------- Handlers ----------
    def on_new_sample(self, ts_epoch: float, value: float) -> None:
        self.time_buf.append(ts_epoch)
        self.data_buf.append(value)
        if self.logging_enabled and self.log_writer:
            iso = datetime.fromtimestamp(ts_epoch).isoformat(timespec="milliseconds")
            self.log_writer.writerow([iso, f"{ts_epoch:.6f}", f"{value:.8f}"])

    def on_serial_error(self, msg: str) -> None:
        self.console_append(f"[Serial error] {msg}")

    def on_reader_stopped(self) -> None:
        self.stop_logging_if_needed(send_stop_command=False)
        self.connect_btn.setChecked(False)
        self.connect_btn.setText("Connect")
        self._set_status("Disconnected", "red")

    def on_duration_changed(self, val: int) -> None:
        self.plot_seconds = val

    def add_note(self) -> None:
        note = self.notes_edit.text().strip()
        if not note:
            return
        if not self.notes_file:
            self.console_append("No notes file open (are you logging?).")
            return
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.notes_file.write(f"{ts} | {self.base_filename}.csv | {note}\n")
        self.console_append(f"[NOTE] {note}")
        self.notes_edit.clear()

    # ---------- Plotting ----------
    def update_plot(self) -> None:
        if not self.time_buf:
            return
        now = self.time_buf[-1]
        t0 = now - self.plot_seconds
        xs = []
        ys = []
        for t, y in zip(self.time_buf, self.data_buf):
            if t >= t0:
                xs.append(t - now)
                ys.append(y)
        if xs:
            self.plot_data_item.setData(xs, ys)
            self.plot_widget.setXRange(-self.plot_seconds, 0.0, padding=0.0)

    # ---------- Utils ----------
    def console_append(self, text: str) -> None:
        self.console.appendPlainText(text)

    def _set_status(self, text: str, color: str) -> None:
        self.status_lbl.setText(text)
        self.status_lbl.setStyleSheet(f"color: {color}; font-weight: bold;")
