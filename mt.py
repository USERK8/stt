import json
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QLineEdit, QMessageBox, QDialog, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

TEACH_FILE = "teach_dat.json"
CLASS_FILE = "classes.json"
MSC_FILE = "msc.json"


# ------------------- Load / Save -------------------
def load_teachers():
    if not os.path.exists(TEACH_FILE):
        return []
    with open(TEACH_FILE, "r") as f:
        return json.load(f)


def save_teachers(data):
    with open(TEACH_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_classes():
    if not os.path.exists(CLASS_FILE):
        return []
    with open(CLASS_FILE, "r") as f:
        return json.load(f)


def load_msc():
    if not os.path.exists(MSC_FILE):
        return []
    with open(MSC_FILE, "r") as f:
        return json.load(f)


def save_msc(data):
    with open(MSC_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ------------------- Edit Teacher Dialog -------------------
class EditTeacherDialog(QDialog):
    def __init__(self, teacher_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Teacher")
        self.setFixedSize(400, 220)

        self.teacher_data = teacher_data
        self.result_data = None

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Teacher Name:"))
        self.name_input = QLineEdit()
        self.name_input.setText(teacher_data["name"])
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Subject:"))
        self.subject_input = QLineEdit()
        self.subject_input.setText(teacher_data["subject"])
        layout.addWidget(self.subject_input)

        btn_layout = QHBoxLayout()
        done_btn = QPushButton("Done")
        done_btn.clicked.connect(self.accept_edit)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(done_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.name_input.returnPressed.connect(self.accept_edit)
        self.subject_input.returnPressed.connect(self.accept_edit)

    def accept_edit(self):
        name = self.name_input.text().strip()
        subject = self.subject_input.text().strip()

        if not name or not subject:
            return

        self.result_data = {"name": name, "subject": subject}
        self.accept()


# ------------------- Manage Teachers Page -------------------
class ManageTeachers(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.teachers = load_teachers()
        self.init_ui()
        self.refresh_list()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setSpacing(25)
        self.layout.setContentsMargins(80, 60, 80, 60)

        # Back Button
        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(self.go_back)
        self.layout.addWidget(self.back_btn)

        # Title
        self.title = QLabel("Manage Teachers")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title)

        # Name Input
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Teacher Name")
        self.layout.addWidget(self.name_input)

        # Subject Input
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Subject")
        self.layout.addWidget(self.subject_input)

        self.name_input.returnPressed.connect(self.add_teacher)
        self.subject_input.returnPressed.connect(self.add_teacher)

        # Buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add")
        self.edit_btn = QPushButton("Edit")
        self.delete_btn = QPushButton("Delete")
        self.schedule_btn = QPushButton("Manage Teacher's Schedule")

        self.add_btn.clicked.connect(self.add_teacher)
        self.edit_btn.clicked.connect(self.edit_teacher)
        self.delete_btn.clicked.connect(self.delete_teacher)
        self.schedule_btn.clicked.connect(self.manage_schedule)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        self.layout.addLayout(btn_layout)

        self.layout.addWidget(self.schedule_btn)

        # List
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

        self.setLayout(self.layout)

    # ------------------- Navigation -------------------
    def go_back(self):
        if self.parent_window:
            self.parent_window.go_home()

    # ------------------- Core -------------------
    def refresh_list(self):
        self.list_widget.clear()
        for teacher in self.teachers:
            self.list_widget.addItem(f"{teacher['name']} — {teacher['subject']}")

    def add_teacher(self):
        name = self.name_input.text().strip()
        subject = self.subject_input.text().strip()
        if not name or not subject:
            return
        for t in self.teachers:
            if t["name"] == name:
                QMessageBox.warning(self, "Warning", "Teacher already exists!")
                return
        self.teachers.append({"name": name, "subject": subject})
        save_teachers(self.teachers)
        self.refresh_list()
        self.name_input.clear()
        self.subject_input.clear()

    def delete_teacher(self):
        row = self.list_widget.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warning", "Select a teacher first!")
            return
        del self.teachers[row]
        save_teachers(self.teachers)
        self.refresh_list()

    def edit_teacher(self):
        row = self.list_widget.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warning", "Select a teacher first!")
            return
        dialog = EditTeacherDialog(self.teachers[row], self)
        if dialog.exec():
            self.teachers[row] = dialog.result_data
            save_teachers(self.teachers)
            self.refresh_list()

    # ------------------- Schedule -------------------
    def manage_schedule(self):
        row = self.list_widget.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warning", "Select a teacher first!")
            return

        teacher = self.teachers[row]
        teacher_name = teacher["name"]
        subject = teacher["subject"]

        # Local import to avoid circular import
        from mts import ManageTeacherSchedule

        self._schedule_window = ManageTeacherSchedule(
            parent=self, teacher_name=teacher_name, subject=subject
        )
        self._schedule_window.show()
        self._schedule_window.raise_()
