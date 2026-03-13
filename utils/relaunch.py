from views.app_entry import LoginWindow
from PySide6.QtWidgets import QApplication

def relaunch_app():
    # Ferme la fenêtre principale et ouvre la page login sans recréer QApplication
    login_window = LoginWindow()
    login_window.show()
