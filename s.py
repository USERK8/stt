# s.py

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class SettingsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.buttons = []
        self.init_ui()
        self.apply_style()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_help = QPushButton("Help")
        self.btn_help.clicked.connect(self.show_help)

        self.btn_about = QPushButton("About Us")
        self.btn_about.clicked.connect(self.show_about)

        self.btn_version = QPushButton("Version")
        self.btn_version.clicked.connect(self.show_version)

        self.btn_back = QPushButton("Back")
        self.btn_back.clicked.connect(self.main_window.go_home)

        self.buttons.extend([
            self.btn_help,
            self.btn_about,
            self.btn_version,
            self.btn_back
        ])

        for btn in self.buttons:
            self.layout.addWidget(btn)

        self.setLayout(self.layout)

    def apply_style(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
            }
        """)

    # This runs whenever page becomes visible
    def showEvent(self, event):
        self.dynamic_scaling()
        super().showEvent(event)

    # Also update when resized
    def resizeEvent(self, event):
        self.dynamic_scaling()
        super().resizeEvent(event)

    def dynamic_scaling(self):
        if not self.main_window:
            return

        width = self.main_window.width()

        font_size = max(16, width // 60)
        padding = max(14, width // 90)
        spacing = max(25, width // 50)

        self.layout.setSpacing(spacing)

        for btn in self.buttons:
            btn.setFont(QFont("Arial", font_size))
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
                    border-radius: 18px;
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

    def show_help(self):
        QMessageBox.information(
            self,
            "Help",
            "Facing trouble?\n\nContact us:\nPhone: 9409503970\nEmail: polisohankumarreddy@gmail.com"
        )

    def show_about(self):
        QMessageBox.information(
            self,
            "About Us",
            "Developed by - P. Sohan Kumar Reddy\nClass 11A\nBatch 2025-26"
        )

    def show_version(self):
        try:
            with open("version.txt", "r") as file:
                version = file.read().strip()
        except FileNotFoundError:
            version = "Version file not found."

        QMessageBox.information(
            self,
            "Version",
            f"Current Version: {version}"
        )
