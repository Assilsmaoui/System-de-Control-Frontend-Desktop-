# Vue Qt pour afficher la liste des étudiants
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton
from services.student_service import get_students

class StudentsViewQt(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("Liste des étudiants")
        label.setStyleSheet("font-size: 16px; margin-bottom: 10px;")
        layout.addWidget(label)
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        refresh_btn = QPushButton("Rafraîchir")
        refresh_btn.clicked.connect(self.load_students)
        layout.addWidget(refresh_btn)
        self.load_students()

    def load_students(self):
        self.list_widget.clear()
        students = get_students()
        for s in students:
            self.list_widget.addItem(s)
