# pet.py

import threading
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel,
    QFrame, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QMetaObject, Q_ARG, pyqtSlot
from PyQt6.QtGui import QFont

from get import generate_timetable_async
from tw import generate_teacherwise_pdf

def generate_daywise_pdf():
    return "Day-wise PDF generator is still under development."


class PDFExporterPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self._generating   = False

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.setSpacing(30)
        self.main_layout.setContentsMargins(60, 40, 60, 40)

        # Title
        self.title = QLabel("PDF Exporter")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.title)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #a0a0a0; font-size: 16px;")
        self.main_layout.addWidget(self.status_label)

        # Progress bar — hidden until generation starts
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 120)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(18)
        self.progress_bar.hide()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 9px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff4ecd, stop:1 #a855f7
                );
                border-radius: 9px;
            }
        """)
        self.main_layout.addWidget(self.progress_bar)

        # Button container
        self.button_box = QFrame()
        self.box_layout = QVBoxLayout()
        self.box_layout.setSpacing(25)

        self.buttons = []

        self.btn_classwise   = QPushButton("Generate Class-wise PDF")
        self.btn_teacherwise = QPushButton("Generate Teacher-wise PDF")
        self.btn_daywise     = QPushButton("Generate Day-wise PDF")
        self.btn_back        = QPushButton("Back to Home")

        self.btn_classwise.clicked.connect(self.run_classwise_pdf)
        self.btn_teacherwise.clicked.connect(self.run_teacherwise_pdf)
        self.btn_daywise.clicked.connect(self.run_daywise_pdf)
        self.btn_back.clicked.connect(self.go_back)

        self.buttons.extend([
            self.btn_classwise,
            self.btn_teacherwise,
            self.btn_daywise,
            self.btn_back
        ])

        for btn in self.buttons:
            self.box_layout.addWidget(btn)

        self.button_box.setLayout(self.box_layout)
        self.main_layout.addWidget(self.button_box)
        self.setLayout(self.main_layout)

        self.apply_base_style()
        self.dynamic_scaling()

    # ---------------- Styles ----------------
    def apply_base_style(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
            }
            QFrame {
                background-color: #1c1c1c;
                border: 3px solid #2a2a2a;
                border-radius: 20px;
            }
            QPushButton {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f3d2e, stop:1 #1b2a4a
                );
                color: white;
                border: 2px solid #2f2f2f;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #145c43, stop:1 #243b6b
                );
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #555555;
                border: 2px solid #1a1a1a;
            }
        """)

    # ---------------- Dynamic scaling ----------------
    def dynamic_scaling(self):
        if not hasattr(self, "title"):
            return

        width = self.width()

        title_size = max(40, width // 20)
        self.title.setFont(QFont("Arial", title_size, QFont.Weight.Bold))
        self.title.setStyleSheet("""
            QLabel {
                color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff4ecd, stop:1 #a855f7
                );
                margin-bottom: 50px;
            }
        """)

        button_font_size = max(18, width // 60)
        padding          = max(15, width // 120)

        for btn in self.buttons:
            btn.setFont(QFont("Arial", button_font_size))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 #0f3d2e, stop:1 #1b2a4a
                    );
                    color: white;
                    border: 2px solid #2f2f2f;
                    border-radius: 20px;
                    padding: {padding}px;
                }}
                QPushButton:hover {{
                    background-color: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 #145c43, stop:1 #243b6b
                    );
                }}
                QPushButton:disabled {{
                    background-color: #2a2a2a;
                    color: #555555;
                    border: 2px solid #1a1a1a;
                }}
            """)

    def resizeEvent(self, event):
        self.dynamic_scaling()
        super().resizeEvent(event)

    # ---------------- Busy helpers ----------------
    def _set_busy(self, status_text, total=120):
        self._generating = True
        self.status_label.setText(status_text)
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        for btn in self.buttons:
            btn.setEnabled(False)

    def _set_idle(self):
        self._generating = False
        self.status_label.setText("")
        self.progress_bar.hide()
        self.progress_bar.setValue(0)
        for btn in self.buttons:
            btn.setEnabled(True)
        self.dynamic_scaling()

    # ---------------- Qt slots (always called on main thread) ----------------
    @pyqtSlot(int, int, int)
    def _on_progress(self, attempt, total, best_empty):
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(attempt)
        self.status_label.setText(
            f"Attempt {attempt} / {total}  —  best empty slots so far: {best_empty}"
        )

    @pyqtSlot(str)
    def _on_generation_done(self, message):
        self._set_idle()
        QMessageBox.information(self, "Done", message)

    @pyqtSlot(str)
    def _on_generation_error(self, error_text):
        self._set_idle()
        QMessageBox.critical(self, "Error", error_text)

    # ---------------- Button actions ----------------
    def run_classwise_pdf(self):
        if self._generating:
            return

        from get import MAX_ATTEMPTS
        self._set_busy("Generating class-wise timetable… please wait.", total=MAX_ATTEMPTS)

        def on_progress(attempt, total, best_empty):
            QMetaObject.invokeMethod(
                self, "_on_progress",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(int, attempt),
                Q_ARG(int, total),
                Q_ARG(int, best_empty),
            )

        def on_done(msg):
            QMetaObject.invokeMethod(
                self, "_on_generation_done",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(str, str(msg))
            )

        def on_error(err):
            QMetaObject.invokeMethod(
                self, "_on_generation_error",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(str, f"Error generating class-wise PDF:\n{err}")
            )

        generate_timetable_async(
            on_progress=on_progress,
            on_done=on_done,
            on_error=on_error
        )

    def run_teacherwise_pdf(self):
        if self._generating:
            return

        self._set_busy("Generating teacher-wise timetable… please wait.", total=0)
        # total=0 → indeterminate progress bar (pulse effect not in Qt natively,
        # but setting range 0,0 shows a "busy" bar on most platforms)
        self.progress_bar.setRange(0, 0)

        def _worker():
            try:
                msg = generate_teacherwise_pdf()
                QMetaObject.invokeMethod(
                    self, "_on_generation_done",
                    Qt.ConnectionType.QueuedConnection,
                    Q_ARG(str, str(msg))
                )
            except Exception as exc:
                QMetaObject.invokeMethod(
                    self, "_on_generation_error",
                    Qt.ConnectionType.QueuedConnection,
                    Q_ARG(str, f"Error generating teacher-wise PDF:\n{exc}")
                )

        threading.Thread(target=_worker, daemon=True).start()

    def run_daywise_pdf(self):
        try:
            msg = generate_daywise_pdf()
            QMessageBox.information(self, "Info", msg)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating day-wise PDF:\n{e}")

    def go_back(self):
        if self._generating:
            QMessageBox.warning(
                self, "Busy",
                "Please wait for the current generation to finish before going back."
            )
            return
        if self.parent_window:
            self.parent_window.go_home()