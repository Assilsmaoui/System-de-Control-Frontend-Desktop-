from PySide6.QtWidgets import QApplication, QMainWindow
from views.login_view import LoginViewQt
from views.main_window import MainWindowQt
import sys

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connexion utilisateur")
        self.resize(400, 300)
        self.login_view = LoginViewQt(on_success=self.handle_login_success)
        self.setCentralWidget(self.login_view)

    def handle_login_success(self, result):
        self.main_window = MainWindowQt()
        self.main_window.token = result.get('token')
        self.main_window.username = result.get('username')
        self.main_window.handle_login_success(result)
        self.main_window.show()
        self.close()

def run_app():
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())
