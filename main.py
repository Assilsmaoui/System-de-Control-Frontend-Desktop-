import sys
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        import platform
        system = platform.system()
        self.setWindowTitle("PySide6 Demo")
        label = QLabel(f"Bienvenue sur PySide6 !\nSystème utilisé : {system}")
        self.setCentralWidget(label)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
