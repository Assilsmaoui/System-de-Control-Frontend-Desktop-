# Vue Qt pour le login utilisateur
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

from services.auth_service import login_user
import threading
import sys
import os



class LoginViewQt(QWidget):
    def __init__(self, on_success=None, set_user_callback=None):
        super().__init__()
        self.on_success = on_success
        self.set_user_callback = set_user_callback
        # Centrage vertical et horizontal du bloc de login
        from PySide6.QtWidgets import QFrame, QSizePolicy
        from PySide6.QtCore import Qt
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        bloc = QFrame()
        bloc.setStyleSheet("""
            background: #fff;
            border-radius: 16px;
            padding: 32px 32px 24px 32px;
            min-width: 320px;
            max-width: 350px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.08);
        """)
        bloc.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        form_layout = QVBoxLayout(bloc)
        form_layout.setAlignment(Qt.AlignCenter)
        self.label = QLabel("Connexion utilisateur")
        self.label.setProperty('role', 'title')
        self.label.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(self.label)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nom d'utilisateur")
        form_layout.addWidget(self.username_input)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self.password_input)
        self.login_btn = QPushButton("Se connecter")
        self.login_btn.setStyleSheet("background: #e0e0e0; color: #222; border-radius: 8px; padding: 8px 20px; font-size: 15px; margin: 8px;")
        self.login_btn.clicked.connect(self.handle_login)
        form_layout.addWidget(self.login_btn)
        main_layout.addStretch(1)
        main_layout.addWidget(bloc, alignment=Qt.AlignCenter)
        main_layout.addStretch(1)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        result = login_user(username, password)
        if isinstance(result, dict) and not result.get('error'):
            # Transmettre tout le résultat à la fenêtre principale
            if self.set_user_callback:
                self.set_user_callback(result.get('username'))
            if self.on_success:
                self.on_success(result)
        else:
            # Affiche la réponse brute pour aider au debug
            import pprint
            print("Réponse backend:")
            pprint.pprint(result)
            message = result if isinstance(result, str) else result.get('error', f"Erreur inconnue: {result}")
            QMessageBox.information(self, "Résultat", message)
