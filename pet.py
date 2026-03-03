# pet.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# ---------------- Import your existing PDF generators ----------------
from get import generate_timetable_pdfs
from tw import generate_teacherwise_pdf
# dw.py is under development
def generate_daywise_pdf():
    return "Day-wise PDF generator is still under development."

# ---------------- Main PDF Exporter Page ----------------
class PDFExporterPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent

        self.setWindowTitle("PDF Exporter")
        self.showMaximized()

        # Main layout
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.setSpacing(30)
        self.layout.setContentsMargins(60, 40, 60, 40)

        # Title
        self.title = QLabel("PDF Exporter")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title)

        # Button container
        self.button_box = QFrame()
        self.box_layout = QVBoxLayout()
        self.box_layout.setSpacing(25)

        # Buttons
        self.buttons = []

        self.btn_classwise = QPushButton("Generate Class-wise PDF")
        self.btn_teacherwise = QPushButton("Generate Teacher-wise PDF")
        self.btn_daywise = QPushButton("Generate Day-wise PDF")
        self.btn_back = QPushButton("Back to Home")

        # Connect buttons
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
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)

        self.apply_base_style()
        self.dynamic_scaling()  # Initial scaling

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
                    x1:0, y1:0,
                    x2:1, y2:1,
                    stop:0 #0f3d2e,
                    stop:1 #1b2a4a
                );
                color: white;
                border: 2px solid #2f2f2f;
                border-radius: 15px;
            }

            QPushButton:hover {
                background-color: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:1,
                    stop:0 #145c43,
                    stop:1 #243b6b
                );
            }
        """)

    # ---------------- Dynamic scaling ----------------
    def dynamic_scaling(self):
        if not hasattr(self, "title"):
            return  # Prevent crash if called before title exists

        width = self.width()
        height = self.height()

        # Title scaling
        title_size = max(40, width // 20)
        self.title.setFont(QFont("Arial", title_size, QFont.Weight.Bold))
        self.title.setStyleSheet("""
            QLabel {
                color: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 #ff4ecd,
                    stop:1 #a855f7
                );
                margin-bottom: 50px;
            }
        """)

        # Button scaling
        button_font_size = max(18, width // 60)
        padding = max(15, width // 120)

        for btn in self.buttons:
            btn.setFont(QFont("Arial", button_font_size))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: qlineargradient(
                        x1:0, y1:0,
                        x2:1, y2:1,
                        stop:0 #0f3d2e,
                        stop:1 #1b2a4a
                    );
                    color: white;
                    border: 2px solid #2f2f2f;
                    border-radius: 20px;
                    padding: {padding}px;
                }}

                QPushButton:hover {{
                    background-color: qlineargradient(
                        x1:0, y1:0,
                        x2:1, y2:1,
                        stop:0 #145c43,
                        stop:1 #243b6b
                    );
                }}
            """)

    def resizeEvent(self, event):
        self.dynamic_scaling()
        super().resizeEvent(event)

    # ---------------- Button Actions ----------------
    def run_classwise_pdf(self):
        try:
            msg = generate_timetable_pdfs()
            QMessageBox.information(self, "Done", msg)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating class-wise PDF:\n{e}")

    def run_teacherwise_pdf(self):
        try:
            msg = generate_teacherwise_pdf()
            QMessageBox.information(self, "Done", msg)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating teacher-wise PDF:\n{e}")

    def run_daywise_pdf(self):
        try:
            msg = generate_daywise_pdf()
            QMessageBox.information(self, "Info", msg)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating day-wise PDF:\n{e}")

    def go_back(self):
        if self.parent_window:
            self.close()
            self.parent_window.go_home()
