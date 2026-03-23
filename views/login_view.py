from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox, QFrame, QSizePolicy, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor
from services.auth_service import login_user

class LoginViewQt(QWidget):
    def __init__(self, on_success=None, set_user_callback=None):
        super().__init__()
        self.on_success = on_success
        self.set_user_callback = set_user_callback
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Espace Connexion")
        self.setMinimumSize(400, 550)
        
        # QSS : Palette de dégradés de Gris
        self.setStyleSheet("""
            QWidget {
                background-color: #F3F4F6;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
            QFrame#LoginCard {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 20px;
            }
            QLabel#Title {
                font-size: 22px;
                font-weight: 800;
                color: #1F2937;
                margin-bottom: 2px;
            }
            QLabel#Subtitle {
                font-size: 13px;
                color: #9CA3AF;
                margin-bottom: 15px;
            }
            QLineEdit {
                padding: 14px;
                border: 1px solid #D1D5DB;
                border-radius: 10px;
                background-color: #F9FAFB;
                color: #374151;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #6B7280;
                background-color: #FFFFFF;
            }
            QPushButton#LoginBtn {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4B5563, stop:1 #1F2937);
                color: #FFFFFF;
                font-size: 14px;
                font-weight: bold;
                border-radius: 10px;
                padding: 14px;
                margin-top: 10px;
            }
            QPushButton#LoginBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6B7280, stop:1 #374151);
            }
            QPushButton#LoginBtn:pressed {
                background: #111827;
            }
            QLabel#ErrorLabel {
                color: #4B5563; /* Gris foncé pour rester dans le thème même pour l'erreur */
                font-size: 12px;
                font-style: italic;
            }
        """)

        main_layout = QVBoxLayout(self)
        
        # Conteneur de la carte
        self.card = QFrame()
        self.card.setObjectName("LoginCard")
        self.card.setFixedWidth(360)
        
        # Ajout d'une ombre portée (Effet de profondeur Web)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(35, 45, 35, 45)
        card_layout.setSpacing(18)

        # Labels
        # Labels modifiés pour plus de polyvalence
        self.title_label = QLabel("Bienvenue") 
        self.title_label.setObjectName("Title")
        self.title_label.setAlignment(Qt.AlignCenter)

        self.subtitle_label = QLabel("Connectez-vous pour accéder à votre espace")
        self.subtitle_label.setObjectName("Subtitle")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        # Inputs
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nom d'utilisateur")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)

        # Error handling
        self.error_label = QLabel("")
        self.error_label.setObjectName("ErrorLabel")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.hide()

        # Action
        self.login_btn = QPushButton("Se connecter")
        self.login_btn.setObjectName("LoginBtn")
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.clicked.connect(self.handle_login)

        # Montage
        card_layout.addWidget(self.title_label)
        card_layout.addWidget(self.subtitle_label)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.username_input)
        card_layout.addWidget(self.password_input)
        card_layout.addWidget(self.error_label)
        card_layout.addWidget(self.login_btn)

        main_layout.addStretch(1)
        main_layout.addWidget(self.card, alignment=Qt.AlignCenter)
        main_layout.addStretch(1)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            self.show_error("Champs requis")
            return

        result = login_user(username, password)

        if isinstance(result, dict) and not result.get('error'):
            if self.set_user_callback:
                self.set_user_callback(result.get('username'))
            if self.on_success:
                self.on_success(result)
        else:
            error_msg = result if isinstance(result, str) else result.get('error', "Erreur d'accès")
            self.show_error(error_msg)

    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()